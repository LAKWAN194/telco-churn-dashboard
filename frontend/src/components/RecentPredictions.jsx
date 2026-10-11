import { getRecentPredictions } from '../api'
import { formatDateTime, formatPercent } from '../format'
import { useApi } from '../useApi'
import RiskBadge from './RiskBadge'

export default function RecentPredictions({ refreshKey }) {
  // refreshKey changes after each new prediction, which reloads the list
  const { data: predictions, error } = useApi(() => getRecentPredictions(8), refreshKey)

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Recent predictions</h2>
          <p className="card-subtitle">Every prediction is saved to the database.</p>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {predictions && predictions.length === 0 && (
        <p className="muted">No predictions yet. Try the form above.</p>
      )}

      {predictions && predictions.length > 0 && (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th scope="col">When</th>
                <th scope="col">Customer</th>
                <th scope="col" className="numeric">
                  Churn chance
                </th>
                <th scope="col">Risk</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((prediction) => (
                <tr key={prediction.prediction_id}>
                  <td>{formatDateTime(prediction.predicted_at)}</td>
                  <td>{prediction.customer_id ?? 'What-if'}</td>
                  <td className="numeric">{formatPercent(prediction.churn_probability)}</td>
                  <td>
                    <RiskBadge level={prediction.risk_level} />
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
