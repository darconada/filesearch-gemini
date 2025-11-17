/**
 * CLI configuration component
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { cliApi } from '@/services/api';
import type { CLIConfig as CLIConfigType, CLIStatus } from '@/types';

export default function CLIConfig() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [config, setConfig] = useState<CLIConfigType | null>(null);
  const [status, setStatus] = useState<CLIStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [copiedStates, setCopiedStates] = useState<Record<number, boolean>>({});

  // Form state
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000');
  const [defaultStoreId, setDefaultStoreId] = useState('');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      const [configData, statusData] = await Promise.all([
        cliApi.getConfig(),
        cliApi.getStatus(),
      ]);
      setConfig(configData);
      setStatus(statusData);
      setBackendUrl(configData.backend_url);
      setDefaultStoreId(configData.default_store_id || '');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading CLI configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);
      const updated = await cliApi.updateConfig({
        backend_url: backendUrl,
        default_store_id: defaultStoreId || undefined,
      });
      setConfig(updated);
      setSuccess('CLI configuration saved successfully!');
      // Reload status to get updated examples
      const statusData = await cliApi.getStatus();
      setStatus(statusData);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error saving configuration');
    } finally {
      setSaving(false);
    }
  };

  const handleCopy = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedStates({ ...copiedStates, [index]: true });
    setTimeout(() => {
      setCopiedStates({ ...copiedStates, [index]: false });
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
            CLI Local Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Configure the filesearch-gemini command-line tool
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

            <TextField
              fullWidth
              label="Default Store ID (optional)"
              value={defaultStoreId}
              onChange={(e) => setDefaultStoreId(e.target.value)}
              helperText="Default store to use when not specified (e.g., fileSearchStores/abc123)"
              sx={{ mb: 2 }}
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
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                CLI Information
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Executable Path:</strong>
              </Typography>
              <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 2 }}>
                {status.executable_path}
              </Typography>

              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Make the CLI executable: <code>chmod +x {status.executable_path}</code>
                </Typography>
              </Alert>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Example Commands
              </Typography>
              <List>
                {status.example_commands.map((cmd, index) => (
                  <ListItem
                    key={index}
                    secondaryAction={
                      <Tooltip title={copiedStates[index] ? 'Copied!' : 'Copy to clipboard'}>
                        <IconButton
                          edge="end"
                          onClick={() => handleCopy(cmd, index)}
                        >
                          {copiedStates[index] ? <CheckIcon /> : <CopyIcon />}
                        </IconButton>
                      </Tooltip>
                    }
                  >
                    <ListItemText
                      primary={
                        <Typography
                          variant="body2"
                          sx={{
                            fontFamily: 'monospace',
                            backgroundColor: '#f5f5f5',
                            padding: '8px',
                            borderRadius: '4px',
                          }}
                        >
                          {cmd}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </>
      )}

      <Alert severity="info" sx={{ mt: 3 }}>
        <Typography variant="body2">
          <strong>Configuration file:</strong> The CLI reads from{' '}
          <code>~/.filesearch-gemini/config.yaml</code>. You can also use environment variables.
        </Typography>
      </Alert>
    </Box>
  );
}
