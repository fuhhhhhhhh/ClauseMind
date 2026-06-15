import type { ApiResponse } from './request';
import { request } from './request';

import type { UserInfo } from '../types';

export function login(payload: { username: string; password: string }) {
  return request.post<
    ApiResponse<{ user: UserInfo; access_token: string; token_type: string }>
  >('/api/v1/auth/login', payload);
}

export function register(payload: { username: string; email?: string; password: string }) {
  return request.post<
    ApiResponse<{ user: UserInfo; access_token: string; token_type: string }>
  >('/api/v1/auth/register', payload);
}

export function me() {
  return request.get<ApiResponse<UserInfo>>('/api/v1/auth/me');
}
