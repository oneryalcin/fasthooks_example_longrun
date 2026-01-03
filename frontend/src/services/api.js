import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Authentication endpoints
export const auth = {
  register: (email, password, fullName) =>
    api.post('/auth/register', { email, password, full_name: fullName }),
  login: (email, password) =>
    api.post('/auth/login', { email, password }),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
}

// Expense endpoints
export const expenses = {
  getAll: (filters) => api.get('/expenses', { params: filters }),
  getById: (id) => api.get(`/expenses/${id}`),
  create: (data) => api.post('/expenses', data),
  update: (id, data) => api.put(`/expenses/${id}`, data),
  delete: (id) => api.delete(`/expenses/${id}`),
  uploadReceipt: (id, file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/expenses/${id}/receipt`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  exportCsv: () => api.get('/expenses/export/csv'),
}

// Category endpoints
export const categories = {
  getAll: () => api.get('/categories'),
}

// Budget endpoints
export const budgets = {
  getAll: () => api.get('/budgets'),
  create: (data) => api.post('/budgets', data),
  update: (category, data) => api.put(`/budgets/${category}`, data),
  delete: (category) => api.delete(`/budgets/${category}`),
}

// Recurring expense endpoints
export const recurringExpenses = {
  getAll: () => api.get('/recurring-expenses'),
  getById: (id) => api.get(`/recurring-expenses/${id}`),
  create: (data) => api.post('/recurring-expenses', data),
  update: (id, data) => api.put(`/recurring-expenses/${id}`, data),
  delete: (id) => api.delete(`/recurring-expenses/${id}`),
}

// Analytics endpoints
export const analytics = {
  getSummary: (months = 12) => api.get('/analytics/summary', { params: { months } }),
  getByCategory: () => api.get('/analytics/by-category'),
  getByMonth: (months = 12) => api.get('/analytics/by-month', { params: { months } }),
}

export default api
