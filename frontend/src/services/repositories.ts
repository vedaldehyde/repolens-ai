import { apiClient } from './api';
import {
  RepositoryFilesResponse,
  RepositoryMetadata,
  RepositorySubmitPayload,
} from '../types';

export async function ingestRepository(
  payload: RepositorySubmitPayload
): Promise<RepositoryMetadata> {
  const response = await apiClient.post<RepositoryMetadata>('/repositories', payload);
  return response.data;
}

export async function fetchRepositories(): Promise<RepositoryMetadata[]> {
  const response = await apiClient.get<RepositoryMetadata[]>('/repositories');
  return response.data;
}

export async function fetchRepository(
  repositoryId: string
): Promise<RepositoryMetadata> {
  const response = await apiClient.get<RepositoryMetadata>(`/repositories/${encodeURIComponent(repositoryId)}`);
  return response.data;
}

export async function fetchRepositoryFiles(
  repositoryId: string
): Promise<RepositoryFilesResponse> {
  const response = await apiClient.get<RepositoryFilesResponse>(
    `/repositories/${encodeURIComponent(repositoryId)}/files`
  );
  return response.data;
}
