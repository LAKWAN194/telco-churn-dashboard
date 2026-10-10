import { formatPercent } from '../format'
import RiskBadge from './RiskBadge'

export default function PredictionResult({ prediction }) {
  const probability = prediction.churn_probability
  const threshold = prediction.threshold_used

  return (
    <div className="prediction-result" role="status">
      <div className="result-headline">
        <p className="result-value">{formatPercent(probability)}</p>
        <div>
          <p className="result-label">chance of churning</p>
          <RiskBadge level={prediction.risk_level} />
        </div>
      </div>

      <div
        className={`meter meter-${prediction.risk_level}`}
        role="meter"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(probability * 100)}
        aria-label="Churn probability"
      >
        <div className="meter-fill" style={{ width: `${probability * 100}%` }} />
        <div className="meter-threshold" style={{ left: `${threshold * 100}%` }} />
      </div>

      <p className="result-note">
        {prediction.churn_prediction
          ? 'The model predicts this customer will churn.'
          : 'The model predicts this customer will stay.'}{' '}
        It flags anyone at or above {formatPercent(threshold)}, marked on the bar.
      </p>
    </div>
  )
}
