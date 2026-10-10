import { formatNumber, formatPercent } from '../format'

const MODEL_NAMES = {
  logreg: 'Logistic regression',
  xgboost: 'XGBoost',
}

export default function ModelCard({ model }) {
  const { metrics } = model
  const trainedOn = new Date(model.trained_at).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })

  const facts = [
    {
      label: 'PR-AUC',
      value: metrics.pr_auc.toFixed(3),
      note: `random guessing scores ${metrics.baseline_pr_auc.toFixed(3)}`,
    },
    {
      label: 'Recall',
      value: formatPercent(metrics.recall),
      note: 'of churners are caught',
    },
    {
      label: 'Precision',
      value: formatPercent(metrics.precision),
      note: 'of flagged customers do churn',
    },
    {
      label: 'Threshold',
      value: formatPercent(model.threshold),
      note: 'flagged at or above this',
    },
  ]

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Model</h2>
          <p className="card-subtitle">
            {MODEL_NAMES[model.model_name] ?? model.model_name} ({model.model_version}), trained{' '}
            {trainedOn}. Scores are from {formatNumber(metrics.n_samples)} held-out customers
            the model never saw.
          </p>
        </div>
      </div>

      <dl className="fact-grid">
        {facts.map((fact) => (
          <div key={fact.label}>
            <dt>{fact.label}</dt>
            <dd>{fact.value}</dd>
            <p className="stat-note">{fact.note}</p>
          </div>
        ))}
      </dl>
    </section>
  )
}
