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
};

// Stores API
export const storesApi = {
  list: async (pageSize = 50, pageToken?: string): Promise<{ stores: Store[]; next_page_token?: string }> => {
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
    const response = await api.get(`/stores/${storeId}`);
    return response.data;
  },

  delete: async (storeId: string) => {
    const response = await api.delete(`/stores/${storeId}`);
    return response.data;
  },
};

// Documents API
export const documentsApi = {
  list: async (
    storeId: string,
    pageSize = 50,
    pageToken?: string
  ): Promise<{ documents: Document[]; next_page_token?: string }> => {
    const params: any = { page_size: pageSize };
    if (pageToken) params.page_token = pageToken;
    const response = await api.get(`/stores/${storeId}/documents`, { params });
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

    const response = await api.post(`/stores/${storeId}/documents`, formData, {
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

    const response = await api.put(`/stores/${storeId}/documents/${documentId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  delete: async (storeId: string, documentId: string) => {
    const response = await api.delete(`/stores/${storeId}/documents/${documentId}`);
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

export default api;
