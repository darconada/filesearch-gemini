/**
 * Projects management page
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
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
  Alert,
  CircularProgress,
  Chip,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CheckCircle as ActiveIcon,
  RadioButtonUnchecked as InactiveIcon,
} from '@mui/icons-material';
import { projectsApi, configApi } from '@/services/api';
import type { Project, ProjectCreate, ProjectUpdate, GeminiModel, AvailableModels } from '@/types';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProjectId, setActiveProjectId] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  // Form states
  const [formName, setFormName] = useState('');
  const [formApiKey, setFormApiKey] = useState('');
  const [formDescription, setFormDescription] = useState('');
  const [formModelName, setFormModelName] = useState<string>('');
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  // Available models
  const [availableModels, setAvailableModels] = useState<GeminiModel[]>([]);
  const [defaultModel, setDefaultModel] = useState<string>('');

  useEffect(() => {
    loadProjects();
    loadModels();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectsApi.list();
      setProjects(data.projects);
      setActiveProjectId(data.active_project_id);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error loading projects');
    } finally {
      setLoading(false);
    }
  };

  const loadModels = async () => {
    try {
      const data = await configApi.getModels();
      setAvailableModels(data.models);
      setDefaultModel(data.default_model);
    } catch (err: any) {
      console.error('Error loading models:', err);
      // Non-critical error, don't show to user
    }
  };

  const handleOpenCreateDialog = () => {
    setFormName('');
    setFormApiKey('');
    setFormDescription('');
    setFormModelName('');
    setFormErrors({});
    setCreateDialogOpen(true);
  };

  const handleOpenEditDialog = (project: Project) => {
    setSelectedProject(project);
    setFormName(project.name);
    setFormApiKey('');
    setFormDescription(project.description || '');
    setFormModelName(project.model_name || '');
    setFormErrors({});
    setEditDialogOpen(true);
  };

  const handleOpenDeleteDialog = (project: Project) => {
    setSelectedProject(project);
    setDeleteDialogOpen(true);
  };

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formName.trim()) {
      errors.name = 'Project name is required';
    }

    if (createDialogOpen && !formApiKey.trim()) {
      errors.apiKey = 'API key is required when creating a project';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleCreate = async () => {
    if (!validateForm()) return;

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      const data: ProjectCreate = {
        name: formName.trim(),
        api_key: formApiKey.trim(),
        description: formDescription.trim() || undefined,
        model_name: formModelName || undefined,
      };

      await projectsApi.create(data);
      setSuccess('Project created successfully!');
      setCreateDialogOpen(false);
      loadProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error creating project');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async () => {
    if (!selectedProject || !validateForm()) return;

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);

      const data: ProjectUpdate = {
        name: formName.trim() !== selectedProject.name ? formName.trim() : undefined,
        api_key: formApiKey.trim() || undefined,
        description: formDescription.trim() || undefined,
        model_name: formModelName !== selectedProject.model_name ? formModelName || undefined : undefined,
      };

      await projectsApi.update(selectedProject.id, data);
      setSuccess('Project updated successfully!');
      setEditDialogOpen(false);
      loadProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error updating project');
    } finally {
      setSubmitting(false);
    }
  };

  const handleActivate = async (projectId: number) => {
    try {
      setError(null);
      setSuccess(null);
      await projectsApi.activate(projectId);
      setSuccess('Project activated successfully!');
      loadProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error activating project');
    }
  };

  const handleDelete = async () => {
    if (!selectedProject) return;

    try {
      setSubmitting(true);
      setError(null);
      setSuccess(null);
      await projectsApi.delete(selectedProject.id);
      setSuccess('Project deleted successfully!');
      setDeleteDialogOpen(false);
      loadProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error deleting project');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4">Projects</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleOpenCreateDialog}
        >
          Create Project
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Google AI Studio Projects
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Manage multiple Google AI Studio projects. Each project can have up to 10 File Search stores.
            Only one project can be active at a time.
          </Typography>

          {projects.length === 0 ? (
            <Alert severity="info" sx={{ mt: 2 }}>
              No projects found. Create your first project to get started.
            </Alert>
          ) : (
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Status</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Model</TableCell>
                    <TableCell>API Key</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {projects.map((project) => (
                    <TableRow
                      key={project.id}
                      sx={{
                        backgroundColor: project.is_active ? 'action.selected' : 'inherit',
                      }}
                    >
                      <TableCell>
                        {project.is_active ? (
                          <Chip
                            icon={<ActiveIcon />}
                            label="Active"
                            color="success"
                            size="small"
                          />
                        ) : (
                          <Tooltip title="Click to activate">
                            <IconButton
                              size="small"
                              onClick={() => handleActivate(project.id)}
                            >
                              <InactiveIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={project.is_active ? 'bold' : 'normal'}>
                          {project.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {project.description || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {project.model_name || `Default (${defaultModel})`}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {project.has_api_key ? (
                          <Chip label="Configured" color="success" size="small" variant="outlined" />
                        ) : (
                          <Chip label="Not Set" color="error" size="small" variant="outlined" />
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(project.created_at).toLocaleDateString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Edit">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenEditDialog(project)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDeleteDialog(project)}
                            disabled={project.is_active && projects.length === 1}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Create Project Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Project</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Project Name"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              error={!!formErrors.name}
              helperText={formErrors.name || 'Unique name for this project'}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Google AI Studio API Key"
              type="password"
              value={formApiKey}
              onChange={(e) => setFormApiKey(e.target.value)}
              error={!!formErrors.apiKey}
              helperText={formErrors.apiKey || 'API key from Google AI Studio'}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description (optional)"
              multiline
              rows={3}
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              helperText="Brief description of this project"
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth>
              <InputLabel id="create-model-select-label">Gemini Model</InputLabel>
              <Select
                labelId="create-model-select-label"
                id="create-model-select"
                value={formModelName}
                label="Gemini Model"
                onChange={(e) => setFormModelName(e.target.value)}
              >
                <MenuItem value="">
                  <em>Default ({defaultModel})</em>
                </MenuItem>
                {availableModels.map((model) => (
                  <MenuItem key={model.id} value={model.id}>
                    {model.name} {model.recommended && '⭐'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained" disabled={submitting}>
            {submitting ? 'Creating...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Project Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Project</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Project Name"
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              error={!!formErrors.name}
              helperText={formErrors.name || 'Unique name for this project'}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Google AI Studio API Key"
              type="password"
              value={formApiKey}
              onChange={(e) => setFormApiKey(e.target.value)}
              helperText="Leave empty to keep current API key"
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description (optional)"
              multiline
              rows={3}
              value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              helperText="Brief description of this project"
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth>
              <InputLabel id="edit-model-select-label">Gemini Model</InputLabel>
              <Select
                labelId="edit-model-select-label"
                id="edit-model-select"
                value={formModelName}
                label="Gemini Model"
                onChange={(e) => setFormModelName(e.target.value)}
              >
                <MenuItem value="">
                  <em>Default ({defaultModel})</em>
                </MenuItem>
                {availableModels.map((model) => (
                  <MenuItem key={model.id} value={model.id}>
                    {model.name} {model.recommended && '⭐'}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpdate} variant="contained" disabled={submitting}>
            {submitting ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Delete Project</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the project "{selectedProject?.name}"?
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            This action cannot be undone. All stores and documents associated with this project's API key
            will remain in Google AI Studio but won't be accessible through this application.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained" disabled={submitting}>
            {submitting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
