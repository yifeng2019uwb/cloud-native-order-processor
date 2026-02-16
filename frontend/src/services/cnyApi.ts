import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_URLS } from '@/constants';
import type { CnyClaimRequest, CnyClaimResponse } from '@/types';

class CnyApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URLS.CNY,
      headers: { 'Content-Type': 'application/json' },
      timeout: 10000,
    });

    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('auth_token');
          window.location.href = '/auth';
        }
        return Promise.reject(error);
      }
    );
  }

  async claim(data: CnyClaimRequest): Promise<CnyClaimResponse> {
    const response = await this.api.post<CnyClaimResponse>('/claim', data);
    return response.data;
  }
}

export const cnyApiService = new CnyApiService();
