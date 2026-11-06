import axios, { AxiosError } from 'axios';
import { ApiError } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: ApiError; message?: string }>) => {
    let normalizedError: ApiError = {
      code: 'NETWORK_ERROR',
      message: 'Failed to connect to RepoLens backend. Ensure the FastAPI server is running.',
    };

    if (error.response?.data?.error) {
      normalizedError = error.response.data.error;
    } else if (error.response?.data?.message) {
      normalizedError = {
        code: `HTTP_${error.response.status}`,
        message: error.response.data.message,
      };
    } else if (error.message) {
      normalizedError.message = error.message;
    }

    return Promise.reject(normalizedError);
  }
);
