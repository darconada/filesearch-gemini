/**
 * Stores management page
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
} from '@mui/material';
import { Add, Delete, CheckCircle } from '@mui/icons-material';
import { storesApi } from '@/services/api';
import type { Store } from '@/types';

const StoresPage: React.FC = () => {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(false);
  const [openCreate, setOpenCreate] = useState(false);
  const [newStoreName, setNewStoreName] = useState('');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStoreId, setActiveStoreId] = useState<string | null>(null);

  const loadStores = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await storesApi.list();
      setStores(response.stores);

      // Set first store as active if none selected
      if (response.stores.length > 0 && !activeStoreId) {
        setActiveStoreId(response.stores[0].name);
        localStorage.setItem('activeStoreId', response.stores[0].name);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error loading stores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStores();
    // Load active store from localStorage
    const savedStoreId = localStorage.getItem('activeStoreId');
    if (savedStoreId) {
      setActiveStoreId(savedStoreId);
    }
  }, []);

  const handleCreateStore = async () => {
    if (!newStoreName.trim()) return;

    setCreating(true);
    try {
      await storesApi.create({ display_name: newStoreName });
      setOpenCreate(false);
      setNewStoreName('');
      await loadStores();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error creating store');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteStore = async (storeId: string) => {
    if (!window.confirm('Are you sure? This will delete the store and all its documents.')) {
      return;
    }

    try {
      await storesApi.delete(storeId);
      if (activeStoreId === storeId) {
        setActiveStoreId(null);
        localStorage.removeItem('activeStoreId');
      }
      await loadStores();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error deleting store');
    }
  };

  const handleSelectStore = (storeId: string) => {
    setActiveStoreId(storeId);
    localStorage.setItem('activeStoreId', storeId);
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
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">File Search Stores</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setOpenCreate(true)}>
          Create Store
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {stores.length === 0 ? (
        <Alert severity="info">
          No stores found. Create your first store to get started.
        </Alert>
      ) : (
        <Grid container spacing={2}>
          {stores.map((store) => (
            <Grid item xs={12} sm={6} md={4} key={store.name}>
              <Card
                sx={{
                  cursor: 'pointer',
                  border: activeStoreId === store.name ? 2 : 0,
                  borderColor: 'primary.main',
                }}
                onClick={() => handleSelectStore(store.name)}
              >
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                    <Typography variant="h6" noWrap>
                      {store.display_name}
                    </Typography>
                    {activeStoreId === store.name && (
                      <Chip icon={<CheckCircle />} label="Active" color="primary" size="small" />
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary" sx={{ wordBreak: 'break-all' }}>
                    {store.name}
                  </Typography>
                  {store.create_time && (
                    <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
                      Created: {new Date(store.create_time).toLocaleDateString()}
                    </Typography>
                  )}
                </CardContent>
                <CardActions>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteStore(store.name);
                    }}
                  >
                    <Delete />
                  </IconButton>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Store Dialog */}
      <Dialog open={openCreate} onClose={() => !creating && setOpenCreate(false)}>
        <DialogTitle>Create New Store</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            fullWidth
            label="Store Name"
            value={newStoreName}
            onChange={(e) => setNewStoreName(e.target.value)}
            sx={{ mt: 2 }}
            disabled={creating}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreate(false)} disabled={creating}>
            Cancel
          </Button>
          <Button onClick={handleCreateStore} variant="contained" disabled={creating || !newStoreName.trim()}>
            {creating ? <CircularProgress size={24} /> : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StoresPage;
