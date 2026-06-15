import { request } from './request';

export function listContracts() {
  return request.get('/api/v1/contracts');
}

export function getContract(contractId: string) {
  return request.get(`/api/v1/contracts/${contractId}`);
}
