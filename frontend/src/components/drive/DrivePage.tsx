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
import { Add, Delete, Sync } from '@mui/icons-material';
import { driveApi, storesApi } from '@/services/api';
import type { DriveLink, Store } from '@/types';
import { SyncMode } from '@/types';

const DrivePage: React.FC = () => {
  const [links, setLinks] = useState<DriveLink[]>([]);
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(false);
  const [openCreate, setOpenCreate] = useState(false);
  const [driveFileId, setDriveFileId] = useState('');
  const [selectedStoreId, setSelectedStoreId] = useState('');
  const [syncMode, setSyncMode] = useState<SyncMode>(SyncMode.MANUAL);
  const [syncInterval, setSyncInterval] = useState('60');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [linksResponse, storesResponse] = await Promise.all([
        driveApi.list(),
        storesApi.list(),
      ]);
      setLinks(linksResponse.links);
      setStores(storesResponse.stores);
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
      ) : links.length === 0 ? (
        <Alert severity="info">No Drive links configured.</Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Drive File ID</TableCell>
                <TableCell>Store</TableCell>
                <TableCell>Mode</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Synced</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {links.map((link) => (
                <TableRow key={link.id}>
                  <TableCell>{link.drive_file_id}</TableCell>
                  <TableCell>{getStoreDisplayName(link.store_id)}</TableCell>
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
                    <IconButton size="small" onClick={() => handleSync(link.id)}>
                      <Sync />
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
            <TextField
              fullWidth
              label="Drive File ID"
              value={driveFileId}
              onChange={(e) => setDriveFileId(e.target.value)}
              placeholder="Enter Google Drive file ID"
              sx={{ mb: 2 }}
            />

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
    </Box>
  );
};

export default DrivePage;
