/**
 * Main App component with routing and theme management
 */
import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import getTheme from '@/theme/theme';
import Layout from '@/components/common/Layout';
import ConfigPage from '@/components/config/ConfigPage';
import StoresPage from '@/components/stores/StoresPage';
import DocumentsPage from '@/components/documents/DocumentsPage';
import QueryPage from '@/components/query/QueryPage';
import DrivePage from '@/components/drive/DrivePage';
import DriveSetupPage from '@/components/drive/DriveSetupPage';
import LocalFilesPage from '@/components/local/LocalFilesPage';
import IntegrationPage from '@/components/integration/IntegrationPage';
import ProjectsPage from '@/components/projects/ProjectsPage';
import BackupsPage from '@/components/backups/BackupsPage';
import AuditLogsPage from '@/components/audit/AuditLogsPage';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  // Theme management
  const [mode, setMode] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('themeMode');
    return (saved as 'light' | 'dark') || 'light';
  });

  const theme = useMemo(() => getTheme(mode), [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => {
      const newMode = prevMode === 'light' ? 'dark' : 'light';
      localStorage.setItem('themeMode', newMode);
      return newMode;
    });
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Layout onToggleTheme={toggleTheme}>
            <Routes>
              <Route path="/" element={<Navigate to="/config" replace />} />
              <Route path="/config" element={<ConfigPage />} />
              <Route path="/projects" element={<ProjectsPage />} />
              <Route path="/stores" element={<StoresPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/query" element={<QueryPage />} />
              <Route path="/drive" element={<DrivePage />} />
              <Route path="/drive-setup" element={<DriveSetupPage />} />
              <Route path="/local-files" element={<LocalFilesPage />} />
              <Route path="/backups" element={<BackupsPage />} />
              <Route path="/audit-logs" element={<AuditLogsPage />} />
              <Route path="/integration" element={<IntegrationPage />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
