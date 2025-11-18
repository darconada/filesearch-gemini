/**
 * Google Drive Setup Page - Configure OAuth credentials via web UI
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Tabs,
  Tab,
  Divider,
  List,
  ListItem,
  ListItemText,
  Chip,
  Paper,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  CloudUpload as CloudUploadIcon,
  Edit as EditIcon,
  PlayArrow as PlayArrowIcon,
} from '@mui/icons-material';
import { configApi } from '@/services/api';
import type { DriveCredentialsStatus } from '@/types';

export default function DriveSetupPage() {
  const [status, setStatus] = useState<DriveCredentialsStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Form states
  const [inputMode, setInputMode] = useState<'json' | 'manual'>('manual');
  const [credentialsJSON, setCredentialsJSON] = useState('');
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [projectId, setProjectId] = useState('');

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const data = await configApi.getDriveCredentialsStatus();
      setStatus(data);
    } catch (err: any) {
      console.error('Error loading Drive credentials status:', err);
      setError(err.response?.data?.detail || err.message || 'Error loading status');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveJSON = async () => {
    if (!credentialsJSON.trim()) {
      setError('Please paste the credentials JSON');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      await configApi.setDriveCredentialsJSON(credentialsJSON);
      setSuccess('Credenciales guardadas correctamente. Ahora puedes probar la conexión.');
      setCredentialsJSON('');
      loadStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error saving credentials');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSaveManual = async () => {
    if (!clientId.trim() || !clientSecret.trim()) {
      setError('Client ID and Client Secret are required');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      await configApi.setDriveCredentialsManual(
        clientId.trim(),
        clientSecret.trim(),
        projectId.trim() || undefined
      );
      setSuccess('Credenciales guardadas correctamente. Ahora puedes probar la conexión.');
      setClientId('');
      setClientSecret('');
      setProjectId('');
      loadStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error saving credentials');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTestConnection = async () => {
    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      const result = await configApi.testDriveConnection();
      setSuccess(result.message || 'Conexión exitosa');
      loadStatus();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error testing connection');
    } finally {
      setSubmitting(false);
    }
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
      <Typography variant="h4" gutterBottom>
        Google Drive Setup
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Configure OAuth 2.0 credentials to enable Google Drive synchronization
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mt: 2, mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mt: 2, mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Status Card */}
      <Card sx={{ mt: 3, mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Status
          </Typography>
          <List>
            <ListItem>
              <ListItemText primary="Credentials File (credentials.json)" />
              {status?.credentials_configured ? (
                <Chip icon={<CheckCircleIcon />} label="Configured" color="success" size="small" />
              ) : (
                <Chip icon={<ErrorIcon />} label="Not Configured" color="error" size="small" />
              )}
            </ListItem>
            <ListItem>
              <ListItemText primary="OAuth Token (token.json)" />
              {status?.token_exists ? (
                <Chip icon={<CheckCircleIcon />} label="Authenticated" color="success" size="small" />
              ) : (
                <Chip icon={<ErrorIcon />} label="Not Authenticated" color="warning" size="small" />
              )}
            </ListItem>
            <ListItem>
              <ListItemText primary="Drive Connection" />
              {status?.drive_connected ? (
                <Chip icon={<CheckCircleIcon />} label="Connected" color="success" size="small" />
              ) : (
                <Chip icon={<ErrorIcon />} label="Not Connected" color="error" size="small" />
              )}
            </ListItem>
          </List>
          {status?.error_message && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {status.error_message}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Setup Instructions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Setup Instructions
          </Typography>
          <Stepper orientation="vertical">
            <Step active>
              <StepLabel>Create Google Cloud Project</StepLabel>
              <StepContent>
                <Typography variant="body2" paragraph>
                  1. Go to{' '}
                  <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer">
                    Google Cloud Console
                  </a>
                </Typography>
                <Typography variant="body2" paragraph>
                  2. Click on the project selector (top left)
                </Typography>
                <Typography variant="body2" paragraph>
                  3. Click "New Project"
                </Typography>
                <Typography variant="body2" paragraph>
                  4. Name: "File Search RAG App" (or your preference)
                </Typography>
                <Typography variant="body2">5. Click "Create"</Typography>
              </StepContent>
            </Step>

            <Step active>
              <StepLabel>Enable Google Drive API</StepLabel>
              <StepContent>
                <Typography variant="body2" paragraph>
                  1. In the sidebar, go to <strong>APIs & Services → Library</strong>
                </Typography>
                <Typography variant="body2" paragraph>
                  2. Search for "Google Drive API"
                </Typography>
                <Typography variant="body2" paragraph>
                  3. Click on "Google Drive API"
                </Typography>
                <Typography variant="body2">4. Click "ENABLE"</Typography>
              </StepContent>
            </Step>

            <Step active>
              <StepLabel>Configure OAuth Consent Screen</StepLabel>
              <StepContent>
                <Typography variant="body2" paragraph>
                  1. Go to <strong>APIs & Services → OAuth consent screen</strong>
                </Typography>
                <Typography variant="body2" paragraph>
                  2. Select <strong>External</strong> (users can be anyone with Google account)
                </Typography>
                <Typography variant="body2" paragraph>
                  3. Click "Create"
                </Typography>
                <Typography variant="body2" paragraph>
                  4. Fill in the form:
                  <br />
                  &nbsp;&nbsp;- App name: "File Search RAG"
                  <br />
                  &nbsp;&nbsp;- Support email: your email
                  <br />
                  &nbsp;&nbsp;- Developer email: your email
                </Typography>
                <Typography variant="body2" paragraph>
                  5. Click "Save and Continue"
                </Typography>
                <Typography variant="body2" paragraph>
                  6. In "Scopes", click "Add or remove scopes"
                </Typography>
                <Typography variant="body2" paragraph>
                  7. Search and add: <code>https://www.googleapis.com/auth/drive.readonly</code>
                </Typography>
                <Typography variant="body2" paragraph>
                  8. Click "Update" then "Save and Continue"
                </Typography>
                <Typography variant="body2" paragraph>
                  9. In "Test users", add your Google email
                </Typography>
                <Typography variant="body2">10. Click "Save and Continue"</Typography>
              </StepContent>
            </Step>

            <Step active>
              <StepLabel>Create OAuth 2.0 Credentials</StepLabel>
              <StepContent>
                <Typography variant="body2" paragraph>
                  1. Go to <strong>APIs & Services → Credentials</strong>
                </Typography>
                <Typography variant="body2" paragraph>
                  2. Click "Create Credentials" → "OAuth 2.0 Client ID"
                </Typography>
                <Typography variant="body2" paragraph>
                  3. Application type: <strong>Desktop application</strong>
                </Typography>
                <Typography variant="body2" paragraph>
                  4. Name: "File Search RAG Desktop Client"
                </Typography>
                <Typography variant="body2" paragraph>
                  5. Click "Create"
                </Typography>
                <Typography variant="body2" paragraph>
                  6. You'll see a popup with your credentials:
                  <br />
                  &nbsp;&nbsp;- You can download the JSON file, OR
                  <br />
                  &nbsp;&nbsp;- Copy the Client ID and Client Secret to paste below
                </Typography>
              </StepContent>
            </Step>
          </Stepper>
        </CardContent>
      </Card>

      {/* Credentials Input Form */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Configure Credentials
          </Typography>

          <Tabs value={inputMode} onChange={(e, v) => setInputMode(v)} sx={{ mb: 2 }}>
            <Tab label="Enter Client ID & Secret" value="manual" />
            <Tab label="Paste JSON File" value="json" />
          </Tabs>

          <Divider sx={{ mb: 3 }} />

          {inputMode === 'manual' ? (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                After creating OAuth credentials, copy the Client ID and Client Secret from the Google Cloud Console
                and paste them below.
              </Typography>

              <TextField
                fullWidth
                label="Client ID"
                value={clientId}
                onChange={(e) => setClientId(e.target.value)}
                placeholder="662191279043-xxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com"
                sx={{ mt: 2, mb: 2 }}
                helperText="The OAuth 2.0 Client ID from Google Cloud Console"
              />

              <TextField
                fullWidth
                label="Client Secret"
                type="password"
                value={clientSecret}
                onChange={(e) => setClientSecret(e.target.value)}
                placeholder="GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx"
                sx={{ mb: 2 }}
                helperText="The OAuth 2.0 Client Secret from Google Cloud Console"
              />

              <TextField
                fullWidth
                label="Project ID (Optional)"
                value={projectId}
                onChange={(e) => setProjectId(e.target.value)}
                placeholder="file-search-rag-app"
                sx={{ mb: 2 }}
                helperText="Your Google Cloud Project ID (optional)"
              />

              <Button
                variant="contained"
                startIcon={<EditIcon />}
                onClick={handleSaveManual}
                disabled={submitting || !clientId.trim() || !clientSecret.trim()}
              >
                {submitting ? 'Saving...' : 'Save Credentials'}
              </Button>
            </Box>
          ) : (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                If you downloaded the credentials JSON file from Google Cloud Console, paste its entire contents
                below.
              </Typography>

              <TextField
                fullWidth
                label="Credentials JSON"
                multiline
                rows={12}
                value={credentialsJSON}
                onChange={(e) => setCredentialsJSON(e.target.value)}
                placeholder='{"installed":{"client_id":"...","client_secret":"...","auth_uri":"...","token_uri":"..."}}'
                sx={{ mt: 2, mb: 2, fontFamily: 'monospace' }}
                helperText="Paste the complete contents of credentials.json file"
              />

              <Button
                variant="contained"
                startIcon={<CloudUploadIcon />}
                onClick={handleSaveJSON}
                disabled={submitting || !credentialsJSON.trim()}
              >
                {submitting ? 'Saving...' : 'Save Credentials'}
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Test Connection */}
      {status?.credentials_configured && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Test Connection
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {status.token_exists
                ? 'Test the connection to Google Drive to verify everything is working.'
                : 'Click below to start the OAuth authentication flow. Your browser will open to authorize the application.'}
            </Typography>
            <Button
              variant="contained"
              color="primary"
              startIcon={<PlayArrowIcon />}
              onClick={handleTestConnection}
              disabled={submitting}
            >
              {submitting ? 'Testing...' : status.token_exists ? 'Test Connection' : 'Authenticate with Google'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Additional Information */}
      <Paper sx={{ mt: 3, p: 2, bgcolor: 'info.light' }}>
        <Typography variant="body2" paragraph>
          <strong>Security Notes:</strong>
        </Typography>
        <Typography variant="body2" component="div">
          <ul>
            <li>The credentials are stored securely in your backend server</li>
            <li>Read-only access: The app can only read files, not modify or delete them</li>
            <li>
              You can revoke access anytime at{' '}
              <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener noreferrer">
                Google Account Permissions
              </a>
            </li>
          </ul>
        </Typography>
      </Paper>
    </Box>
  );
}
