import React, { useState, useEffect } from 'react'
import * as budgetService from '../services/api'
import * as analyticsService from '../services/api'

const Budgets = () => {
  const [budgets, setBudgets] = useState([])
  const [spending, setSpending] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    category: 'Food',
    monthly_limit: '',
  })
  const [formError, setFormError] = useState('')

  const categories = ['Food', 'Transport', 'Entertainment', 'Utilities', 'Health', 'Shopping', 'Other']

  useEffect(() => {
    fetchBudgets()
  }, [])

  const fetchBudgets = async () => {
    try {
      setIsLoading(true)
      const [budgetsRes, analyticsRes] = await Promise.all([
        budgetService.budgets.getAll(),
        analyticsService.analytics.getSummary(),
      ])

      setBudgets(budgetsRes.data || [])

      // Build spending map from analytics
      const spendingMap = {}
      if (analyticsRes.data?.by_category) {
        analyticsRes.data.by_category.forEach((cat) => {
          spendingMap[cat.category] = cat.total
        })
      }
      setSpending(spendingMap)
    } catch (err) {
      setError('Failed to load budgets')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const validateForm = () => {
    setFormError('')

    if (!formData.monthly_limit) {
      setFormError('Budget limit is required')
      return false
    }

    const limit = parseFloat(formData.monthly_limit)
    if (limit <= 0) {
      setFormError('Budget limit must be greater than 0')
      return false
    }

    return true
  }

  const handleAddBudget = async (e) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      await budgetService.budgets.create({
        category: formData.category,
        monthly_limit: parseFloat(formData.monthly_limit),
      })

      setFormData({ category: 'Food', monthly_limit: '' })
      setShowForm(false)
      fetchBudgets()
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to create budget'
      setFormError(errorMsg)
    }
  }

  const handleDeleteBudget = async (category) => {
    if (window.confirm(`Delete budget for ${category}?`)) {
      try {
        await budgetService.budgets.delete(category)
        fetchBudgets()
      } catch (err) {
        setError('Failed to delete budget')
      }
    }
  }

  const getBudgetStatus = (category) => {
    const budget = budgets.find((b) => b.category === category)
    if (!budget) return null

    const spent = spending[category] || 0
    const limit = budget.monthly_limit
    const percentage = (spent / limit) * 100

    let status = 'safe'
    let color = 'green'

    if (percentage >= 100) {
      status = 'over'
      color = 'red'
    } else if (percentage >= 80) {
      status = 'warning'
      color = 'yellow'
    }

    return { spent, limit, percentage, status, color }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Budgets</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            {showForm ? 'Cancel' : 'Add Budget'}
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

        {/* Add Budget Form */}
        {showForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Create New Budget</h2>
            <form onSubmit={handleAddBudget} className="space-y-4">
              {formError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {formError}
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Limit</label>
                  <div className="relative">
                    <span className="absolute left-4 top-2 text-2xl text-gray-500">$</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={formData.monthly_limit}
                      onChange={(e) => {
                        setFormData({ ...formData, monthly_limit: e.target.value })
                        setFormError('')
                      }}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                      placeholder="0.00"
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 transition"
              >
                Create Budget
              </button>
            </form>
          </div>
        )}

        {/* Budgets List */}
        {budgets.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 text-lg mb-4">No budgets set yet</p>
            <p className="text-gray-500 mb-6">Create a budget to track your spending and get alerts</p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Create Your First Budget
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {budgets.map((budget) => {
              const status = getBudgetStatus(budget.category)
              return (
                <div key={budget.category} className="bg-white rounded-lg shadow p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-bold text-gray-900">{budget.category}</h3>
                    <button
                      onClick={() => handleDeleteBudget(budget.category)}
                      className="text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>

                  {status && (
                    <>
                      {/* Budget Status */}
                      <div className="mb-4">
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-600">Spent</span>
                          <span className="text-sm font-semibold text-gray-900">
                            ${status.spent.toFixed(2)} of ${status.limit.toFixed(2)}
                          </span>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                          <div
                            className={`h-3 rounded-full transition-all bg-${status.color}-500`}
                            style={{
                              width: `${Math.min(status.percentage, 100)}%`,
                              backgroundColor:
                                status.color === 'red'
                                  ? '#ef4444'
                                  : status.color === 'yellow'
                                  ? '#f59e0b'
                                  : '#10b981',
                            }}
                          ></div>
                        </div>
                      </div>

                      {/* Status Badge */}
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{status.percentage.toFixed(1)}% spent</span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium text-white ${
                            status.status === 'safe'
                              ? 'bg-green-600'
                              : status.status === 'warning'
                              ? 'bg-yellow-600'
                              : 'bg-red-600'
                          }`}
                        >
                          {status.status === 'safe'
                            ? 'On Track'
                            : status.status === 'warning'
                            ? 'Warning'
                            : 'Over Budget'}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}

export default Budgets
