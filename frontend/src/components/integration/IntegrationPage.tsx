/**
 * Integration page for MCP Server and CLI configuration
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Cable as IntegrationIcon } from '@mui/icons-material';
import MCPServerConfig from './MCPServerConfig';
import CLIConfig from './CLIConfig';
import IntegrationGuideView from './IntegrationGuide';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`integration-tabpanel-${index}`}
      aria-labelledby={`integration-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

export default function IntegrationPage() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <IntegrationIcon fontSize="large" color="primary" />
          <Typography variant="h4" component="h1">
            LLM Agent Integration
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Configure File Search for use with Gemini CLI, Claude Code, Codex, and local CLI
        </Typography>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        This section allows you to configure the MCP Server and CLI tool to integrate File Search with LLM agents.
        For complete documentation, see <strong>MCP_INTEGRATION.md</strong> in the repository.
      </Alert>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="integration tabs"
          variant="fullWidth"
        >
          <Tab label="MCP Server" id="integration-tab-0" />
          <Tab label="CLI Local" id="integration-tab-1" />
          <Tab label="Integration Guide" id="integration-tab-2" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <MCPServerConfig />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <CLIConfig />
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <IntegrationGuideView />
        </TabPanel>
      </Paper>
    </Container>
  );
}
