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

// Gemini Model types
export interface GeminiModel {
  id: string;
  name: string;
  description: string;
  recommended: boolean;
}

export interface AvailableModels {
  models: GeminiModel[];
  default_model: string;
}

// Project types (Multi-project support)
export interface Project {
  id: number;
  name: string;
  description?: string;
  model_name?: string;  // Modelo específico del proyecto (null = usar default global)
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  has_api_key: boolean;
}

export interface ProjectCreate {
  name: string;
  api_key: string;
  description?: string;
  model_name?: string;  // Modelo a usar (null = default global)
}

export interface ProjectUpdate {
  name?: string;
  api_key?: string;
  description?: string;
  model_name?: string;  // Modelo a usar (null = default global)
}

export interface ProjectList {
  projects: Project[];
  active_project_id?: number;
}

// MCP and CLI Integration types
export interface MCPConfig {
  backend_url: string;
  enabled: boolean;
  last_updated?: string;
}

export interface MCPConfigUpdate {
  backend_url?: string;
  enabled?: boolean;
}

export interface CLIConfig {
  backend_url: string;
  default_store_id?: string;
  last_updated?: string;
}

export interface CLIConfigUpdate {
  backend_url?: string;
  default_store_id?: string;
}

export interface MCPStatus {
  configured: boolean;
  backend_url: string;
  enabled: boolean;
  example_commands: {
    gemini_cli: {
      description: string;
      config: Record<string, any>;
    };
    claude_code: {
      description: string;
      command: string;
      config: Record<string, any>;
    };
    codex_cli: {
      description: string;
      command: string;
      config: Record<string, any>;
    };
  };
}

export interface CLIStatus {
  configured: boolean;
  backend_url: string;
  default_store_id?: string;
  executable_path: string;
  example_commands: string[];
}

export interface IntegrationGuide {
  gemini_cli: {
    title: string;
    description: string;
    steps: string[];
    config: Record<string, any>;
    documentation: string;
  };
  claude_code: {
    title: string;
    description: string;
    steps: string[];
    command: string;
    config: Record<string, any>;
    documentation: string;
  };
  codex_cli: {
    title: string;
    description: string;
    steps: string[];
    command: string;
    config: Record<string, any>;
    documentation: string;
  };
  cli_local: {
    title: string;
    description: string;
    steps: string[];
    executable: string;
    examples: string[];
    documentation: string;
  };
}
