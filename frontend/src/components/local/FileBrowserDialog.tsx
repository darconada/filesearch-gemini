/**
 * File browser component for selecting server files
 */
import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    IconButton,
    TextField,
    CircularProgress,
    Alert,
    Box,
    Typography,
    Breadcrumbs,
    Link,
} from '@mui/material';
import {
    Folder,
    InsertDriveFile,
    Home,
    ArrowUpward,
    Refresh,
} from '@mui/icons-material';
import { fileBrowserApi } from '@/services/api';
import type { DirectoryListing, FileSystemItem } from '@/types';

interface FileBrowserDialogProps {
    open: boolean;
    onClose: () => void;
    onSelect: (filePath: string) => void;
    title?: string;
}

const FileBrowserDialog: React.FC<FileBrowserDialogProps> = ({
    open,
    onClose,
    onSelect,
    title = 'Select File',
}) => {
    const [listing, setListing] = useState<DirectoryListing | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedPath, setSelectedPath] = useState<string | null>(null);

    useEffect(() => {
        if (open) {
            loadDirectory();
        }
    }, [open]);

    const loadDirectory = async (path?: string) => {
        setLoading(true);
        setError(null);
        try {
            const data = await fileBrowserApi.listDirectory(path);
            setListing(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Error loading directory');
        } finally {
            setLoading(false);
        }
    };

    const handleItemClick = (item: FileSystemItem) => {
        if (item.is_directory) {
            loadDirectory(item.path);
            setSelectedPath(null);
        } else {
            setSelectedPath(item.path);
        }
    };

    const handleParentClick = () => {
        if (listing?.parent_path) {
            loadDirectory(listing.parent_path);
            setSelectedPath(null);
        }
    };

    const handleHomeClick = () => {
        loadDirectory();
        setSelectedPath(null);
    };

    const handleRefresh = () => {
        if (listing) {
            loadDirectory(listing.current_path);
        }
    };

    const handleConfirm = () => {
        if (selectedPath) {
            onSelect(selectedPath);
            onClose();
        }
    };

    const formatFileSize = (bytes?: number) => {
        if (!bytes) return '';
        const kb = bytes / 1024;
        if (kb < 1024) return `${kb.toFixed(1)} KB`;
        return `${(kb / 1024).toFixed(1)} MB`;
    };

    const getBreadcrumbs = () => {
        if (!listing) return [];
        const parts = listing.current_path.split('/').filter(Boolean);
        const breadcrumbs = [{ name: 'Home', path: '/' }];

        let currentPath = '';
        for (const part of parts) {
            currentPath += '/' + part;
            breadcrumbs.push({ name: part, path: currentPath });
        }

        return breadcrumbs;
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="h6">{title}</Typography>
                    <Box>
                        <IconButton onClick={handleHomeClick} size="small" title="Home">
                            <Home />
                        </IconButton>
                        <IconButton onClick={handleRefresh} size="small" title="Refresh">
                            <Refresh />
                        </IconButton>
                    </Box>
                </Box>
            </DialogTitle>

            <DialogContent dividers>
                {/* Breadcrumbs */}
                {listing && (
                    <Breadcrumbs sx={{ mb: 2 }}>
                        {getBreadcrumbs().map((crumb, idx) => (
                            <Link
                                key={idx}
                                underline="hover"
                                color={idx === getBreadcrumbs().length - 1 ? 'text.primary' : 'inherit'}
                                onClick={() => loadDirectory(crumb.path)}
                                sx={{ cursor: 'pointer' }}
                            >
                                {crumb.name}
                            </Link>
                        ))}
                    </Breadcrumbs>
                )}

                {/* Error */}
                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                {/* Loading */}
                {loading ? (
                    <Box display="flex" justifyContent="center" p={4}>
                        <CircularProgress />
                    </Box>
                ) : listing ? (
                    <>
                        {/* Parent directory button */}
                        {listing.parent_path && (
                            <ListItem disablePadding>
                                <ListItemButton onClick={handleParentClick}>
                                    <ListItemIcon>
                                        <ArrowUpward />
                                    </ListItemIcon>
                                    <ListItemText primary=".." secondary="Parent directory" />
                                </ListItemButton>
                            </ListItem>
                        )}

                        {/* Directory listing */}
                        <List>
                            {listing.items.map((item, idx) => (
                                <ListItem
                                    key={idx}
                                    disablePadding
                                    secondaryAction={
                                        !item.is_directory && (
                                            <Typography variant="caption" color="text.secondary">
                                                {formatFileSize(item.size)}
                                            </Typography>
                                        )
                                    }
                                >
                                    <ListItemButton
                                        onClick={() => handleItemClick(item)}
                                        selected={selectedPath === item.path}
                                        disabled={!item.is_readable}
                                    >
                                        <ListItemIcon>
                                            {item.is_directory ? <Folder color="primary" /> : <InsertDriveFile />}
                                        </ListItemIcon>
                                        <ListItemText
                                            primary={item.name}
                                            secondary={!item.is_readable ? 'No permission' : undefined}
                                        />
                                    </ListItemButton>
                                </ListItem>
                            ))}
                        </List>

                        {listing.items.length === 0 && (
                            <Typography color="text.secondary" align="center" sx={{ py: 4 }}>
                                Empty directory
                            </Typography>
                        )}
                    </>
                ) : null}

                {/* Selected file path */}
                {selectedPath && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                            Selected:
                        </Typography>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace', wordBreak: 'break-all' }}>
                            {selectedPath}
                        </Typography>
                    </Box>
                )}
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>Cancel</Button>
                <Button onClick={handleConfirm} variant="contained" disabled={!selectedPath}>
                    Select
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default FileBrowserDialog;
