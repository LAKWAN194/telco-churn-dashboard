import { formatMoney, formatMoneyWithCents, formatNumber, formatPercent } from '../format'

export default function StatTiles({ summary }) {
  const tiles = [
    {
      label: 'Customers',
      value: formatNumber(summary.total_customers),
      note: `${formatNumber(summary.churned_customers)} have churned`,
    },
    {
      label: 'Churn rate',
      value: formatPercent(summary.churn_rate),
      note: 'of all customers',
    },
    {
      label: 'Monthly revenue lost',
      value: formatMoney(summary.monthly_revenue_lost),
      note: 'monthly charges of churned customers',
    },
    {
      label: 'Average monthly charge',
      value: formatMoneyWithCents(summary.average_monthly_charges),
      note: `average tenure ${summary.average_tenure} months`,
    },
  ]

  return (
    <section className="stat-tiles" aria-label="Summary">
      {tiles.map((tile) => (
        <div className="card stat-tile" key={tile.label}>
          <p className="stat-label">{tile.label}</p>
          <p className="stat-value">{tile.value}</p>
          <p className="stat-note">{tile.note}</p>
        </div>
      ))}
    </section>
  )
}
