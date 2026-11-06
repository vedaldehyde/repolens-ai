import { apiClient } from './api';
import { HealthStatusResponse } from '../types';

export async function fetchHealthStatus(): Promise<HealthStatusResponse> {
  const response = await apiClient.get<HealthStatusResponse>('/health');
  return response.data;
}
