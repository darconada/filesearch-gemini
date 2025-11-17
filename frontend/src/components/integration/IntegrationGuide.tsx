/**
 * Integration guide component
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  Chip,
  Link,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ContentCopy as CopyIcon,
  Check as CheckIcon,
} from '@mui/icons-material';
import { integrationApi } from '@/services/api';
import type { IntegrationGuide } from '@/types';

export default function IntegrationGuideView() {
  const [loading, setLoading] = useState(true);
  const [guide, setGuide] = useState<IntegrationGuide | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadGuide();
  }, []);

  const loadGuide = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await integrationApi.getGuide();
      setGuide(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading integration guide');
    } finally {
      setLoading(false);
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

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!guide) {
    return null;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Alert severity="info" sx={{ mb: 3 }}>
        Complete integration guide for using File Search with LLM agents. For full documentation,
        see <strong>MCP_INTEGRATION.md</strong> in the repository.
      </Alert>

      {/* Gemini CLI */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">{guide.gemini_cli.title}</Typography>
            <Chip label="MCP" size="small" color="primary" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {guide.gemini_cli.description}
          </Typography>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Setup Steps:
          </Typography>
          <List dense>
            {guide.gemini_cli.steps.map((step, index) => (
              <ListItem key={index}>
                <ListItemText primary={step} />
              </ListItem>
            ))}
          </List>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Configuration:
          </Typography>
          <Box sx={{ position: 'relative' }}>
            <pre style={{
              backgroundColor: '#f5f5f5',
              padding: '16px',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '12px',
            }}>
              {JSON.stringify(guide.gemini_cli.config, null, 2)}
            </pre>
            <Tooltip title={copiedStates['gemini-guide'] ? 'Copied!' : 'Copy to clipboard'}>
              <IconButton
                size="small"
                onClick={() => handleCopy(JSON.stringify(guide.gemini_cli.config, null, 2), 'gemini-guide')}
                sx={{ position: 'absolute', top: 8, right: 8 }}
              >
                {copiedStates['gemini-guide'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>

          <Link href={guide.gemini_cli.documentation} target="_blank" sx={{ mt: 2, display: 'block' }}>
            View full documentation →
          </Link>
        </AccordionDetails>
      </Accordion>

      {/* Claude Code */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">{guide.claude_code.title}</Typography>
            <Chip label="MCP" size="small" color="primary" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {guide.claude_code.description}
          </Typography>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Setup Steps:
          </Typography>
          <List dense>
            {guide.claude_code.steps.map((step, index) => (
              <ListItem key={index}>
                <ListItemText primary={step} />
              </ListItem>
            ))}
          </List>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
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
              {guide.claude_code.command}
            </pre>
            <Tooltip title={copiedStates['claude-cmd-guide'] ? 'Copied!' : 'Copy to clipboard'}>
              <IconButton
                size="small"
                onClick={() => handleCopy(guide.claude_code.command, 'claude-cmd-guide')}
                sx={{ position: 'absolute', top: 4, right: 4 }}
              >
                {copiedStates['claude-cmd-guide'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>

          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Configuration:
          </Typography>
          <Box sx={{ position: 'relative' }}>
            <pre style={{
              backgroundColor: '#f5f5f5',
              padding: '16px',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '12px',
            }}>
              {JSON.stringify(guide.claude_code.config, null, 2)}
            </pre>
            <Tooltip title={copiedStates['claude-guide'] ? 'Copied!' : 'Copy to clipboard'}>
              <IconButton
                size="small"
                onClick={() => handleCopy(JSON.stringify(guide.claude_code.config, null, 2), 'claude-guide')}
                sx={{ position: 'absolute', top: 8, right: 8 }}
              >
                {copiedStates['claude-guide'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>

          <Link href={guide.claude_code.documentation} target="_blank" sx={{ mt: 2, display: 'block' }}>
            View full documentation →
          </Link>
        </AccordionDetails>
      </Accordion>

      {/* Codex CLI */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">{guide.codex_cli.title}</Typography>
            <Chip label="MCP" size="small" color="primary" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {guide.codex_cli.description}
          </Typography>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Setup Steps:
          </Typography>
          <List dense>
            {guide.codex_cli.steps.map((step, index) => (
              <ListItem key={index}>
                <ListItemText primary={step} />
              </ListItem>
            ))}
          </List>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
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
              {guide.codex_cli.command}
            </pre>
            <Tooltip title={copiedStates['codex-cmd-guide'] ? 'Copied!' : 'Copy to clipboard'}>
              <IconButton
                size="small"
                onClick={() => handleCopy(guide.codex_cli.command, 'codex-cmd-guide')}
                sx={{ position: 'absolute', top: 4, right: 4 }}
              >
                {copiedStates['codex-cmd-guide'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>

          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Configuration:
          </Typography>
          <Box sx={{ position: 'relative' }}>
            <pre style={{
              backgroundColor: '#f5f5f5',
              padding: '16px',
              borderRadius: '4px',
              overflow: 'auto',
              fontSize: '12px',
            }}>
              {JSON.stringify(guide.codex_cli.config, null, 2)}
            </pre>
            <Tooltip title={copiedStates['codex-guide'] ? 'Copied!' : 'Copy to clipboard'}>
              <IconButton
                size="small"
                onClick={() => handleCopy(JSON.stringify(guide.codex_cli.config, null, 2), 'codex-guide')}
                sx={{ position: 'absolute', top: 8, right: 8 }}
              >
                {copiedStates['codex-guide'] ? <CheckIcon fontSize="small" /> : <CopyIcon fontSize="small" />}
              </IconButton>
            </Tooltip>
          </Box>

          <Link href={guide.codex_cli.documentation} target="_blank" sx={{ mt: 2, display: 'block' }}>
            View full documentation →
          </Link>
        </AccordionDetails>
      </Accordion>

      {/* CLI Local */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">{guide.cli_local.title}</Typography>
            <Chip label="CLI" size="small" color="secondary" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {guide.cli_local.description}
          </Typography>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Setup Steps:
          </Typography>
          <List dense>
            {guide.cli_local.steps.map((step, index) => (
              <ListItem key={index}>
                <ListItemText primary={step} />
              </ListItem>
            ))}
          </List>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Executable Path:
          </Typography>
          <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 2 }}>
            {guide.cli_local.executable}
          </Typography>

          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Example Commands:
          </Typography>
          <List dense>
            {guide.cli_local.examples.map((example, index) => (
              <ListItem key={index}>
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
                      {example}
                    </Typography>
                  }
                />
                <IconButton
                  edge="end"
                  onClick={() => handleCopy(example, `cli-${index}`)}
                >
                  {copiedStates[`cli-${index}`] ? <CheckIcon /> : <CopyIcon />}
                </IconButton>
              </ListItem>
            ))}
          </List>

          <Link href={guide.cli_local.documentation} target="_blank" sx={{ mt: 2, display: 'block' }}>
            View full documentation →
          </Link>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}
