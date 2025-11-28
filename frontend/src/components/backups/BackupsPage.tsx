import React, { useState } from 'react';
import {
    Box,
    Typography,
    Paper,
    Button,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    IconButton,
    Tooltip,
    Alert,
    CircularProgress,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
} from '@mui/material';
import {
    CloudDownload,
    Restore,
    Add,
    UploadFile,
    Refresh,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { backupsApi } from '@/services/api';
import { BackupInfo } from '@/types';

const BackupsPage: React.FC = () => {
    const queryClient = useQueryClient();
    const [restoreDialogOpen, setRestoreDialogOpen] = useState(false);
    const [selectedBackup, setSelectedBackup] = useState<string | null>(null);
    const [uploadError, setUploadError] = useState<string | null>(null);

    // Fetch backups
    const { data: backups, isLoading, error, refetch } = useQuery({
        queryKey: ['backups'],
        queryFn: backupsApi.list,
    });

    // Create backup mutation
    const createMutation = useMutation({
        mutationFn: backupsApi.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['backups'] });
        },
    });

    // Restore backup mutation
    const restoreMutation = useMutation({
        mutationFn: backupsApi.restore,
        onSuccess: () => {
            setRestoreDialogOpen(false);
            setSelectedBackup(null);
            alert('Backup restored successfully!');
        },
    });

    // Upload backup mutation
    const uploadMutation = useMutation({
        mutationFn: backupsApi.upload,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['backups'] });
            // Ask to restore the uploaded file
            setSelectedBackup(data.filename);
            setRestoreDialogOpen(true);
        },
        onError: (error: any) => {
            setUploadError(error.response?.data?.detail || 'Upload failed');
        },
    });

    const handleCreateBackup = () => {
        createMutation.mutate();
    };

    const handleRestoreClick = (filename: string) => {
        setSelectedBackup(filename);
        setRestoreDialogOpen(true);
    };

    const handleConfirmRestore = () => {
        if (selectedBackup) {
            restoreMutation.mutate(selectedBackup);
        }
    };

    const handleDownload = async (filename: string) => {
        try {
            const blob = await backupsApi.download(filename);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download failed', error);
        }
    };

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setUploadError(null);
            uploadMutation.mutate(file);
        }
    };

    const formatSize = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString();
    };

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h4">Backups</Typography>
                <Box>
                    <input
                        accept=".tar.gz"
                        style={{ display: 'none' }}
                        id="raised-button-file"
                        type="file"
                        onChange={handleFileUpload}
                    />
                    <label htmlFor="raised-button-file">
                        <Button
                            variant="outlined"
                            component="span"
                            startIcon={<UploadFile />}
                            sx={{ mr: 2 }}
                            disabled={uploadMutation.isPending}
                        >
                            Upload & Restore
                        </Button>
                    </label>
                    <Button
                        variant="contained"
                        startIcon={<Add />}
                        onClick={handleCreateBackup}
                        disabled={createMutation.isPending}
                    >
                        Create Backup
                    </Button>
                </Box>
            </Box>

            {uploadError && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setUploadError(null)}>
                    {uploadError}
                </Alert>
            )}

            {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                    Error loading backups: {(error as Error).message}
                </Alert>
            )}

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Filename</TableCell>
                            <TableCell>Size</TableCell>
                            <TableCell>Created At</TableCell>
                            <TableCell align="right">
                                <IconButton size="small" onClick={() => refetch()}>
                                    <Refresh />
                                </IconButton>
                            </TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {isLoading ? (
                            <TableRow>
                                <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                                    <CircularProgress />
                                </TableCell>
                            </TableRow>
                        ) : backups?.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={4} align="center" sx={{ py: 3 }}>
                                    No backups found
                                </TableCell>
                            </TableRow>
                        ) : (
                            backups?.map((backup) => (
                                <TableRow key={backup.filename}>
                                    <TableCell>{backup.filename}</TableCell>
                                    <TableCell>{formatSize(backup.size)}</TableCell>
                                    <TableCell>{formatDate(backup.created_at)}</TableCell>
                                    <TableCell align="right">
                                        <Tooltip title="Download">
                                            <IconButton onClick={() => handleDownload(backup.filename)}>
                                                <CloudDownload />
                                            </IconButton>
                                        </Tooltip>
                                        <Tooltip title="Restore">
                                            <IconButton
                                                color="warning"
                                                onClick={() => handleRestoreClick(backup.filename)}
                                            >
                                                <Restore />
                                            </IconButton>
                                        </Tooltip>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </TableContainer>

            {/* Restore Confirmation Dialog */}
            <Dialog
                open={restoreDialogOpen}
                onClose={() => setRestoreDialogOpen(false)}
            >
                <DialogTitle>Confirm Restore</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to restore from <strong>{selectedBackup}</strong>?
                        <br /><br />
                        <span style={{ color: 'red', fontWeight: 'bold' }}>WARNING:</span> This will overwrite your current database and credentials. This action cannot be undone.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setRestoreDialogOpen(false)}>Cancel</Button>
                    <Button
                        onClick={handleConfirmRestore}
                        color="error"
                        variant="contained"
                        disabled={restoreMutation.isPending}
                    >
                        {restoreMutation.isPending ? 'Restoring...' : 'Restore'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default BackupsPage;
