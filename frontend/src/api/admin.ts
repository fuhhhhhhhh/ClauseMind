import { request } from './request';

export function getAdminStatistics() {
  return request.get('/api/v1/admin/statistics');
}
