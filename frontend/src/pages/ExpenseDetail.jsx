import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import * as expenseService from '../services/api'

const ExpenseDetail = () => {
  const navigate = useNavigate()
  const { id } = useParams()

  const [expense, setExpense] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)
  const [uploadError, setUploadError] = useState(null)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [receiptUrl, setReceiptUrl] = useState(null)

  useEffect(() => {
    fetchExpense()
  }, [id])

  const fetchExpense = async () => {
    try {
      setIsLoading(true)
      const response = await expenseService.expenses.getById(id)
      setExpense(response.data)
      if (response.data.receipt_path) {
        // Construct full URL for receipt image
        const receiptPath = response.data.receipt_path
        const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
        const baseUrl = apiBaseUrl.replace('/api', '')
        setReceiptUrl(`${baseUrl}${receiptPath}`)
      }
    } catch (err) {
      setError('Failed to load expense details')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleReceiptUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg']
    if (!validTypes.includes(file.type)) {
      setUploadError('Only PNG and JPG files are allowed')
      return
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError('File size must be less than 5MB')
      return
    }

    setIsUploading(true)
    setUploadError(null)
    setUploadSuccess(false)

    try {
      await expenseService.expenses.uploadReceipt(id, file)
      setUploadSuccess(true)
      // Refresh expense to get the receipt URL
      await fetchExpense()
      setTimeout(() => setUploadSuccess(false), 3000)
    } catch (err) {
      setUploadError('Failed to upload receipt')
      console.error(err)
    } finally {
      setIsUploading(false)
      // Clear file input
      e.target.value = ''
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const formatCurrency = (amount) => {
    return `$${amount.toFixed(2)}`
  }

  const getCategoryColor = (category) => {
    const colors = {
      Food: 'bg-orange-100 text-orange-800',
      Transport: 'bg-blue-100 text-blue-800',
      Entertainment: 'bg-purple-100 text-purple-800',
      Utilities: 'bg-yellow-100 text-yellow-800',
      Health: 'bg-red-100 text-red-800',
      Shopping: 'bg-pink-100 text-pink-800',
      Other: 'bg-gray-100 text-gray-800',
    }
    return colors[category] || colors['Other']
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !expense) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <h1 className="text-3xl font-bold text-gray-900">Expense Details</h1>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error || 'Expense not found'}
          </div>
          <button
            onClick={() => navigate('/expenses')}
            className="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Back to Expenses
          </button>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">Expense Details</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Expense Details Card */}
        <div className="bg-white rounded-lg shadow p-8 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Column: Basic Info */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Details</h2>

              {/* Amount */}
              <div className="mb-6">
                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">Amount</p>
                <p className="text-4xl font-bold text-gray-900 mt-2">{formatCurrency(expense.amount)}</p>
              </div>

              {/* Category */}
              <div className="mb-6">
                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Category</p>
                <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${getCategoryColor(expense.category)}`}>
                  {expense.category}
                </span>
              </div>

              {/* Date */}
              <div className="mb-6">
                <p className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Date</p>
                <p className="text-lg text-gray-900">{formatDate(expense.date)}</p>
              </div>

              {/* Description */}
              {expense.description && (
                <div className="mb-6">
                  <p className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Description</p>
                  <p className="text-gray-700 whitespace-pre-wrap">{expense.description}</p>
                </div>
              )}
            </div>

            {/* Right Column: Receipt Upload */}
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Receipt</h2>

              {uploadSuccess && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
                  Receipt uploaded successfully!
                </div>
              )}

              {uploadError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
                  {uploadError}
                </div>
              )}

              {/* Receipt Display */}
              {receiptUrl ? (
                <div className="mb-6">
                  <div className="bg-gray-100 rounded-lg overflow-hidden mb-4 border-2 border-gray-200">
                    <img
                      src={receiptUrl}
                      alt="Receipt"
                      className="w-full h-auto max-h-96 object-contain"
                    />
                  </div>
                  <a
                    href={receiptUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 underline text-sm"
                  >
                    Open in new window
                  </a>
                </div>
              ) : (
                <div className="bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 p-8 text-center mb-6">
                  <svg
                    className="mx-auto h-12 w-12 text-gray-400 mb-4"
                    stroke="currentColor"
                    fill="none"
                    viewBox="0 0 48 48"
                  >
                    <path
                      d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20m-14-8v14m0 0l-4-4m4 4l4-4"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                  <p className="text-gray-600">No receipt uploaded yet</p>
                </div>
              )}

              {/* Upload Input */}
              <label className="block">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/jpg"
                  onChange={handleReceiptUpload}
                  disabled={isUploading}
                  className="hidden"
                  id="receipt-input"
                />
                <label
                  htmlFor="receipt-input"
                  className="block text-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition cursor-pointer disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
                >
                  {isUploading ? 'Uploading...' : receiptUrl ? 'Update Receipt' : 'Upload Receipt'}
                </label>
              </label>
              <p className="text-xs text-gray-500 mt-3 text-center">
                PNG or JPG, max 5MB
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={() => navigate(`/expenses/${id}/edit`)}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium"
          >
            Edit Expense
          </button>
          <button
            onClick={() => navigate('/expenses')}
            className="flex-1 bg-gray-300 text-gray-900 px-4 py-2 rounded-lg hover:bg-gray-400 transition font-medium"
          >
            Back to Expenses
          </button>
        </div>
      </main>
    </div>
  )
}

export default ExpenseDetail
