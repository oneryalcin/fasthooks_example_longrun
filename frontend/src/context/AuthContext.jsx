import React, { createContext, useState, useCallback, useEffect } from 'react'
import * as authService from '../services/authService'

export const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const response = await authService.getCurrentUser()
          setUser(response.data)
          setIsAuthenticated(true)
        } catch (err) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          setIsAuthenticated(false)
        }
      }
      setIsLoading(false)
    }

    checkAuth()
  }, [])

  const register = useCallback(async (email, password, fullName) => {
    try {
      setError(null)
      const response = await authService.register(email, password, fullName)
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)

      // Get user info
      const userResponse = await authService.getCurrentUser()
      setUser(userResponse.data)
      setIsAuthenticated(true)
      return { success: true }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Registration failed'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }, [])

  const login = useCallback(async (email, password) => {
    try {
      setError(null)
      const response = await authService.login(email, password)
      localStorage.setItem('access_token', response.data.access_token)
      localStorage.setItem('refresh_token', response.data.refresh_token)

      // Get user info
      const userResponse = await authService.getCurrentUser()
      setUser(userResponse.data)
      setIsAuthenticated(true)
      return { success: true }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      setIsAuthenticated(false)
    }
  }, [])

  const value = {
    user,
    isAuthenticated,
    isLoading,
    error,
    register,
    login,
    logout,
    setError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = React.useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
