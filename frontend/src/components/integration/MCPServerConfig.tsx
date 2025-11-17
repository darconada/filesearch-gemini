/**
 * MCP Server configuration component
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { mcpApi } from '@/services/api';
import type { MCPConfig, MCPStatus } from '@/types';

export default function MCPServerConfig() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<MCPConfig | null>(null);
  const [status, setStatus] = useState<MCPStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});

  // Form state
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000');
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const [configData, statusData] = await Promise.all([
        mcpApi.getConfig(),
        mcpApi.getStatus(),
      ]);
      setConfig(configData);
      setStatus(statusData);
      setBackendUrl(configData.backend_url);
      setEnabled(configData.enabled);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading MCP configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      const updated = await mcpApi.updateConfig({
        backend_url: backendUrl,
        enabled,
      });
      setConfig(updated);
      setSuccess('MCP Server configuration saved successfully!');
      // Reload status to get updated examples
      const statusData = await mcpApi.getStatus();
      setStatus(statusData);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error saving configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStates({ ...copiedStates, [key]: true });
    setTimeout(() => {
      setCopiedStates({ ...copiedStates, [key]: false });
    }, 2000);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            MCP Server Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Configure the Model Context Protocol server for LLM agent integration
          </Typography>

          <Box sx={{ mt: 3 }}>
            <TextField
              fullWidth
              label="Backend URL"
              value={backendUrl}
              onChange={(e) => setBackendUrl(e.target.value)}
              helperText="URL where the FastAPI backend is running"
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={enabled}
                  onChange={(e) => setEnabled(e.target.checked)}
                />
              }
              label="Enable MCP Server"
            />

            <Box sx={{ mt: 3 }}>
              <Button
                variant="contained"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {status && (
        <>
          <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>
            Agent Configuration Examples
          </Typography>

          {/* Gemini CLI */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Gemini CLI</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {status.example_commands.gemini_cli.description}
              </Typography>
              <Box sx={{ position: 'relative' }}>
                <pre style={{
                  backgroundColor: '#f5f5f5',
                  padding: '16px',
                  borderRadius: '4px',
                  overflow: 'auto',
                  fontSize: '12px',
                }}>
                  {JSON.stringify(status.example_commands.gemini_cli.config, null, 2)}
                </pre>
                <Tooltip title={copiedStates['gemini'] ? 'Copied!' : 'Copy to clipboard'}>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(JSON.stringify(status.example_commands.gemini_cli.config, null, 2), 'gemini')}
                    sx={{ position: 'absolute', top: 8, right: 8 }}
                  >
                    {copiedStates['gemini'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
                  </IconButton>
                </Tooltip>
              </Box>
            </AccordionDetails>
          </Accordion>

          {/* Claude Code */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Claude Code</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {status.example_commands.claude_code.description}
              </Typography>
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Command:
              </Typography>
              <Box sx={{ position: 'relative', mb: 2 }}>
                <pre style={{
                  backgroundColor: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  overflow: 'auto',
                  fontSize: '12px',
                }}>
                  {status.example_commands.claude_code.command}
                </pre>
                <Tooltip title={copiedStates['claude-cmd'] ? 'Copied!' : 'Copy to clipboard'}>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(status.example_commands.claude_code.command, 'claude-cmd')}
                    sx={{ position: 'absolute', top: 4, right: 4 }}
                  >
                    {copiedStates['claude-cmd'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography variant="subtitle2" gutterBottom>
                Config:
              </Typography>
              <Box sx={{ position: 'relative' }}>
                <pre style={{
                  backgroundColor: '#f5f5f5',
                  padding: '16px',
                  borderRadius: '4px',
                  overflow: 'auto',
                  fontSize: '12px',
                }}>
                  {JSON.stringify(status.example_commands.claude_code.config, null, 2)}
                </pre>
                <Tooltip title={copiedStates['claude'] ? 'Copied!' : 'Copy to clipboard'}>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(JSON.stringify(status.example_commands.claude_code.config, null, 2), 'claude')}
                    sx={{ position: 'absolute', top: 8, right: 8 }}
                  >
                    {copiedStates['claude'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
                  </IconButton>
                </Tooltip>
              </Box>
            </AccordionDetails>
          </Accordion>

          {/* Codex CLI */}
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Codex CLI</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {status.example_commands.codex_cli.description}
              </Typography>
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Command:
              </Typography>
              <Box sx={{ position: 'relative', mb: 2 }}>
                <pre style={{
                  backgroundColor: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  overflow: 'auto',
                  fontSize: '12px',
                }}>
                  {status.example_commands.codex_cli.command}
                </pre>
                <Tooltip title={copiedStates['codex-cmd'] ? 'Copied!' : 'Copy to clipboard'}>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(status.example_commands.codex_cli.command, 'codex-cmd')}
                    sx={{ position: 'absolute', top: 4, right: 4 }}
                  >
                    {copiedStates['codex-cmd'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
                  </IconButton>
                </Tooltip>
              </Box>
              <Typography variant="subtitle2" gutterBottom>
                Config:
              </Typography>
              <Box sx={{ position: 'relative' }}>
                <pre style={{
                  backgroundColor: '#f5f5f5',
                  padding: '16px',
                  borderRadius: '4px',
                  overflow: 'auto',
                  fontSize: '12px',
                }}>
                  {JSON.stringify(status.example_commands.codex_cli.config, null, 2)}
                </pre>
                <Tooltip title={copiedStates['codex'] ? 'Copied!' : 'Copy to clipboard'}>
                  <IconButton
                    size="small"
                    onClick={() => handleCopy(JSON.stringify(status.example_commands.codex_cli.config, null, 2), 'codex')}
                    sx={{ position: 'absolute', top: 8, right: 8 }}
                  >
                    {copiedStates['codex'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
                  </IconButton>
                </Tooltip>
              </Box>
            </AccordionDetails>
          </Accordion>
        </>
      )}

      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>To start the MCP server:</strong> Run{' '}
          <code>python backend/mcp_server.py</code> from the project root.
        </Typography>
      </Alert>
    </Box>
  );
}
