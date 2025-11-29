/**
 * Google Drive File Picker Component
 * Uses Google Picker API to allow users to select files from their Drive
 */
import React, { useState } from 'react';
import { Button, CircularProgress, Alert } from '@mui/material';
import { FolderOpen } from '@mui/icons-material';
import { driveApi } from '@/services/api';

// Declare global google object for TypeScript
declare global {
  interface Window {
    google?: any;
    gapi?: any;
  }
}

interface DriveFile {
  id: string;
  name: string;
  mimeType?: string;
}

interface DriveFilePickerProps {
  onFileSelect: (file: DriveFile) => void;
  disabled?: boolean;
}

// Google API Key - This should be configured in your Google Cloud Console
// For now, we'll try to get it from environment or use a placeholder
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY || '';
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';

export default function DriveFilePicker({ onFileSelect, disabled = false }: DriveFilePickerProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pickerApiLoaded, setPickerApiLoaded] = useState(false);

  /**
   * Load the Google Picker API script
   */
  const loadPickerApi = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      // Check if already loaded
      if (window.google?.picker) {
        setPickerApiLoaded(true);
        resolve();
        return;
      }

      // Load the Google API script
      if (!window.gapi) {
        const script = document.createElement('script');
        script.src = 'https://apis.google.com/js/api.js';
        script.onload = () => {
          window.gapi.load('picker', {
            callback: () => {
              setPickerApiLoaded(true);
              resolve();
            },
            onerror: () => reject(new Error('Failed to load Google Picker API')),
          });
        };
        script.onerror = () => reject(new Error('Failed to load Google API script'));
        document.body.appendChild(script);
      } else {
        window.gapi.load('picker', {
          callback: () => {
            setPickerApiLoaded(true);
            resolve();
          },
          onerror: () => reject(new Error('Failed to load Google Picker API')),
        });
      }
    });
  };

  /**
   * Create and open the Google Picker
   */
  const openPicker = async () => {
    setLoading(true);
    setError(null);

    try {
      // 1. Load Picker API if not loaded
      if (!pickerApiLoaded) {
        await loadPickerApi();
      }

      // 2. Get OAuth access token from backend
      const { access_token } = await driveApi.getOAuthToken();

      // 3. Create the picker
      const pickerBuilder = new window.google.picker.PickerBuilder()
        // Add different views
        .addView(window.google.picker.ViewId.DOCS) // All documents
        .addView(new window.google.picker.DocsView()
          .setIncludeFolders(true)
          .setMode(window.google.picker.DocsViewMode.LIST))
        // Set OAuth token
        .setOAuthToken(access_token)
        // Set callback
        .setCallback((data: any) => {
          console.log('Picker callback triggered:', data);

          if (data.action === window.google.picker.Action.PICKED) {
            console.log('File picked:', data.docs);
            const file = data.docs[0];
            console.log('Selected file details:', {
              id: file.id,
              name: file.name,
              mimeType: file.mimeType
            });

            onFileSelect({
              id: file.id,
              name: file.name,
              mimeType: file.mimeType,
            });
          }
          // Handle cancel/close action
          if (data.action === window.google.picker.Action.CANCEL) {
            console.log('Picker was closed/cancelled');
          }
        })
        // Appearance and controls
        .setTitle('Select a file from Google Drive')
        .setSize(800, 600);

      // Only set API key if it's actually configured
      if (GOOGLE_API_KEY && GOOGLE_API_KEY.trim()) {
        pickerBuilder.setDeveloperKey(GOOGLE_API_KEY);
      }

      const picker = pickerBuilder.build();

      // 4. Show the picker
      picker.setVisible(true);
    } catch (err: any) {
      console.error('Error opening Drive picker:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to open Drive picker');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="outlined"
        startIcon={loading ? <CircularProgress size={20} /> : <FolderOpen />}
        onClick={openPicker}
        disabled={disabled || loading}
        sx={{ minWidth: 'auto' }}
      >
        Browse Drive
      </Button>
      {error && (
        <Alert severity="error" sx={{ mt: 1 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
    </>
  );
}
