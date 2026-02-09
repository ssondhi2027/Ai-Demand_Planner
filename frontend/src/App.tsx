import { useMemo, useState, type FormEvent } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts'

type ForecastResult = {
  model: 'arima' | 'xgboost'
  dates: string[]
  forecast: number[]
  lower: number[]
  upper: number[]
  metrics?: {
    MAE?: number
    RMSE?: number
  }
}

type UploadResponse = {
  dataset_id: string
  rows: number
}

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

function buildSeries(result: ForecastResult) {
  return result.dates.map((date, i) => ({
    date,
    forecast: result.forecast[i],
    lower: result.lower[i],
    upper: result.upper[i]
  }))
}

export default function App() {
  const [step, setStep] = useState<'auth' | 'upload' | 'dashboard'>('auth')
  const [authName, setAuthName] = useState('')
  const [authEmail, setAuthEmail] = useState('')
  const [authPassword, setAuthPassword] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [datasetId, setDatasetId] = useState('')
  const [rows, setRows] = useState<number | null>(null)
  const [horizon, setHorizon] = useState(30)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [arimaResult, setArimaResult] = useState<ForecastResult | null>(null)
  const [xgbResult, setXgbResult] = useState<ForecastResult | null>(null)

  const arimaSeries = useMemo(
    () => (arimaResult ? buildSeries(arimaResult) : []),
    [arimaResult]
  )
  const xgbSeries = useMemo(
    () => (xgbResult ? buildSeries(xgbResult) : []),
    [xgbResult]
  )

  const canAuth = authName.trim() && authEmail.trim() && authPassword.trim()
  const canUpload = Boolean(file)

  async function handleAuthSubmit(e: FormEvent) {
    e.preventDefault()
    if (!canAuth) return
    setStep('upload')
  }

  async function handleUpload(e: FormEvent) {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    setError(null)
    setArimaResult(null)
    setXgbResult(null)

    try {
      const form = new FormData()
      form.append('file', file)

      const uploadRes = await fetch(`${API_BASE}/api/upload/upload`, {
        method: 'POST',
        body: form
      })
      if (!uploadRes.ok) {
        const detail = await uploadRes.json().catch(() => ({}))
        throw new Error(detail.detail || 'Upload failed')
      }
      const uploadData = (await uploadRes.json()) as UploadResponse
      setDatasetId(uploadData.dataset_id)
      setRows(uploadData.rows)

      const [arimaRes, xgbRes] = await Promise.all([
        fetch(`${API_BASE}/api/forecast/forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            dataset_id: uploadData.dataset_id,
            model: 'arima',
            horizon
          })
        }),
        fetch(`${API_BASE}/api/forecast/forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            dataset_id: uploadData.dataset_id,
            model: 'xgboost',
            horizon
          })
        })
      ])

      if (!arimaRes.ok) {
        const detail = await arimaRes.json().catch(() => ({}))
        throw new Error(detail.detail || 'ARIMA forecast failed')
      }
      if (!xgbRes.ok) {
        const detail = await xgbRes.json().catch(() => ({}))
        throw new Error(detail.detail || 'XGBoost forecast failed')
      }

      const arimaData = (await arimaRes.json()) as ForecastResult
      const xgbData = (await xgbRes.json()) as ForecastResult

      setArimaResult(arimaData)
      setXgbResult(xgbData)
      setStep('dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  async function handleRerun() {
    if (!datasetId) return
    setLoading(true)
    setError(null)
    try {
      const [arimaRes, xgbRes] = await Promise.all([
        fetch(`${API_BASE}/api/forecast/forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            dataset_id: datasetId,
            model: 'arima',
            horizon
          })
        }),
        fetch(`${API_BASE}/api/forecast/forecast`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            dataset_id: datasetId,
            model: 'xgboost',
            horizon
          })
        })
      ])

      if (!arimaRes.ok) {
        const detail = await arimaRes.json().catch(() => ({}))
        throw new Error(detail.detail || 'ARIMA forecast failed')
      }
      if (!xgbRes.ok) {
        const detail = await xgbRes.json().catch(() => ({}))
        throw new Error(detail.detail || 'XGBoost forecast failed')
      }

      setArimaResult((await arimaRes.json()) as ForecastResult)
      setXgbResult((await xgbRes.json()) as ForecastResult)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <div className="hero-content">
          <p className="eyebrow">Demand Intelligence Studio</p>
          <h1>
            Forecast, stress-test, and communicate demand plans with confidence
          </h1>
          <p className="subhead">
            Upload your demand history once, then compare ARIMA and XGBoost
            forecasts side by side with clean visuals and transparent metrics.
          </p>
        </div>
        <div className="hero-panel">
          <div className="stepper">
            <div className={`step ${step !== 'auth' ? 'done' : 'active'}`}>
              1
            </div>
            <span>Authenticate</span>
            <div className={`step ${step === 'upload' ? 'active' : step === 'dashboard' ? 'done' : ''}`}>
              2
            </div>
            <span>Upload</span>
            <div className={`step ${step === 'dashboard' ? 'active' : ''}`}>
              3
            </div>
            <span>Dashboard</span>
          </div>
          <p className="env">API: {API_BASE}</p>
        </div>
      </header>

      <main className="content">
        {step === 'auth' && (
          <section className="panel">
            <h2>Authenticity Check</h2>
            <p className="muted">
              This portfolio demo uses a simple front-end gate. Enter your
              details to unlock the forecasting workflow.
            </p>
            <form className="form" onSubmit={handleAuthSubmit}>
              <label>
                Full name
                <input
                  type="text"
                  placeholder="Simra Patel"
                  value={authName}
                  onChange={(e) => setAuthName(e.target.value)}
                />
              </label>
              <label>
                Work email
                <input
                  type="email"
                  placeholder="you@company.com"
                  value={authEmail}
                  onChange={(e) => setAuthEmail(e.target.value)}
                />
              </label>
              <label>
                Passphrase
                <input
                  type="password"
                  placeholder="••••••••"
                  value={authPassword}
                  onChange={(e) => setAuthPassword(e.target.value)}
                />
              </label>
              <button className="primary" type="submit" disabled={!canAuth}>
                Continue to upload
              </button>
            </form>
          </section>
        )}

        {step === 'upload' && (
          <section className="panel">
            <h2>Upload demand history</h2>
            <p className="muted">
              Accepted columns: <span className="pill">date</span>{' '}
              <span className="pill">product_name</span>{' '}
              <span className="pill">demand</span>
            </p>
            <form className="form" onSubmit={handleUpload}>
              <label className="upload">
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />
                <div>
                  <strong>{file ? file.name : 'Drop CSV or click to browse'}</strong>
                  <span>Max 10MB. Time-series data recommended.</span>
                </div>
              </label>
              <label>
                Forecast horizon (days)
                <input
                  type="number"
                  min={1}
                  max={365}
                  value={horizon}
                  onChange={(e) => setHorizon(Number(e.target.value))}
                />
              </label>
              <button className="primary" type="submit" disabled={!canUpload || loading}>
                {loading ? 'Processing…' : 'Upload + Run ARIMA & XGBoost'}
              </button>
              {error && <p className="error">{error}</p>}
            </form>
          </section>
        )}

        {step === 'dashboard' && (
          <section className="panel">
            <div className="panel-head">
              <div>
                <h2>Forecast comparison dashboard</h2>
                <p className="muted">
                  Dataset <span className="pill">{datasetId}</span>
                  {rows !== null && (
                    <>
                      {' '}
                      • Rows <span className="pill">{rows}</span>
                    </>
                  )}
                </p>
              </div>
              <div className="panel-actions">
                <label>
                  Horizon
                  <input
                    type="number"
                    min={1}
                    max={365}
                    value={horizon}
                    onChange={(e) => setHorizon(Number(e.target.value))}
                  />
                </label>
                <button className="ghost" onClick={handleRerun} disabled={loading}>
                  {loading ? 'Re-running…' : 'Re-run forecasts'}
                </button>
              </div>
            </div>

            {error && <p className="error">{error}</p>}

            <div className="grid">
              <div className="card">
                <h3>ARIMA Forecast</h3>
                <p className="muted">Baseline statistical model.</p>
                <div className="chart">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={arimaSeries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0c5a8" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="forecast" stroke="#1b7f7a" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="lower" stroke="#9db7b5" strokeDasharray="4 4" dot={false} />
                      <Line type="monotone" dataKey="upper" stroke="#9db7b5" strokeDasharray="4 4" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="card">
                <h3>XGBoost Forecast</h3>
                <p className="muted">Machine learning model with engineered lags.</p>
                <div className="chart">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={xgbSeries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0c5a8" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip />
                      <Line type="monotone" dataKey="forecast" stroke="#f05d3b" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="lower" stroke="#f1b4a4" strokeDasharray="4 4" dot={false} />
                      <Line type="monotone" dataKey="upper" stroke="#f1b4a4" strokeDasharray="4 4" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                {xgbResult?.metrics && (
                  <div className="metrics">
                    <div>
                      <span>MAE</span>
                      <strong>{xgbResult.metrics.MAE ?? '-'}</strong>
                    </div>
                    <div>
                      <span>RMSE</span>
                      <strong>{xgbResult.metrics.RMSE ?? '-'}</strong>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
