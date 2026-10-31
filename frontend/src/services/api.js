import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
});

// Request Interceptor: Attach JWT Bearer Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('banksense_access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle Token Refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry &&
      !originalRequest.url.includes('/token/') &&
      !originalRequest.url.includes('/auth/login/')
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('banksense_refresh_token');
      if (refreshToken) {
        try {
          const res = await axios.post('/api/token/refresh/', { refresh: refreshToken });
          const newAccess = res.data.access;
          localStorage.setItem('banksense_access_token', newAccess);
          originalRequest.headers['Authorization'] = `Bearer ${newAccess}`;
          return api(originalRequest);
        } catch (refreshErr) {
          localStorage.removeItem('banksense_access_token');
          localStorage.removeItem('banksense_refresh_token');
          localStorage.removeItem('banksense_user');
          window.dispatchEvent(new Event('banksense_auth_logout'));
        }
      } else {
        localStorage.removeItem('banksense_access_token');
        localStorage.removeItem('banksense_refresh_token');
        localStorage.removeItem('banksense_user');
        window.dispatchEvent(new Event('banksense_auth_logout'));
      }
    }
    return Promise.reject(error);
  }
);

// API Service Endpoints
export const authService = {
  register: (data) => api.post('/auth/register/', data),
  login: (credentials) => api.post('/token/', credentials),
  getProfile: () => api.get('/auth/me/'),
  updateProfile: (data) => api.patch('/auth/me/', data),
  logout: () => {
    localStorage.removeItem('banksense_access_token');
    localStorage.removeItem('banksense_refresh_token');
    localStorage.removeItem('banksense_user');
    window.dispatchEvent(new Event('banksense_auth_logout'));
  },
};

export const accountService = {
  list: () => api.get('/accounts/'),
  create: (data) => api.post('/accounts/', data),
  update: (id, data) => api.patch(`/accounts/${id}/`, data),
  delete: (id) => api.delete(`/accounts/${id}/`),
  recalculate: (id) => api.post(`/accounts/${id}/recalculate/`),
};

export const statementService = {
  list: () => api.get('/statements/'),
  get: (id) => api.get(`/statements/${id}/`),
  upload: (formData) =>
    api.post('/statements/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  confirm: (id, data = {}) => api.post(`/statements/${id}/confirm/`, data),
  delete: (id) => api.delete(`/statements/${id}/`),
};

export const transactionService = {
  list: (params) => api.get('/transactions/', { params }),
  getCategories: () => api.get('/transactions/categories/'),
  updateCategory: (id, data) => api.patch(`/transactions/${id}/update_category/`, data),
  delete: (id) => api.delete(`/transactions/${id}/`),
};

export const analyticsService = {
  getDashboard: (params) => api.get('/analytics/dashboard/', { params }),
  getInsights: () => api.get('/analytics/insights/'),
};

export const assistantService = {
  chat: (message) => api.post('/assistant/chat/', { message }),
};

export const reportService = {
  getCSVUrl: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return `/api/reports/transactions/csv/${qs ? '?' + qs : ''}`;
  },
  getPDFUrl: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return `/api/reports/financial-summary/pdf/${qs ? '?' + qs : ''}`;
  },
  getSummary: (params) => api.get('/reports/summary/', { params }),
};

export default api;
