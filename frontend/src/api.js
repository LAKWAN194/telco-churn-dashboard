export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options) {
  const response = await fetch(`${API_URL}${path}`, options)

  if (!response.ok) {
    // FastAPI puts the reason in "detail": a string for our own errors,
    // a list of field problems for validation errors.
    const body = await response.json().catch(() => ({}))
    const detail = Array.isArray(body.detail)
      ? body.detail.map((problem) => `${problem.loc.at(-1)}: ${problem.msg}`).join('; ')
      : body.detail

    throw new Error(detail || `Request failed (${response.status})`)
  }

  return response.json()
}

export function getSummary() {
  return request('/stats/summary')
}

export function getChurnBy(dimension) {
  return request(`/stats/churn-by/${dimension}`)
}

export function getModelInfo() {
  return request('/model')
}

export function getAtRiskCustomers(limit = 8) {
  return request(`/customers/at-risk?limit=${limit}`)
}

export function getCustomer(customerId) {
  return request(`/customers/${encodeURIComponent(customerId)}`)
}

export function getRecentPredictions(limit = 8) {
  return request(`/predictions?limit=${limit}`)
}

export function predictChurn(customer) {
  return request('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(customer),
  })
}
