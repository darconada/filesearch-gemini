/**
 * Google Drive sync page (base for future implementation)
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
} from '@mui/material';
import { Add, Delete, Sync, Upload, History } from '@mui/icons-material';
import { Tooltip } from '@mui/material';
import { driveApi, storesApi, fileUpdatesApi, projectsApi } from '@/services/api';
import type { DriveLink, Store, FileVersionHistory, Project } from '@/types';
import { SyncMode } from '@/types';
import DriveFilePicker from './DriveFilePicker';

const DrivePage: React.FC = () => {
  const [links, setLinks] = useState<DriveLink[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [activeProject, setActiveProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(false);
  const [openCreate, setOpenCreate] = useState(false);
  const [openReplace, setOpenReplace] = useState(false);
  const [openHistory, setOpenHistory] = useState(false);
  const [driveFileId, setDriveFileId] = useState('');
  const [driveFileName, setDriveFileName] = useState('');
  const [selectedStoreId, setSelectedStoreId] = useState('');
  const [selectedLinkId, setSelectedLinkId] = useState('');
  const [replaceFile, setReplaceFile] = useState<File | null>(null);
  const [versionHistory, setVersionHistory] = useState<FileVersionHistory | null>(null);
  const [syncMode, setSyncMode] = useState<SyncMode>(SyncMode.MANUAL);
  const [syncInterval, setSyncInterval] = useState('60');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();

    // Listen for active project changes and reload data
    const handleProjectChange = () => {
      console.log('Active project changed, reloading Drive links...');
      loadData();
    };

    window.addEventListener('activeProjectChanged', handleProjectChange);

    return () => {
      window.removeEventListener('activeProjectChanged', handleProjectChange);
    };
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [linksResponse, storesResponse, projectsResponse] = await Promise.all([
        driveApi.list(),
        storesApi.list(),
        projectsApi.list(),
      ]);
      setLinks(linksResponse.links);
      setStores(storesResponse.stores);

      // Find active project
      const active = projectsResponse.projects.find(p => p.is_active);
      setActiveProject(active || null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error loading data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    if (!driveFileId.trim() || !selectedStoreId) return;

    setCreating(true);
    setError(null);

    try {
      await driveApi.create({
        drive_file_id: driveFileId,
        store_id: selectedStoreId,
        sync_mode: syncMode,
        sync_interval_minutes: syncMode === SyncMode.AUTO ? parseInt(syncInterval) : undefined,
      });

      setOpenCreate(false);
      setDriveFileId('');
      setDriveFileName('');
      setSelectedStoreId('');
      setSyncMode(SyncMode.MANUAL);
      setSyncInterval('60');
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creating link');
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (linkId: string) => {
    if (!window.confirm('Delete this Drive link?')) return;

    try {
      await driveApi.delete(linkId);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error deleting link');
    }
  };

  const handleSync = async (linkId: string) => {
    try {
      await driveApi.sync(linkId, false);
      await loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error syncing link');
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

  const handleDriveFileSelect = (file: { id: string; name: string }) => {
    setDriveFileId(file.id);
    setDriveFileName(file.name);
  };

  const getStoreDisplayName = (storeId: string) => {
    const store = stores.find((s) => s.name === storeId);
    return store ? store.display_name : storeId;
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Google Drive Sync
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Configure Google Drive synchronization to automatically sync files from Drive to File Search stores.
        Supports manual and automatic sync modes. See DRIVE_SETUP.md for OAuth configuration instructions.
      </Alert>

      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Drive Links</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpenCreate(true)}>
          Add Link
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      ) : links.filter(link => stores.some(s => s.name === link.store_id)).length === 0 ? (
        <Alert severity="info">
          {links.length > 0
            ? "No Drive links found for the active project (switch projects to see other links)."
            : "No Drive links configured."}
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Drive File</TableCell>
                <TableCell>Store</TableCell>
                <TableCell>Project</TableCell>
                <TableCell>Mode</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Synced</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {links
                .filter(link => stores.some(s => s.name === link.store_id))
                .map((link) => (
                  <TableRow key={link.id}>
                    <TableCell>
                      {link.drive_file_name ? (
                        <Tooltip title={`File ID: ${link.drive_file_id}`} arrow>
                          <Box component="span" sx={{ cursor: 'help' }}>
                            {link.drive_file_name}
                          </Box>
                        </Tooltip>
                      ) : (
                        <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                          {link.drive_file_id}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{getStoreDisplayName(link.store_id)}</TableCell>
                    <TableCell>
                      {activeProject ? (
                        <Chip label={activeProject.name} size="small" variant="outlined" />
                      ) : (
                        <Typography variant="caption" color="text.secondary">-</Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={link.sync_mode}
                        size="small"
                        color={link.sync_mode === SyncMode.AUTO ? 'primary' : 'default'}
                      />
                      {link.sync_interval_minutes && (
                        <Typography variant="caption" display="block">
                          Every {link.sync_interval_minutes}min
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip label={`v${link.version}`} size="small" color="primary" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={link.status}
                        size="small"
                        color={link.status === 'synced' ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      {link.last_synced_at
                        ? new Date(link.last_synced_at).toLocaleString()
                        : 'Never'}
                    </TableCell>
                    <TableCell>
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
                      <IconButton size="small" color="error" onClick={() => handleDelete(link.id)}>
                        <Delete />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Create Link Dialog */}
      <Dialog open={openCreate} onClose={() => !creating && setOpenCreate(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Drive Link</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-start', mb: 2 }}>
              <TextField
                fullWidth
                label="Drive File ID"
                value={driveFileId}
                onChange={(e) => setDriveFileId(e.target.value)}
                placeholder="Enter manually or browse Drive"
                helperText={driveFileName || "File ID from Google Drive"}
              />
              <DriveFilePicker
                onFileSelect={handleDriveFileSelect}
                disabled={creating}
              />
            </Box>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Destination Store</InputLabel>
              <Select
                value={selectedStoreId}
                onChange={(e) => setSelectedStoreId(e.target.value)}
                label="Destination Store"
              >
                {stores.map((store) => (
                  <MenuItem key={store.name} value={store.name}>
                    {store.display_name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Sync Mode</InputLabel>
              <Select
                value={syncMode}
                onChange={(e) => setSyncMode(e.target.value as SyncMode)}
                label="Sync Mode"
              >
                <MenuItem value={SyncMode.MANUAL}>Manual</MenuItem>
                <MenuItem value={SyncMode.AUTO}>Automatic</MenuItem>
              </Select>
            </FormControl>

            {syncMode === SyncMode.AUTO && (
              <TextField
                fullWidth
                type="number"
                label="Sync Interval (minutes)"
                value={syncInterval}
                onChange={(e) => setSyncInterval(e.target.value)}
                inputProps={{ min: 5 }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreate(false)} disabled={creating}>
            Cancel
          </Button>
          <Button
            onClick={handleCreate}
            variant="contained"
            disabled={creating || !driveFileId.trim() || !selectedStoreId}
          >
            {creating ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Replace File Dialog */}
      <Dialog open={openReplace} onClose={() => setOpenReplace(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Replace File</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2, mt: 1 }}>
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
          <Typography variant="subtitle2" gutterBottom sx={{ mt: 1 }}>
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
    </Box>
  );
};

export default DrivePage;
