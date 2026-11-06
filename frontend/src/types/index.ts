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
