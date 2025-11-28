/**
 * Local file sync page
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Add, Delete, Sync, Upload, History, FolderOpen } from '@mui/icons-material';
import { localFilesApi, storesApi, fileUpdatesApi, projectsApi } from '@/services/api';
import type { LocalFileLink, Store, FileVersionHistory, Project } from '@/types';
import FileBrowserDialog from './FileBrowserDialog';

const LocalFilesPage: React.FC = () => {
  const [links, setLinks] = useState<LocalFileLink[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [openCreate, setOpenCreate] = useState(false);
  const [openReplace, setOpenReplace] = useState(false);
  const [openHistory, setOpenHistory] = useState(false);
  const [filePath, setFilePath] = useState('');
  const [selectedStoreId, setSelectedStoreId] = useState('');
  const [selectedLinkId, setSelectedLinkId] = useState('');
  const [replaceFile, setReplaceFile] = useState<File | null>(null);
  const [versionHistory, setVersionHistory] = useState<FileVersionHistory | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openFileBrowser, setOpenFileBrowser] = useState(false);
  const [metadata, setMetadata] = useState<Record<string, any>>({});
  const [metadataKey, setMetadataKey] = useState('');
  const [metadataValue, setMetadataValue] = useState('');

  useEffect(() => {
    loadData();

    // Listen for project changes
    const handleProjectChanged = () => {
      console.log('LocalFilesPage: Active project changed, reloading data...');
      loadData();
    };

    window.addEventListener('activeProjectChanged', handleProjectChanged);

    return () => {
      window.removeEventListener('activeProjectChanged', handleProjectChanged);
    };
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [linksResponse, storesResponse, projectsResponse] = await Promise.all([
        localFilesApi.list(),
        storesApi.list(),
        projectsApi.list(),
      ]);
      setLinks(linksResponse.links);
      setStores(storesResponse.stores);
      setProjects(projectsResponse.projects);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!filePath.trim() || !selectedStoreId) return;

    setCreating(true);
    setError(null);

    try {
      await localFilesApi.create({
        local_file_path: filePath,
        store_id: selectedStoreId,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
      });

      setOpenCreate(false);
      setFilePath('');
      setSelectedStoreId('');
      setMetadata({});
      setMetadataKey('');
      setMetadataValue('');
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creating link');
    } finally {
      setCreating(false);
    }
  };

  const handleAddMetadata = () => {
    if (!metadataKey.trim() || !metadataValue.trim()) return;

    setMetadata((prev) => ({
      ...prev,
      [metadataKey.trim()]: metadataValue.trim(),
    }));
    setMetadataKey('');
    setMetadataValue('');
  };

  const handleRemoveMetadata = (key: string) => {
    setMetadata((prev) => {
      const updated = { ...prev };
      delete updated[key];
      return updated;
    });
  };

  const handleDelete = async (linkId: string) => {
    if (!window.confirm('Delete this local file link?')) return;

    try {
      await localFilesApi.delete(linkId, false);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error deleting link');
    }
  };

  const handleSync = async (linkId: string) => {
    try {
      await localFilesApi.sync(linkId, false);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error syncing file');
    }
  };

  const handleReplace = async () => {
    if (!replaceFile || !selectedLinkId) return;

    setCreating(true);
    setError(null);

    try {
      await fileUpdatesApi.replace(selectedLinkId, replaceFile);
      setOpenReplace(false);
      setReplaceFile(null);
      setSelectedLinkId('');
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error replacing file');
    } finally {
      setCreating(false);
    }
  };

  const handleShowHistory = async (linkId: string) => {
    try {
      const history = await fileUpdatesApi.getHistory(linkId);
      setVersionHistory(history);
      setOpenHistory(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error loading history');
    }
  };

  const getStoreDisplayName = (storeId: string) => {
    const store = stores.find((s) => s.name === storeId);
    return store ? store.display_name : storeId;
  };

  const getProjectName = (projectId?: number) => {
    if (!projectId) return '-';
    const project = projects.find((p) => p.id === projectId);
    return project ? project.name : `Project ${projectId}`;
  };

  const handleFileBrowserSelect = (path: string) => {
    setFilePath(path);
    setOpenFileBrowser(false);
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Local File Sync
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Sync local files to File Search stores. Changes are detected using SHA256 hash comparison.
        Files are automatically updated when their content changes.
      </Alert>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Local Files</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpenCreate(true)}>
          Add File
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>File Name</TableCell>
                <TableCell>Path</TableCell>
                <TableCell>Store</TableCell>
                <TableCell>Project</TableCell>
                <TableCell>Metadata</TableCell>
                <TableCell>Size</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Synced</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {links.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <Typography color="text.secondary">No local files configured</Typography>
                  </TableCell>
                </TableRow>
              ) : (
                links.map((link) => (
                  <TableRow key={link.id}>
                    <TableCell>{link.file_name}</TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                      {link.local_file_path}
                    </TableCell>
                    <TableCell>{getStoreDisplayName(link.store_id)}</TableCell>
                    <TableCell>
                      <Chip
                        label={getProjectName(link.project_id)}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {link.custom_metadata && Object.keys(link.custom_metadata).length > 0 ? (
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {Object.entries(link.custom_metadata).slice(0, 2).map(([key, value]) => (
                            <Chip
                              key={key}
                              label={`${key}: ${value}`}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          ))}
                          {Object.keys(link.custom_metadata).length > 2 && (
                            <Chip
                              label={`+${Object.keys(link.custom_metadata).length - 2}`}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.7rem' }}
                            />
                          )}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          -
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{formatFileSize(link.file_size)}</TableCell>
                    <TableCell>
                      <Chip label={`v${link.version}`} size="small" color="primary" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={link.status}
                        color={link.status === 'synced' ? 'success' : link.status === 'error' ? 'error' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {link.last_synced_at ? new Date(link.last_synced_at).toLocaleString() : 'Never'}
                    </TableCell>
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => handleSync(link.id)} title="Sync Now">
                        <Sync />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => {
                          setSelectedLinkId(link.id);
                          setOpenReplace(true);
                        }}
                        title="Replace File"
                      >
                        <Upload />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleShowHistory(link.id)}
                        title="Version History"
                      >
                        <History />
                      </IconButton>
                      <IconButton size="small" onClick={() => handleDelete(link.id)} color="error">
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Dialog open={openCreate} onClose={() => setOpenCreate(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Local File</DialogTitle>
        <DialogContent>
          <Box display="flex" gap={1} alignItems="flex-start">
            <TextField
              fullWidth
              label="File Path (absolute)"
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              placeholder="/home/user/documents/file.pdf"
              margin="normal"
              helperText="Enter the absolute path to the local file"
            />
            <Button
              variant="outlined"
              startIcon={<FolderOpen />}
              onClick={() => setOpenFileBrowser(true)}
              sx={{ mt: 2, minWidth: 'auto' }}
            >
              Browse
            </Button>
          </Box>
          <FormControl fullWidth margin="normal">
            <InputLabel>Target Store</InputLabel>
            <Select
              value={selectedStoreId}
              onChange={(e) => setSelectedStoreId(e.target.value)}
              label="Target Store"
            >
              {stores.map((store) => (
                <MenuItem key={store.name} value={store.name}>
                  {store.display_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
            Metadata (Optional)
          </Typography>
          <Box display="flex" gap={1} alignItems="flex-start">
            <TextField
              label="Key"
              value={metadataKey}
              onChange={(e) => setMetadataKey(e.target.value)}
              size="small"
              sx={{ flex: 1 }}
            />
            <TextField
              label="Value"
              value={metadataValue}
              onChange={(e) => setMetadataValue(e.target.value)}
              size="small"
              sx={{ flex: 1 }}
            />
            <Button
              variant="outlined"
              onClick={handleAddMetadata}
              disabled={!metadataKey.trim() || !metadataValue.trim()}
              sx={{ minWidth: 'auto' }}
            >
              Add
            </Button>
          </Box>
          {Object.keys(metadata).length > 0 && (
            <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              {Object.entries(metadata).map(([key, value]) => (
                <Chip
                  key={key}
                  label={`${key}: ${value}`}
                  onDelete={() => handleRemoveMetadata(key)}
                  size="small"
                />
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreate(false)}>Cancel</Button>
          <Button
            onClick={handleCreate}
            variant="contained"
            disabled={creating || !filePath.trim() || !selectedStoreId}
          >
            {creating ? <CircularProgress size={24} /> : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Replace File Dialog */}
      <Dialog open={openReplace} onClose={() => setOpenReplace(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Replace File</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will replace the current file in File Search. The old version will be saved in history.
          </Alert>
          <Button variant="outlined" component="label" fullWidth>
            Choose New File
            <input
              type="file"
              hidden
              onChange={(e) => setReplaceFile(e.target.files?.[0] || null)}
            />
          </Button>
          {replaceFile && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected: {replaceFile.name}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenReplace(false)}>Cancel</Button>
          <Button
            onClick={handleReplace}
            variant="contained"
            disabled={creating || !replaceFile}
            color="warning"
          >
            {creating ? <CircularProgress size={24} /> : 'Replace'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Version History Dialog */}
      <Dialog open={openHistory} onClose={() => setOpenHistory(false)} maxWidth="md" fullWidth>
        <DialogTitle>Version History: {versionHistory?.file_name}</DialogTitle>
        <DialogContent>
          <Typography variant="subtitle2" gutterBottom>
            Current Version: v{versionHistory?.current_version}
          </Typography>
          <Typography variant="caption" display="block" gutterBottom>
            Document ID: {versionHistory?.current_document_id}
          </Typography>

          {versionHistory && versionHistory.previous_versions.length > 0 ? (
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Version</TableCell>
                    <TableCell>Document ID</TableCell>
                    <TableCell>Replaced At</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {versionHistory.previous_versions.map((version, idx) => (
                    <TableRow key={idx}>
                      <TableCell>v{version.version}</TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {version.document_id}
                      </TableCell>
                      <TableCell>{new Date(version.replaced_at).toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography color="text.secondary" sx={{ mt: 2 }}>
              No previous versions
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenHistory(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* File Browser Dialog */}
      <FileBrowserDialog
        open={openFileBrowser}
        onClose={() => setOpenFileBrowser(false)}
        onSelect={handleFileBrowserSelect}
        title="Browse Server Files"
      />
    </Box>
  );
};

export default LocalFilesPage;
