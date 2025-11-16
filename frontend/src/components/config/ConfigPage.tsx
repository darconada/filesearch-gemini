/**
 * Configuration page component
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
  Chip,
} from '@mui/material';
import { CheckCircle, Error as ErrorIcon } from '@mui/icons-material';
import { configApi } from '@/services/api';
import type { ConfigStatus } from '@/types';

const ConfigPage: React.FC = () => {
  const [apiKey, setApiKey] = useState('');
  const [status, setStatus] = useState<ConfigStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const statusData = await configApi.getStatus();
      setStatus(statusData);
    } catch (error) {
      console.error('Error loading config status:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) {
      setMessage({ type: 'error', text: 'Please enter an API key' });
      return;
    }

    setSaving(true);
    setMessage(null);

    try {
      await configApi.setApiKey(apiKey);
      setMessage({ type: 'success', text: 'API key configured successfully' });
      setApiKey('');
      await loadStatus();
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Error configuring API key',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Configuration
      </Typography>

      {/* Status Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Connection Status
          </Typography>
          <Box display="flex" gap={2} alignItems="center" mb={2}>
            <Typography variant="body2" color="text.secondary">
              Configured:
            </Typography>
            {status?.configured ? (
              <Chip icon={<CheckCircle />} label="Yes" color="success" size="small" />
            ) : (
              <Chip icon={<ErrorIcon />} label="No" color="error" size="small" />
            )}
          </Box>
          <Box display="flex" gap={2} alignItems="center" mb={2}>
            <Typography variant="body2" color="text.secondary">
              API Key Valid:
            </Typography>
            {status?.api_key_valid ? (
              <Chip icon={<CheckCircle />} label="Valid" color="success" size="small" />
            ) : (
              <Chip icon={<ErrorIcon />} label="Invalid" color="error" size="small" />
            )}
          </Box>
          {status?.model_available && (
            <Box display="flex" gap={2} alignItems="center">
              <Typography variant="body2" color="text.secondary">
                Model:
              </Typography>
              <Typography variant="body2">{status.model_available}</Typography>
            </Box>
          )}
          {status?.error_message && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {status.error_message}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* API Key Input Card */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Google API Key
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Enter your Google Generative Language API key. You can obtain one from the{' '}
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
            >
              Google AI Studio
            </a>
            .
          </Typography>

          <TextField
            fullWidth
            type="password"
            label="API Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your Google API key"
            sx={{ mb: 2 }}
            disabled={saving}
          />

          {message && (
            <Alert severity={message.type} sx={{ mb: 2 }}>
              {message.text}
            </Alert>
          )}

          <Button
            variant="contained"
            onClick={handleSaveApiKey}
            disabled={saving || !apiKey.trim()}
          >
            {saving ? <CircularProgress size={24} /> : 'Save API Key'}
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ConfigPage;
