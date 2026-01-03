import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import * as analyticsService from '../services/api'

const Dashboard = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchSummary()
  }, [])

  const fetchSummary = async () => {
    try {
      setIsLoading(true)
      const response = await analyticsService.analytics.getSummary()
      setSummary(response.data)
    } catch (err) {
      setError('Failed to load analytics')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const handleNavigate = (path) => {
    navigate(path)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Expense Tracker</h1>
            <p className="text-gray-600 mt-1">Welcome, {user?.full_name || user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center items-center h-96">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {/* Total Spending Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 text-sm font-medium">Total Spending</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  ${summary?.total_spending?.toFixed(2) || '0.00'}
                </p>
              </div>

              {/* Current Month Spending Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 text-sm font-medium">This Month</p>
                <p className="text-3xl font-bold text-blue-600 mt-2">
                  ${summary?.current_month_spending?.toFixed(2) || '0.00'}
                </p>
              </div>

              {/* Categories Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 text-sm font-medium">Categories</p>
                <p className="text-3xl font-bold text-green-600 mt-2">
                  {summary?.by_category?.length || 0}
                </p>
              </div>

              {/* Expenses Count Card */}
              <div className="bg-white rounded-lg shadow p-6">
                <p className="text-gray-600 text-sm font-medium">Total Expenses</p>
                <p className="text-3xl font-bold text-purple-600 mt-2">
                  {summary?.monthly_trends?.reduce((acc, month) => acc + month.by_category.length, 0) || 0}
                </p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <button
                onClick={() => handleNavigate('/expenses')}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium"
              >
                View Expenses
              </button>
              <button
                onClick={() => handleNavigate('/expenses/new')}
                className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition font-medium"
              >
                Add Expense
              </button>
              <button
                onClick={() => handleNavigate('/budgets')}
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition font-medium"
              >
                Manage Budgets
              </button>
              <button
                onClick={() => handleNavigate('/analytics')}
                className="bg-orange-600 text-white px-6 py-3 rounded-lg hover:bg-orange-700 transition font-medium"
              >
                Analytics
              </button>
            </div>

            {/* Category Breakdown */}
            {summary?.by_category && summary.by_category.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-6">Spending by Category</h2>
                <div className="space-y-4">
                  {summary.by_category.map((cat) => (
                    <div key={cat.category} className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="text-gray-900 font-medium">{cat.category}</p>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{ width: `${cat.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="text-right ml-4">
                        <p className="text-gray-900 font-bold">${cat.total?.toFixed(2)}</p>
                        <p className="text-gray-600 text-sm">{cat.percentage?.toFixed(1)}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default Dashboard
