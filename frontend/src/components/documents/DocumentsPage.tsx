/**
 * Documents management page
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  Chip,
  Collapse,
} from '@mui/material';
import {
  Add,
  Delete,
  Edit,
  ExpandMore,
  ExpandLess,
  CloudUpload,
} from '@mui/icons-material';
import { documentsApi } from '@/services/api';
import type { Document } from '@/types';

const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [openUpload, setOpenUpload] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [metadata, setMetadata] = useState<Array<{ key: string; value: string }>>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [maxTokensPerChunk, setMaxTokensPerChunk] = useState('');
  const [maxOverlapTokens, setMaxOverlapTokens] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStoreId, setActiveStoreId] = useState<string | null>(null);

  useEffect(() => {
    const storeId = localStorage.getItem('activeStoreId');
    setActiveStoreId(storeId);
    if (storeId) {
      loadDocuments(storeId);
    }
  }, []);

  const loadDocuments = async (storeId: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await documentsApi.list(storeId);
      setDocuments(response.documents);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error loading documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      setSelectedFile(file);
      if (!displayName) {
        setDisplayName(file.name);
      }
    }
  };

  const handleAddMetadata = () => {
    setMetadata([...metadata, { key: '', value: '' }]);
  };

  const handleRemoveMetadata = (index: number) => {
    setMetadata(metadata.filter((_, i) => i !== index));
  };

  const handleMetadataChange = (index: number, field: 'key' | 'value', value: string) => {
    const newMetadata = [...metadata];
    newMetadata[index][field] = value;
    setMetadata(newMetadata);
  };

  const handleUpload = async () => {
    if (!selectedFile || !activeStoreId) return;

    setUploading(true);
    setError(null);

    try {
      const metadataObj: Record<string, any> = {};
      metadata.forEach((item) => {
        if (item.key) {
          // Try to parse as number
          const numValue = parseFloat(item.value);
          metadataObj[item.key] = isNaN(numValue) ? item.value : numValue;
        }
      });

      const chunkingConfig: any = {};
      if (maxTokensPerChunk) chunkingConfig.max_tokens_per_chunk = parseInt(maxTokensPerChunk);
      if (maxOverlapTokens) chunkingConfig.max_overlap_tokens = parseInt(maxOverlapTokens);

      await documentsApi.upload(
        activeStoreId,
        selectedFile,
        displayName || undefined,
        Object.keys(metadataObj).length > 0 ? metadataObj : undefined,
        Object.keys(chunkingConfig).length > 0 ? chunkingConfig : undefined
      );

      // Reset form
      setOpenUpload(false);
      setSelectedFile(null);
      setDisplayName('');
      setMetadata([]);
      setMaxTokensPerChunk('');
      setMaxOverlapTokens('');
      setShowAdvanced(false);

      await loadDocuments(activeStoreId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error uploading document');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!window.confirm('Are you sure? This action cannot be undone.')) return;
    if (!activeStoreId) return;

    try {
      await documentsApi.delete(activeStoreId, documentId);
      await loadDocuments(activeStoreId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error deleting document');
    }
  };

  if (!activeStoreId) {
    return (
      <Alert severity="warning">
        Please select an active store in the Stores page first.
      </Alert>
    );
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Documents</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpenUpload(true)}>
          Upload Document
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        Active Store: <strong>{activeStoreId}</strong>
      </Alert>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {documents.length === 0 ? (
        <Alert severity="info">No documents found. Upload your first document to get started.</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Metadata</TableCell>
                <TableCell>State</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {documents.map((doc) => (
                <TableRow key={doc.name}>
                  <TableCell>{doc.display_name}</TableCell>
                  <TableCell>
                    {Object.entries(doc.custom_metadata).map(([key, value]) => (
                      <Chip
                        key={key}
                        label={`${key}: ${value}`}
                        size="small"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </TableCell>
                  <TableCell>
                    <Chip label={doc.state || 'INDEXED'} size="small" color="success" />
                  </TableCell>
                  <TableCell>
                    {doc.create_time ? new Date(doc.create_time).toLocaleDateString() : '-'}
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" color="error" onClick={() => handleDelete(doc.name)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Upload Dialog */}
      <Dialog open={openUpload} onClose={() => !uploading && setOpenUpload(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Document</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Button variant="outlined" component="label" fullWidth startIcon={<CloudUpload />}>
              {selectedFile ? selectedFile.name : 'Select File'}
              <input type="file" hidden onChange={handleFileSelect} />
            </Button>

            <TextField
              fullWidth
              label="Display Name"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              sx={{ mt: 2 }}
            />

            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
              Metadata (up to 20 key-value pairs)
            </Typography>
            {metadata.map((item, index) => (
              <Box key={index} display="flex" gap={1} mb={1}>
                <TextField
                  size="small"
                  label="Key"
                  value={item.key}
                  onChange={(e) => handleMetadataChange(index, 'key', e.target.value)}
                  sx={{ flex: 1 }}
                />
                <TextField
                  size="small"
                  label="Value"
                  value={item.value}
                  onChange={(e) => handleMetadataChange(index, 'value', e.target.value)}
                  sx={{ flex: 1 }}
                />
                <IconButton size="small" onClick={() => handleRemoveMetadata(index)}>
                  <Delete />
                </IconButton>
              </Box>
            ))}
            <Button size="small" onClick={handleAddMetadata} disabled={metadata.length >= 20}>
              Add Metadata
            </Button>

            <Box sx={{ mt: 2 }}>
              <Button
                size="small"
                onClick={() => setShowAdvanced(!showAdvanced)}
                endIcon={showAdvanced ? <ExpandLess /> : <ExpandMore />}
              >
                Advanced Options
              </Button>
              <Collapse in={showAdvanced}>
                <Box sx={{ mt: 2 }}>
                  <TextField
                    fullWidth
                    size="small"
                    type="number"
                    label="Max Tokens Per Chunk (100-2048)"
                    value={maxTokensPerChunk}
                    onChange={(e) => setMaxTokensPerChunk(e.target.value)}
                    sx={{ mb: 1 }}
                  />
                  <TextField
                    fullWidth
                    size="small"
                    type="number"
                    label="Max Overlap Tokens (0-512)"
                    value={maxOverlapTokens}
                    onChange={(e) => setMaxOverlapTokens(e.target.value)}
                  />
                </Box>
              </Collapse>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUpload(false)} disabled={uploading}>
            Cancel
          </Button>
          <Button onClick={handleUpload} variant="contained" disabled={uploading || !selectedFile}>
            {uploading ? <CircularProgress size={24} /> : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DocumentsPage;
