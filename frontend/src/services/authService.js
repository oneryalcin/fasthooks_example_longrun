import api from './api'

export const register = (email, password, fullName) =>
  api.post('/auth/register', {
    email,
    password,
    full_name: fullName,
  })

export const login = (email, password) =>
  api.post('/auth/login', { email, password })

export const logout = () =>
  api.post('/auth/logout')

export const getCurrentUser = () =>
  api.get('/auth/me')

export const refreshToken = (refreshToken) =>
  api.post('/auth/refresh', { refresh_token: refreshToken })
