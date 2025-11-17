/**
 * Project selector component for the header
 */
import React, { useState, useEffect } from 'react';
import {
  FormControl,
  Select,
  MenuItem,
  CircularProgress,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import { Folder as FolderIcon } from '@mui/icons-material';
import { projectsApi } from '@/services/api';
import type { Project } from '@/types';

export default function ProjectSelector() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activeProjectId, setActiveProjectId] = useState<number | undefined>();
  const [loading, setLoading] = useState(true);
  const [switching, setSwitching] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const data = await projectsApi.list();
      setProjects(data.projects);
      setActiveProjectId(data.active_project_id);
    } catch (err) {
      console.error('Error loading projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectChange = async (projectId: number) => {
    if (projectId === activeProjectId) return;

    try {
      setSwitching(true);
      await projectsApi.activate(projectId);
      setActiveProjectId(projectId);
      // Reload the page to refresh all data with the new active project
      window.location.reload();
    } catch (err) {
      console.error('Error switching project:', err);
      setSwitching(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
        <CircularProgress size={20} color="inherit" />
      </Box>
    );
  }

  if (projects.length === 0) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
        <Typography variant="body2" color="inherit">
          No projects
        </Typography>
      </Box>
    );
  }

  const activeProject = projects.find((p) => p.id === activeProjectId);

  return (
    <FormControl
      size="small"
      sx={{
        mr: 2,
        minWidth: 200,
        '& .MuiOutlinedInput-root': {
          color: 'inherit',
          '& fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.3)',
          },
          '&:hover fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.5)',
          },
          '&.Mui-focused fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.7)',
          },
        },
        '& .MuiSvgIcon-root': {
          color: 'inherit',
        },
      }}
    >
      <Select
        value={activeProjectId || ''}
        onChange={(e) => handleProjectChange(Number(e.target.value))}
        disabled={switching}
        displayEmpty
        renderValue={(value) => {
          if (!value || !activeProject) {
            return (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FolderIcon fontSize="small" />
                <Typography variant="body2">Select Project</Typography>
              </Box>
            );
          }
          return (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <FolderIcon fontSize="small" />
              <Typography variant="body2">{activeProject.name}</Typography>
            </Box>
          );
        }}
      >
        {projects.map((project) => (
          <MenuItem key={project.id} value={project.id}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
              <Typography variant="body2">{project.name}</Typography>
              {project.id === activeProjectId && (
                <Chip label="Active" size="small" color="primary" />
              )}
            </Box>
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
