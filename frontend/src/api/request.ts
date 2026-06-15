import axios from 'axios';

export type ApiResponse<T> = {
  code: number;
  message: string;
  data: T;
};

export const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '',
  timeout: 30000,
});

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('clausemind_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function getHealth() {
  const response = await request.get<ApiResponse<{ service: string; environment: string; status: string }>>(
    '/health',
  );
  return response.data;
}

export async function getPublicConfig() {
  const response = await request.get<
    ApiResponse<{
      app_name: string;
      app_env: string;
      database: string;
      llm_model: string;
      llm_api_base_configured: boolean;
      mineru_backend: string;
      cors_origins: string[];
    }>
  >('/api/v1/system/config');
  return response.data;
}
