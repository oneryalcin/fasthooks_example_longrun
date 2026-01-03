import React, { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import * as analyticsService from '../services/api'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6']

const Analytics = () => {
  const [summary, setSummary] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
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

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-700 px-8 py-6 rounded-lg">
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm font-medium">Total Spending</p>
            <p className="text-4xl font-bold text-gray-900 mt-2">
              ${summary?.total_spending?.toFixed(2) || '0.00'}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm font-medium">Current Month</p>
            <p className="text-4xl font-bold text-blue-600 mt-2">
              ${summary?.current_month_spending?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Pie Chart - Spending by Category */}
          {summary?.by_category && summary.by_category.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Spending by Category</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={summary.by_category}
                    dataKey="total"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={({ category, percentage }) => `${category} (${percentage}%)`}
                  >
                    {summary.by_category.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                </PieChart>
              </ResponsiveContainer>

              {/* Legend */}
              <div className="mt-6 space-y-2">
                {summary.by_category.map((cat, index) => (
                  <div key={cat.category} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      ></div>
                      <span className="text-gray-700">{cat.category}</span>
                    </div>
                    <span className="font-semibold text-gray-900">
                      ${cat.total?.toFixed(2)} ({cat.percentage?.toFixed(1)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Bar Chart - Monthly Trends */}
          {summary?.monthly_trends && summary.monthly_trends.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-6">Monthly Spending Trends</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={summary.monthly_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => `$${value.toFixed(2)}`} />
                  <Bar dataKey="total" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Category Breakdown Table */}
        {summary?.by_category && summary.by_category.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Category Details</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left px-4 py-3 text-sm font-semibold text-gray-900">Category</th>
                    <th className="text-right px-4 py-3 text-sm font-semibold text-gray-900">Count</th>
                    <th className="text-right px-4 py-3 text-sm font-semibold text-gray-900">Total</th>
                    <th className="text-right px-4 py-3 text-sm font-semibold text-gray-900">Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.by_category.map((cat) => (
                    <tr key={cat.category} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900 font-medium">{cat.category}</td>
                      <td className="px-4 py-3 text-sm text-gray-600 text-right">{cat.count}</td>
                      <td className="px-4 py-3 text-sm text-gray-900 font-semibold text-right">
                        ${cat.total?.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 text-right">
                        {cat.percentage?.toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default Analytics
