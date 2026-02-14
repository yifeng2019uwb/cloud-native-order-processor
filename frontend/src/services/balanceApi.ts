import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_URLS } from '@/constants';
import type {
  DepositRequest,
  WithdrawRequest,
  BalanceTransactionListRequest,
  BalanceResponse,
  BalanceTransactionResponse,
  BalanceApiError
} from '@/types';

class BalanceApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URLS.BALANCE,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - Add JWT token to requests
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

    // Response interceptor - Handle errors and token expiration
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('auth_token');
          window.location.href = '/auth';
        }
        return Promise.reject(this.formatError(error));
      }
    );
  }

  /** Strip exception class prefix from backend error (e.g. CNOPDailyLimitExceededException: ) */
  private stripExceptionPrefix(msg: string): string {
    return msg.replace(/^[A-Za-z0-9_]+Exception:\s*/i, '').trim();
  }

  /** Convert Pydantic validation errors to user-friendly messages */
  private formatValidationDetail(detail: unknown): string {
    if (Array.isArray(detail)) {
      const messages = detail.map((e: { type?: string; loc?: string[]; msg?: string; ctx?: { le?: number; gt?: number } }) => {
        const loc = e.loc?.join('.') ?? '';
        const isAmount = loc.includes('amount');
        if (e.type === 'less_than_equal' && isAmount && e.ctx?.le != null) {
          return `Amount must be at most $${e.ctx.le.toLocaleString()}`;
        }
        if ((e.type === 'greater_than' || e.type === 'greater_than_equal') && isAmount && e.ctx?.gt != null) {
          return `Amount must be at least $${e.ctx.gt}`;
        }
        if (e.msg) return e.msg;
        return String(e);
      });
      return messages.join('. ');
    }
    return String(detail);
  }

  private formatError(error: AxiosError): BalanceApiError {
    if (error.response?.data) {
      const responseData = error.response.data as any;

      // Handle FastAPI HTTPException format: detail as string (e.g. daily limit exceeded)
      if (responseData.detail && typeof responseData.detail === 'string') {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: this.stripExceptionPrefix(responseData.detail),
          timestamp: new Date().toISOString()
        };
      }

      // Handle FastAPI/Pydantic validation: detail as array of validation errors
      if (responseData.detail && Array.isArray(responseData.detail)) {
        return {
          success: false,
          error: 'VALIDATION_ERROR',
          message: this.formatValidationDetail(responseData.detail),
          timestamp: new Date().toISOString()
        };
      }

      // Handle FastAPI HTTPException format: detail as object
      if (responseData.detail && typeof responseData.detail === 'object') {
        const rawMsg = responseData.detail.message || JSON.stringify(responseData.detail);
        return { ...responseData.detail, message: this.stripExceptionPrefix(rawMsg) };
      }

      // Handle direct error response format
      if (responseData.success === false) {
        return responseData as BalanceApiError;
      }

      // Fallback to direct data
      return responseData as BalanceApiError;
    }

    return {
      success: false,
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString()
    };
  }

  // Balance API methods
  async getBalance(): Promise<BalanceResponse> {
    const response = await this.api.get<BalanceResponse>('');
    return response.data;
  }

  async deposit(depositData: DepositRequest): Promise<{success: boolean, message: string, transaction_id: string, timestamp: string}> {
    const response = await this.api.post<{success: boolean, message: string, transaction_id: string, timestamp: string}>('/deposit', depositData);
    return response.data;
  }

  async withdraw(withdrawData: WithdrawRequest): Promise<{success: boolean, message: string, transaction_id: string, timestamp: string}> {
    const response = await this.api.post<{success: boolean, message: string, transaction_id: string, timestamp: string}>('/withdraw', withdrawData);
    return response.data;
  }

  async getTransactions(params?: BalanceTransactionListRequest): Promise<BalanceTransactionResponse> {
    const queryParams = new URLSearchParams();

    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }

    if (params?.offset) {
      queryParams.append('offset', params.offset.toString());
    }

    if (params?.transaction_type) {
      queryParams.append('transaction_type', params.transaction_type);
    }

    const url = `/transactions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await this.api.get<BalanceTransactionResponse>(url);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/health');
    return response.data;
  }
}

// Export singleton instance
export const balanceApiService = new BalanceApiService();
export default balanceApiService;
