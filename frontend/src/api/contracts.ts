import type { ApiResponse } from './request';
import { request } from './request';

import type { ContractDetail, ContractListItem } from '../types';

export function listContracts() {
  return request.get<ApiResponse<{ items: ContractListItem[]; total: number }>>('/api/v1/contracts');
}

export function getContract(contractId: number | string) {
  return request.get<ApiResponse<ContractDetail>>(`/api/v1/contracts/${contractId}`);
}

export function uploadContract(file: File, contractType?: string) {
  const formData = new FormData();
  formData.append('file', file);
  if (contractType) {
    formData.append('contract_type', contractType);
  }
  return request.post<ApiResponse<ContractDetail>>('/api/v1/contracts/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
}

export function deleteContract(contractId: number | string) {
  return request.delete<ApiResponse<null>>(`/api/v1/contracts/${contractId}`);
}
