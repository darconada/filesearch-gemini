/**
 * Type definitions for the application
 */

// Config types
export interface ConfigStatus {
  configured: boolean;
  api_key_valid: boolean;
  error_message?: string;
  model_available?: string;
}

// Store types
export interface Store {
  name: string;
  display_name: string;
  create_time?: string;
  update_time?: string;
}

export interface StoreCreate {
  display_name: string;
}

// Document types
export interface Document {
  name: string;
  display_name: string;
  custom_metadata: Record<string, any>;
  create_time?: string;
  update_time?: string;
  state?: string;
}

export interface DocumentUpload {
  file: File;
  display_name?: string;
  metadata?: Record<string, any>;
  max_tokens_per_chunk?: number;
  max_overlap_tokens?: number;
}

// Query types
export interface QueryRequest {
  question: string;
  store_ids: string[];
  metadata_filter?: string;
}

export interface DocumentSource {
  document_display_name?: string;
  document_id?: string;
  metadata: Record<string, any>;
  chunk_text?: string;
  relevance_score?: number;
}

export interface QueryResponse {
  answer: string;
  sources: DocumentSource[];
  model_used?: string;
}

// Drive link types
export enum SyncMode {
  MANUAL = 'manual',
  AUTO = 'auto',
}

export interface DriveLink {
  id: string;
  drive_file_id: string;
  store_id: string;
  document_id?: string;
  sync_mode: SyncMode;
  sync_interval_minutes?: number;
  last_synced_at?: string;
  drive_last_modified_at?: string;
  status: string;
  error_message?: string;
}

export interface DriveLinkCreate {
  drive_file_id: string;
  store_id: string;
  sync_mode: SyncMode;
  sync_interval_minutes?: number;
}
