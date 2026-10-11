import { useState } from 'react'
import { predictChurn } from '../api'
import PredictionResult from './PredictionResult'

const DEFAULT_CUSTOMER = {
  gender: 'Female',
  senior_citizen: false,
  partner: false,
  dependents: false,
  tenure: 6,
  phone_service: true,
  multiple_lines: 'No',
  internet_service: 'Fiber optic',
  online_security: 'No',
  online_backup: 'No',
  device_protection: 'No',
  tech_support: 'No',
  streaming_tv: 'No',
  streaming_movies: 'No',
  contract_type: 'Month-to-month',
  paperless_billing: true,
  payment_method: 'Electronic check',
  monthly_charges: 80,
}

const INTERNET_ADDONS = [
  { name: 'online_security', label: 'Online security' },
  { name: 'online_backup', label: 'Online backup' },
  { name: 'device_protection', label: 'Device protection' },
  { name: 'tech_support', label: 'Tech support' },
  { name: 'streaming_tv', label: 'Streaming TV' },
  { name: 'streaming_movies', label: 'Streaming movies' },
]

const CHECKBOXES = [
  { name: 'senior_citizen', label: 'Senior citizen' },
  { name: 'partner', label: 'Has a partner' },
  { name: 'dependents', label: 'Has dependents' },
  { name: 'paperless_billing', label: 'Paperless billing' },
]

// Keeps the dependent fields consistent with the dataset: a customer without
// phone or internet service cannot have the add-ons that need it.
function withDependentFields(customer) {
  const next = { ...customer }

  if (!next.phone_service) {
    next.multiple_lines = 'No phone service'
  } else if (next.multiple_lines === 'No phone service') {
    next.multiple_lines = 'No'
  }

  for (const { name } of INTERNET_ADDONS) {
    if (next.internet_service === 'No') {
      next[name] = 'No internet service'
    } else if (next[name] === 'No internet service') {
      next[name] = 'No'
    }
  }

  return next
}

function Select({ label, value, onChange, options, disabled }) {
  return (
    <label className="field">
      {label}
      <select value={value} onChange={(event) => onChange(event.target.value)} disabled={disabled}>
        {options.map((option) => (
          <option key={option}>{option}</option>
        ))}
      </select>
    </label>
  )
}

// "What if" in the at-risk table hands a stored customer to the form. The
// stored record has extra columns (id, total charges, churn label) that the
// model does not take, so only the form's own fields are kept.
function initialCustomer(loadedCustomer) {
  if (!loadedCustomer) return DEFAULT_CUSTOMER

  const fields = Object.fromEntries(
    Object.keys(DEFAULT_CUSTOMER).map((name) => [name, loadedCustomer[name]]),
  )
  return withDependentFields(fields)
}

export default function PredictionForm({ loadedCustomer, onPredicted }) {
  const [customer, setCustomer] = useState(() => initialCustomer(loadedCustomer))
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  function update(name, value) {
    setCustomer((current) => withDependentFields({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const prediction = await predictChurn({
        ...customer,
        tenure: Number(customer.tenure),
        monthly_charges: Number(customer.monthly_charges),
      })
      setResult(prediction)
      onPredicted()
    } catch (problem) {
      setError(problem instanceof TypeError ? 'Could not reach the API.' : problem.message)
    } finally {
      setSubmitting(false)
    }
  }

  const hasInternet = customer.internet_service !== 'No'

  return (
    <section className="card" id="predict">
      <div className="card-header">
        <div>
          <h2>Predict churn</h2>
          <p className="card-subtitle">
            {loadedCustomer
              ? `Loaded customer ${loadedCustomer.customer_id}. Change anything and predict again.`
              : 'Describe a customer to get a live prediction from the model.'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <fieldset>
          <legend>Account</legend>
          <div className="field-grid">
            <label className="field">
              Tenure (months)
              <input
                type="number"
                min="0"
                max="120"
                required
                value={customer.tenure}
                onChange={(event) => update('tenure', event.target.value)}
              />
            </label>
            <label className="field">
              Monthly charges ($)
              <input
                type="number"
                min="0"
                max="1000"
                step="0.01"
                required
                value={customer.monthly_charges}
                onChange={(event) => update('monthly_charges', event.target.value)}
              />
            </label>
            <Select
              label="Contract"
              value={customer.contract_type}
              onChange={(value) => update('contract_type', value)}
              options={['Month-to-month', 'One year', 'Two year']}
            />
            <Select
              label="Payment method"
              value={customer.payment_method}
              onChange={(value) => update('payment_method', value)}
              options={[
                'Electronic check',
                'Mailed check',
                'Bank transfer (automatic)',
                'Credit card (automatic)',
              ]}
            />
            <Select
              label="Gender"
              value={customer.gender}
              onChange={(value) => update('gender', value)}
              options={['Female', 'Male']}
            />
          </div>
          <div className="checkbox-row">
            {CHECKBOXES.map(({ name, label }) => (
              <label className="checkbox" key={name}>
                <input
                  type="checkbox"
                  checked={customer[name]}
                  onChange={(event) => update(name, event.target.checked)}
                />
                {label}
              </label>
            ))}
          </div>
        </fieldset>

        <fieldset>
          <legend>Services</legend>
          <div className="field-grid">
            <Select
              label="Phone service"
              value={customer.phone_service ? 'Yes' : 'No'}
              onChange={(value) => update('phone_service', value === 'Yes')}
              options={['Yes', 'No']}
            />
            <Select
              label="Multiple lines"
              value={customer.multiple_lines}
              onChange={(value) => update('multiple_lines', value)}
              options={customer.phone_service ? ['Yes', 'No'] : ['No phone service']}
              disabled={!customer.phone_service}
            />
            <Select
              label="Internet service"
              value={customer.internet_service}
              onChange={(value) => update('internet_service', value)}
              options={['DSL', 'Fiber optic', 'No']}
            />
            {INTERNET_ADDONS.map(({ name, label }) => (
              <Select
                key={name}
                label={label}
                value={customer[name]}
                onChange={(value) => update(name, value)}
                options={hasInternet ? ['Yes', 'No'] : ['No internet service']}
                disabled={!hasInternet}
              />
            ))}
          </div>
        </fieldset>

        <div className="form-actions">
          <button type="submit" className="primary-button" disabled={submitting}>
            {submitting ? 'Predicting…' : 'Predict churn'}
          </button>
          <button
            type="button"
            className="link-button"
            onClick={() => {
              setCustomer(initialCustomer(loadedCustomer))
              setResult(null)
              setError(null)
            }}
          >
            Reset
          </button>
        </div>
      </form>

      {error && <p className="error">{error}</p>}
      {result && <PredictionResult prediction={result} />}
    </section>
  )
}
