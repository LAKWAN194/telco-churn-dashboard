import { useState } from 'react'
import { API_URL, getCustomer, getModelInfo, getSummary } from './api'
import AtRiskTable from './components/AtRiskTable'
import ChurnBreakdown from './components/ChurnBreakdown'
import ModelCard from './components/ModelCard'
import PredictionForm from './components/PredictionForm'
import RecentPredictions from './components/RecentPredictions'
import StatTiles from './components/StatTiles'
import { useApi } from './useApi'

function App() {
  const summary = useApi(getSummary)
  const model = useApi(getModelInfo)

  const [loadedCustomer, setLoadedCustomer] = useState(null)
  // Counts "What if" clicks. Used as the form's key, so each click starts the
  // form afresh with that customer, even if it is the same one twice.
  const [whatIfCount, setWhatIfCount] = useState(0)
  const [predictionCount, setPredictionCount] = useState(0)
  const [whatIfError, setWhatIfError] = useState(null)

  async function handleWhatIf(customerId) {
    try {
      setLoadedCustomer(await getCustomer(customerId))
      setWhatIfCount((count) => count + 1)
      setWhatIfError(null)
      document.getElementById('predict').scrollIntoView({ behavior: 'smooth' })
    } catch (problem) {
      setWhatIfError(`Could not load customer ${customerId}: ${problem.message}`)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Telco Churn Dashboard</h1>
        <p>Who is leaving, who is likely to leave next, and what the model makes of any customer.</p>
      </header>

      {summary.error && (
        <div className="card notice" role="alert">
          <h2>The dashboard cannot load its data</h2>
          <p>{summary.error}</p>
          <p className="muted">
            It is looking for the API at <code>{API_URL}</code>. Start it from the project root
            with <code>uvicorn backend.main:app --reload</code>.
          </p>
        </div>
      )}

      {summary.data && summary.data.total_customers === 0 && (
        <div className="card notice" role="alert">
          <h2>No customers in the database yet</h2>
          <p className="muted">
            Load the dataset with <code>python pipeline/ingest.py</code>, then refresh.
          </p>
        </div>
      )}

      {summary.data && summary.data.total_customers > 0 && (
        <>
          <StatTiles summary={summary.data} />

          {model.error && (
            <div className="card notice" role="alert">
              <h2>Predictions are unavailable</h2>
              <p>{model.error}</p>
            </div>
          )}

          <div className="columns">
            <div className="column">
              <ChurnBreakdown overallRate={summary.data.churn_rate} />
              {model.data && <AtRiskTable onWhatIf={handleWhatIf} />}
              {whatIfError && <p className="error">{whatIfError}</p>}
            </div>

            {model.data && (
              <div className="column">
                <PredictionForm
                  key={whatIfCount}
                  loadedCustomer={loadedCustomer}
                  onPredicted={() => setPredictionCount((count) => count + 1)}
                />
                <RecentPredictions refreshKey={predictionCount} />
                <ModelCard model={model.data} />
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

export default App
