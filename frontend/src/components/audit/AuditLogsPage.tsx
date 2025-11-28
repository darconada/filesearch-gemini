/**
 * Audit Logs Page - Muestra el historial de acciones del sistema
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TablePagination,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import api from '@/services/api';
import type { AuditLog, AuditLogFilter, AuditStats } from '@/types';

const AuditLogsPage: React.FC = () => {
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(50);
  const [filters, setFilters] = useState<AuditLogFilter>({});

  // Query para obtener logs
  const { data: logsData, isLoading: logsLoading, error: logsError } = useQuery({
    queryKey: ['auditLogs', page, pageSize, filters],
    queryFn: () => api.getAuditLogs({ ...filters, page: page + 1, page_size: pageSize }),
    refetchInterval: 30000, // Refrescar cada 30 segundos
  });

  // Query para obtener estadísticas
  const { data: stats } = useQuery<AuditStats>({
    queryKey: ['auditStats'],
    queryFn: () => api.getAuditStats(30),
    refetchInterval: 60000, // Refrescar cada minuto
  });

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPageSize(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getActionColor = (action: string): "default" | "primary" | "secondary" | "error" | "warning" | "info" | "success" => {
    if (action.includes('create')) return 'success';
    if (action.includes('delete')) return 'error';
    if (action.includes('update')) return 'info';
    if (action.includes('activate')) return 'primary';
    if (action.includes('query')) return 'secondary';
    return 'default';
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatAction = (action: string) => {
    return action.replace(/_/g, ' ').toUpperCase();
  };

  if (logsLoading && !logsData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (logsError) {
    return (
      <Box p={3}>
        <Alert severity="error">
          Error loading audit logs: {logsError instanceof Error ? logsError.message : 'Unknown error'}
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Logs
      </Typography>

      <Typography variant="body2" color="text.secondary" paragraph>
        Historial de todas las acciones realizadas en el sistema
      </Typography>

      {/* Estadísticas */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total Actions (30d)
                </Typography>
                <Typography variant="h4">{stats.total_actions}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Success Rate
                </Typography>
                <Typography variant="h4" color="success.main">
                  {stats.success_rate.toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Successful
                </Typography>
                <Typography variant="h4" color="success.main">
                  {stats.successful_actions}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Failed
                </Typography>
                <Typography variant="h4" color="error.main">
                  {stats.failed_actions}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filtros */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Resource Type</InputLabel>
              <Select
                value={filters.resource_type || ''}
                label="Resource Type"
                onChange={(e) => setFilters({ ...filters, resource_type: e.target.value || undefined })}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="project">Project</MenuItem>
                <MenuItem value="store">Store</MenuItem>
                <MenuItem value="document">Document</MenuItem>
                <MenuItem value="query">Query</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.success === undefined ? 'all' : filters.success ? 'success' : 'failed'}
                label="Status"
                onChange={(e) => {
                  const value = e.target.value;
                  setFilters({
                    ...filters,
                    success: value === 'all' ? undefined : value === 'success'
                  });
                }}
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="success">Success</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              size="small"
              label="User/IP"
              value={filters.user_identifier || ''}
              onChange={(e) => setFilters({ ...filters, user_identifier: e.target.value || undefined })}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <TextField
              fullWidth
              size="small"
              label="Resource ID"
              value={filters.resource_id || ''}
              onChange={(e) => setFilters({ ...filters, resource_id: e.target.value || undefined })}
            />
          </Grid>
        </Grid>
      </Paper>

      {/* Tabla de logs */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell>
              <TableCell>Action</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>User/IP</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {logsData?.logs.map((log: AuditLog) => (
              <TableRow key={log.id}>
                <TableCell>{formatTimestamp(log.timestamp)}</TableCell>
                <TableCell>
                  <Chip
                    label={formatAction(log.action)}
                    color={getActionColor(log.action)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {log.resource_type && (
                    <Typography variant="body2">
                      {log.resource_type}
                      {log.resource_id && `: ${log.resource_id}`}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    {log.user_identifier || 'N/A'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={log.success ? 'Success' : 'Failed'}
                    color={log.success ? 'success' : 'error'}
                    size="small"
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  {log.error_message && (
                    <Typography variant="body2" color="error">
                      {log.error_message}
                    </Typography>
                  )}
                  {log.details && Object.keys(log.details).length > 0 && (
                    <Typography variant="caption" sx={{ display: 'block', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {JSON.stringify(log.details)}
                    </Typography>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <TablePagination
          component="div"
          count={logsData?.total || 0}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={pageSize}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[25, 50, 100, 200]}
        />
      </TableContainer>
    </Box>
  );
};

export default AuditLogsPage;
