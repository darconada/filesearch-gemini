/**
 * API client for File Search RAG backend
 */
import axios from 'axios';
import type {
  ConfigStatus,
  Store,
  StoreCreate,
  Document,
  QueryRequest,
  QueryResponse,
  DriveLink,
  DriveLinkCreate,
  MCPConfig,
  MCPConfigUpdate,
  MCPStatus,
  CLIConfig,
  CLIConfigUpdate,
  CLIStatus,
  IntegrationGuide,
  Project,
  ProjectCreate,
  ProjectUpdate,
  ProjectList,
  AvailableModels,
  DriveCredentialsStatus,
  LocalFileLink,
  LocalFileLinkCreate,
  LocalFileLinkList,
  FileReplaceResponse,
  FileVersionHistory,
  DirectoryListing,
  FileSystemItem,
  BackupInfo,
} from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Config API
export const configApi = {
  setApiKey: async (apiKey: string) => {
    const response = await api.post('/config/api-key', { api_key: apiKey });
    return response.data;
  },

  getStatus: async (): Promise<ConfigStatus> => {
    const response = await api.get('/config/status');
    return response.data;
  },

  getModels: async (): Promise<AvailableModels> => {
    const response = await api.get('/config/models');
    return response.data;
  },

  // Drive credentials
  setDriveCredentialsJSON: async (credentials_json: string) => {
    const response = await api.post('/config/drive-credentials/json', { credentials_json });
    return response.data;
  },

  setDriveCredentialsManual: async (client_id: string, client_secret: string, project_id?: string) => {
    const response = await api.post('/config/drive-credentials/manual', { client_id, client_secret, project_id });
    return response.data;
  },

  getDriveCredentialsStatus: async (): Promise<DriveCredentialsStatus> => {
    const response = await api.get('/config/drive-credentials/status');
    return response.data;
  },

  testDriveConnection: async () => {
    const response = await api.post('/config/drive-credentials/test');
    return response.data;
  },
};

// Stores API
export const storesApi = {
  list: async (pageSize = 20, pageToken?: string): Promise<{ stores: Store[]; next_page_token?: string }> => {
    const params: any = { page_size: pageSize };
    if (pageToken) params.page_token = pageToken;
    const response = await api.get('/stores', { params });
    return response.data;
  },

  create: async (data: StoreCreate): Promise<Store> => {
    const response = await api.post('/stores', data);
    return response.data;
  },

  get: async (storeId: string): Promise<Store> => {
    const response = await api.get(`/stores/${encodeURIComponent(storeId)}`);
    return response.data;
  },

  delete: async (storeId: string) => {
    const response = await api.delete(`/stores/${encodeURIComponent(storeId)}`);
    return response.data;
  },
};

// Helper function to extract store ID from full store name
const extractStoreId = (fullStoreId: string): string => {
  // fullStoreId format: "fileSearchStores/store-id"
  // We need just "store-id"
  if (fullStoreId.startsWith('fileSearchStores/')) {
    return fullStoreId.substring('fileSearchStores/'.length);
  }
  return fullStoreId;
};

// Helper function to extract document ID from full document name
const extractDocumentId = (fullDocumentId: string): string => {
  // fullDocumentId format: "fileSearchStores/store-id/documents/doc-id"
  // We need just "doc-id"
  const parts = fullDocumentId.split('/documents/');
  if (parts.length === 2) {
    return parts[1];
  }
  return fullDocumentId;
};

// Documents API
export const documentsApi = {
  list: async (
    storeId: string,
    pageSize = 20,
    pageToken?: string
  ): Promise<{ documents: Document[]; next_page_token?: string }> => {
    const params: any = { page_size: pageSize };
    if (pageToken) params.page_token = pageToken;
    // Extract just the store ID part
    const shortStoreId = extractStoreId(storeId);
    const response = await api.get(`/stores/fileSearchStores/${encodeURIComponent(shortStoreId)}/documents`, { params });
    return response.data;
  },

  upload: async (
    storeId: string,
    file: File,
    displayName?: string,
    metadata?: Record<string, any>,
    chunkingConfig?: { max_tokens_per_chunk?: number; max_overlap_tokens?: number }
  ): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    if (displayName) formData.append('display_name', displayName);
    if (metadata) formData.append('metadata', JSON.stringify(metadata));
    if (chunkingConfig?.max_tokens_per_chunk) {
      formData.append('max_tokens_per_chunk', chunkingConfig.max_tokens_per_chunk.toString());
    }
    if (chunkingConfig?.max_overlap_tokens) {
      formData.append('max_overlap_tokens', chunkingConfig.max_overlap_tokens.toString());
    }

    // Extract just the store ID part
    const shortStoreId = extractStoreId(storeId);
    const response = await api.post(`/stores/fileSearchStores/${encodeURIComponent(shortStoreId)}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  update: async (
    storeId: string,
    documentId: string,
    file: File,
    displayName?: string,
    metadata?: Record<string, any>
  ): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    if (displayName) formData.append('display_name', displayName);
    if (metadata) formData.append('metadata', JSON.stringify(metadata));

    // Extract just the store ID and document ID parts
    const shortStoreId = extractStoreId(storeId);
    const shortDocId = extractDocumentId(documentId);
    const response = await api.put(`/stores/fileSearchStores/${encodeURIComponent(shortStoreId)}/documents/${encodeURIComponent(shortDocId)}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  delete: async (storeId: string, documentId: string) => {
    // Extract just the store ID and document ID parts
    const shortStoreId = extractStoreId(storeId);
    const shortDocId = extractDocumentId(documentId);
    const response = await api.delete(`/stores/fileSearchStores/${encodeURIComponent(shortStoreId)}/documents/${encodeURIComponent(shortDocId)}`);
    return response.data;
  },
};

// Query API
export const queryApi = {
  execute: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await api.post('/query', request);
    return response.data;
  },
};

// Drive links API
export const driveApi = {
  list: async (): Promise<{ links: DriveLink[] }> => {
    const response = await api.get('/drive-links');
    return response.data;
  },

  create: async (data: DriveLinkCreate): Promise<DriveLink> => {
    const response = await api.post('/drive-links', data);
    return response.data;
  },

  get: async (linkId: string): Promise<DriveLink> => {
    const response = await api.get(`/drive-links/${linkId}`);
    return response.data;
  },

  delete: async (linkId: string) => {
    const response = await api.delete(`/drive-links/${linkId}`);
    return response.data;
  },

  sync: async (linkId: string, force = false): Promise<DriveLink> => {
    const response = await api.post(`/drive-links/${linkId}/sync-now`, { force });
    return response.data;
  },
};

// MCP Server API
export const mcpApi = {
  getConfig: async (): Promise<MCPConfig> => {
    const response = await api.get('/integration/mcp/config');
    return response.data;
  },

  updateConfig: async (data: MCPConfigUpdate): Promise<MCPConfig> => {
    const response = await api.post('/integration/mcp/config', data);
    return response.data;
  },

  getStatus: async (): Promise<MCPStatus> => {
    const response = await api.get('/integration/mcp/status');
    return response.data;
  },
};

// CLI API
export const cliApi = {
  getConfig: async (): Promise<CLIConfig> => {
    const response = await api.get('/integration/cli/config');
    return response.data;
  },

  updateConfig: async (data: CLIConfigUpdate): Promise<CLIConfig> => {
    const response = await api.post('/integration/cli/config', data);
    return response.data;
  },

  getStatus: async (): Promise<CLIStatus> => {
    const response = await api.get('/integration/cli/status');
    return response.data;
  },
};

// Integration Guide API
export const integrationApi = {
  getGuide: async (): Promise<IntegrationGuide> => {
    const response = await api.get('/integration/guide');
    return response.data;
  },
};

// Projects API
export const projectsApi = {
  list: async (): Promise<ProjectList> => {
    const response = await api.get('/projects');
    return response.data;
  },

  create: async (data: ProjectCreate): Promise<Project> => {
    const response = await api.post('/projects', data);
    return response.data;
  },

  get: async (projectId: number): Promise<Project> => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },

  getActive: async (): Promise<Project> => {
    const response = await api.get('/projects/active');
    return response.data;
  },

  update: async (projectId: number, data: ProjectUpdate): Promise<Project> => {
    const response = await api.put(`/projects/${projectId}`, data);
    return response.data;
  },

  activate: async (projectId: number): Promise<Project> => {
    const response = await api.post(`/projects/${projectId}/activate`);
    return response.data;
  },

  delete: async (projectId: number) => {
    const response = await api.delete(`/projects/${projectId}`);
    return response.data;
  },
};

// Local Files API
export const localFilesApi = {
  list: async (storeId?: string): Promise<LocalFileLinkList> => {
    const params = storeId ? { store_id: storeId } : {};
    const response = await api.get('/local-files/links', { params });
    return response.data;
  },

  create: async (data: LocalFileLinkCreate): Promise<LocalFileLink> => {
    const response = await api.post('/local-files/links', data);
    return response.data;
  },

  get: async (linkId: string): Promise<LocalFileLink> => {
    const response = await api.get(`/local-files/links/${linkId}`);
    return response.data;
  },

  delete: async (linkId: string, deleteFromStore = false) => {
    const response = await api.delete(`/local-files/links/${linkId}`, {
      params: { delete_from_store: deleteFromStore }
    });
    return response.data;
  },

  sync: async (linkId: string, force = false): Promise<LocalFileLink> => {
    const response = await api.post(`/local-files/links/${linkId}/sync`, { force });
    return response.data;
  },

  syncAll: async (storeId?: string): Promise<LocalFileLinkList> => {
    const params = storeId ? { store_id: storeId } : {};
    const response = await api.post('/local-files/sync-all', null, { params });
    return response.data;
  },
};

// File Updates API
export const fileUpdatesApi = {
  replace: async (linkId: string, file: File): Promise<FileReplaceResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post(`/file-updates/replace/${linkId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getHistory: async (linkId: string): Promise<FileVersionHistory> => {
    const response = await api.get(`/file-updates/history/${linkId}`);
    return response.data;
  },
};

// File Browser API
export const fileBrowserApi = {
  listDirectory: async (path?: string): Promise<DirectoryListing> => {
    const params = path ? { path } : {};
    const response = await api.get('/file-browser/list', { params });
    return response.data;
  },

  getFileInfo: async (path: string): Promise<FileSystemItem> => {
    const response = await api.get('/file-browser/file-info', { params: { path } });
    return response.data;
  },
};

// Backups API
export const backupsApi = {
  list: async (): Promise<BackupInfo[]> => {
    const response = await api.get('/backups');
    return response.data;
  },

  create: async (): Promise<BackupInfo> => {
    const response = await api.post('/backups');
    return response.data;
  },

  restore: async (filename: string): Promise<{ message: string }> => {
    const response = await api.post(`/backups/${filename}/restore`);
    return response.data;
  },

  download: async (filename: string): Promise<Blob> => {
    const response = await api.get(`/backups/${filename}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  upload: async (file: File): Promise<{ message: string; filename: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/backups/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};

export default api;
