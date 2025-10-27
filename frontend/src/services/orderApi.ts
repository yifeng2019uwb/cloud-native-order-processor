import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_URLS, API_PATHS, buildQueryString } from '@/constants';
import type {
  Order,
  CreateOrderRequest,
  OrderListRequest,
  OrderListResponse,
  OrderDetailResponse,
  OrderApiError
} from '@/types';

class OrderApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URLS.ORDERS,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    // Debug logging to see what base URL is set
    console.log('🔍 Orders API Constructor Debug:');
    console.log('  - API_URLS.ORDERS:', API_URLS.ORDERS);
    console.log('  - this.api.defaults.baseURL:', this.api.defaults.baseURL);

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

  private formatError(error: AxiosError): OrderApiError {
    if (error.response?.data) {
      const responseData = error.response.data as any;

      // Handle FastAPI HTTPException format
      if (responseData.detail && typeof responseData.detail === 'object') {
        return responseData.detail as OrderApiError;
      }

      // Handle direct error response format
      if (responseData.success === false) {
        return responseData as OrderApiError;
      }

      // Fallback to direct data
      return responseData as OrderApiError;
    }

    return {
      success: false,
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString()
    };
  }

  // Order API methods
  async createOrder(orderData: CreateOrderRequest): Promise<Order> {
    // Backend returns { data: OrderData }
    const response = await this.api.post(API_PATHS.ORDERS, orderData);
    // Axios response has response.data as the JSON body
    return response.data.data;
  }

  async getOrder(orderId: string): Promise<OrderDetailResponse> {
    const response = await this.api.get<OrderDetailResponse>(API_PATHS.ORDER_BY_ID(orderId));
    return response.data;
  }

  async listOrders(params?: OrderListRequest): Promise<OrderListResponse> {
    const queryString = buildQueryString({
      limit: params?.limit?.toString(),
      offset: params?.offset?.toString(),
      status: params?.status,
      order_type: params?.order_type,
      asset_id: params?.asset_id
    });
    const url = `${API_PATHS.ORDERS}${queryString}`;
    const response = await this.api.get<OrderListResponse>(url);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/health');
    return response.data;
  }
}

// Export singleton instance
export const orderApiService = new OrderApiService();
export default orderApiService;
