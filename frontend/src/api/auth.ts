import { request } from './request';

export function login(payload: { username: string; password: string }) {
  return request.post('/api/v1/auth/login', payload);
}

export function register(payload: { username: string; email?: string; password: string }) {
  return request.post('/api/v1/auth/register', payload);
}
