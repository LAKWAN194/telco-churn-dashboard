import { useState } from 'react'
import { getChurnBy } from '../api'
import { formatNumber, formatPercent } from '../format'
import { useApi } from '../useApi'

const DIMENSIONS = [
  { value: 'contract_type', label: 'Contract type' },
  { value: 'tenure_band', label: 'Tenure' },
  { value: 'internet_service', label: 'Internet service' },
  { value: 'payment_method', label: 'Payment method' },
  { value: 'tech_support', label: 'Tech support' },
]

// Tenure bands have a natural order, so they stay as the API returns them.
// Everything else is sorted so the worst group is at the top.
const ORDERED_DIMENSIONS = ['tenure_band']

export default function ChurnBreakdown({ overallRate }) {
  const [dimension, setDimension] = useState('contract_type')
  const { data, error, loading } = useApi(() => getChurnBy(dimension), dimension)

  // The rate is worked out from the counts here, so the label is not a
  // rounding of the API's already-rounded figure.
  const withRates = (data ?? []).map((group) => ({
    ...group,
    churn_rate: group.churned / group.customers,
  }))

  const groups = ORDERED_DIMENSIONS.includes(dimension)
    ? withRates
    : [...withRates].sort((a, b) => b.churn_rate - a.churn_rate)

  // Bars are scaled to the largest group, leaving room for the label at the tip
  const highestRate = Math.max(...groups.map((group) => group.churn_rate), 0.01)

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Churn rate by group</h2>
          <p className="card-subtitle">
            Share of customers in each group who left. Overall: {formatPercent(overallRate)}.
          </p>
        </div>
        <label className="inline-field">
          Group by
          <select value={dimension} onChange={(event) => setDimension(event.target.value)}>
            {DIMENSIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      {error && <p className="error">{error}</p>}

      {groups.length > 0 && (
        <div className="table-scroll">
          <table className={`bar-table ${loading ? 'is-refreshing' : ''}`}>
            <thead>
              <tr>
                <th scope="col">Group</th>
                <th scope="col">Churn rate</th>
                <th scope="col" className="numeric">
                  Churned / customers
                </th>
              </tr>
            </thead>
            <tbody>
              {groups.map((group) => (
                <tr key={group.label}>
                  <th scope="row">{group.label}</th>
                  <td className="bar-cell">
                    <div className="bar-row">
                      <div
                        className="bar"
                        style={{ width: `${(group.churn_rate / highestRate) * 100}%` }}
                      />
                      <span className="bar-value">{formatPercent(group.churn_rate)}</span>
                    </div>
                  </td>
                  <td className="numeric muted">
                    {formatNumber(group.churned)} / {formatNumber(group.customers)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
