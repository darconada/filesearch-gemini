/**
 * RAG Query page
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  TextField,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Collapse,
} from '@mui/material';
import { Search, ExpandMore, ExpandLess } from '@mui/icons-material';
import { queryApi, storesApi } from '@/services/api';
import type { QueryResponse, Store } from '@/types';

const QueryPage: React.FC = () => {
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStores, setSelectedStores] = useState<string[]>([]);
  const [question, setQuestion] = useState('');
  const [metadataFilter, setMetadataFilter] = useState('');
  const [showFilter, setShowFilter] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<QueryResponse | null>(null);

  useEffect(() => {
    loadStores();

    // Listen for active project changes and reload stores
    const handleProjectChange = () => {
      console.log('Active project changed, reloading stores in QueryPage...');
      setSelectedStores([]);
      setResponse(null);
      loadStores();
    };

    window.addEventListener('activeProjectChanged', handleProjectChange);

    return () => {
      window.removeEventListener('activeProjectChanged', handleProjectChange);
    };
  }, []);

  const loadStores = async () => {
    try {
      const response = await storesApi.list();
      setStores(response.stores);

      // Auto-select active store if exists
      const activeStoreId = localStorage.getItem('activeStoreId');
      if (activeStoreId && response.stores.some((s) => s.name === activeStoreId)) {
        setSelectedStores([activeStoreId]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error loading stores');
    }
  };

  const handleStoreToggle = (storeId: string) => {
    if (selectedStores.includes(storeId)) {
      setSelectedStores(selectedStores.filter((id) => id !== storeId));
    } else {
      setSelectedStores([...selectedStores, storeId]);
    }
  };

  const handleQuery = async () => {
    if (!question.trim() || selectedStores.length === 0) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await queryApi.execute({
        question: question.trim(),
        store_ids: selectedStores,
        metadata_filter: metadataFilter.trim() || undefined,
      });
      setResponse(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error executing query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        RAG Query
      </Typography>

      {/* Query Input */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Your Question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents..."
            sx={{ mb: 2 }}
          />

          <Typography variant="subtitle2" gutterBottom>
            Select Stores to Query
          </Typography>
          <FormGroup>
            {stores.map((store) => (
              <FormControlLabel
                key={store.name}
                control={
                  <Checkbox
                    checked={selectedStores.includes(store.name)}
                    onChange={() => handleStoreToggle(store.name)}
                  />
                }
                label={store.display_name}
              />
            ))}
          </FormGroup>

          {stores.length === 0 && (
            <Alert severity="info" sx={{ mt: 1 }}>
              No stores available. Create stores and upload documents first.
            </Alert>
          )}

          <Box sx={{ mt: 2 }}>
            <Button
              size="small"
              onClick={() => setShowFilter(!showFilter)}
              endIcon={showFilter ? <ExpandLess /> : <ExpandMore />}
            >
              Metadata Filter
            </Button>
            <Collapse in={showFilter}>
              <TextField
                fullWidth
                size="small"
                label="Metadata Filter"
                value={metadataFilter}
                onChange={(e) => setMetadataFilter(e.target.value)}
                placeholder='e.g., author="Robert Graves"'
                helperText='Use syntax like: author="value" or year=2021'
                sx={{ mt: 2 }}
              />
            </Collapse>
          </Box>

          <Button
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <Search />}
            onClick={handleQuery}
            disabled={loading || !question.trim() || selectedStores.length === 0}
            sx={{ mt: 2 }}
          >
            {loading ? 'Searching...' : 'Query'}
          </Button>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Response */}
      {response && (
        <Box>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Answer
            </Typography>
            <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
              {response.answer}
            </Typography>
            {response.model_used && (
              <Typography variant="caption" color="text.secondary">
                Model: {response.model_used}
              </Typography>
            )}
          </Paper>

          {response.sources.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Sources ({response.sources.length})
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {response.sources.map((source, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" color="primary">
                    {source.document_display_name || 'Unknown Document'}
                  </Typography>
                  {source.document_id && (
                    <Typography variant="caption" display="block" color="text.secondary">
                      ID: {source.document_id}
                    </Typography>
                  )}
                  {Object.keys(source.metadata).length > 0 && (
                    <Typography variant="body2" color="text.secondary">
                      Metadata: {JSON.stringify(source.metadata)}
                    </Typography>
                  )}
                  {source.chunk_text && (
                    <Typography variant="body2" sx={{ mt: 1, fontStyle: 'italic' }}>
                      "{source.chunk_text}"
                    </Typography>
                  )}
                  {source.relevance_score && (
                    <Typography variant="caption" color="text.secondary">
                      Relevance: {source.relevance_score.toFixed(3)}
                    </Typography>
                  )}
                  {index < response.sources.length - 1 && <Divider sx={{ mt: 2 }} />}
                </Box>
              ))}
            </Paper>
          )}
        </Box>
      )}
    </Box>
  );
};

export default QueryPage;
