import { getAtRiskCustomers } from '../api'
import { formatMoneyWithCents, formatPercent } from '../format'
import { useApi } from '../useApi'
import RiskBadge from './RiskBadge'

export default function AtRiskTable({ onWhatIf }) {
  const { data: customers, error } = useApi(() => getAtRiskCustomers(8))

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h2>Customers most likely to leave</h2>
          <p className="card-subtitle">
            Current customers ranked by the model. Use "What if" to load one into the form
            and see what would change their score.
          </p>
        </div>
      </div>

      {error && <p className="error">{error}</p>}
      {customers && customers.length === 0 && <p className="muted">No customers loaded yet.</p>}

      {customers && customers.length > 0 && (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th scope="col">Customer</th>
                <th scope="col">Contract</th>
                <th scope="col" className="numeric">
                  Tenure
                </th>
                <th scope="col" className="numeric">
                  Monthly
                </th>
                <th scope="col" className="numeric">
                  Churn chance
                </th>
                <th scope="col">Risk</th>
                <th scope="col">
                  <span className="visually-hidden">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.customer_id}>
                  <th scope="row">{customer.customer_id}</th>
                  <td>{customer.contract_type}</td>
                  <td className="numeric">{customer.tenure} mo</td>
                  <td className="numeric">{formatMoneyWithCents(customer.monthly_charges)}</td>
                  <td className="numeric">{formatPercent(customer.churn_probability)}</td>
                  <td>
                    <RiskBadge level={customer.risk_level} />
                  </td>
                  <td>
                    <button
                      type="button"
                      className="link-button"
                      onClick={() => onWhatIf(customer.customer_id)}
                    >
                      What if
                    </button>
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
