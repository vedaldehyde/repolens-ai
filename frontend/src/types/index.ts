export interface HealthStorageDetails {
  repos_dir_exists: boolean;
  chroma_dir_exists: boolean;
}

export interface HealthDetails {
  storage: HealthStorageDetails;
  environment: string;
  debug: boolean;
}

export interface HealthStatusResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  environment: string;
  uptime_seconds: number;
  details: HealthDetails;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data?: T;
  error?: ApiError;
}

export interface NavigationItem {
  label: string;
  path: string;
  icon: string;
  badge?: string;
}

export interface DiscoveredFile {
  path: string;
  size_bytes: number;
  extension: string;
  language: string;
  category: 'code' | 'documentation' | 'configuration';
}

export interface RepositoryMetadata {
  id: string;
  name: string;
  owner: string;
  github_url: string;
  commit_sha: string;
  branch?: string | null;
  file_count: number;
  total_size_bytes: number;
  detected_languages: string[];
  has_readme: boolean;
  readme_path?: string | null;
  ingested_at: string;
  status: 'completed' | 'processing' | 'failed';
}

export interface RepositoryFilesResponse {
  repository_id: string;
  file_count: number;
  files: DiscoveredFile[];
}

export interface RepositorySubmitPayload {
  github_url: string;
  branch?: string;
}
