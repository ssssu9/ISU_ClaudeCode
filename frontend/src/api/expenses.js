import client from './client'

export const uploadReceipt = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return client.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  })
}

export const getExpenses = (from, to) =>
  client.get('/expenses', { params: { from_date: from, to_date: to } })

export const deleteExpense = (id) => client.delete(`/expenses/${id}`)

export const updateExpense = (id, data) => client.put(`/expenses/${id}`, data)

export const getSummary = (month) =>
  client.get('/summary', { params: { month } })
