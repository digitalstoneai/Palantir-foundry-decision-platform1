import { useEffect, useState } from 'react'
import { apiFetch } from '../../api/client.js'
import ConfidenceFlag from '../shared/ConfidenceFlag.jsx'
import ModelTag from '../shared/ModelTag.jsx'

export default function ImpactSummary({ objectId, eventId, onResult }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!objectId) return
    setLoading(true)
    setError(null)
    apiFetch('/api/opsgraph/impact', {
      method: 'POST',
      body: JSON.stringify({ object_id: objectId, event_id: eventId ?? null }),
    })
      .then((data) => {
        setResult(data)
        onResult?.(data)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [objectId, eventId])

  if (!objectId) {
    return (
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Impact Analysis</h3>
        <p style={{ color: 'var(--text-muted)' }}>Select an object to analyze impact.</p>
      </div>
    )
  }

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Impact Analysis</h3>
      {loading && <p style={{ color: 'var(--text-muted)' }}>Analyzing dependency path...</p>}
      {error && <p style={{ color: 'var(--red)' }}>{error}</p>}
      {result && (
        <>
          <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
            <ModelTag model={result.ai_model} />
            <ConfidenceFlag confidence={result.confidence} />
            {result.degraded_mode && (
              <span className="badge" style={{ background: 'rgba(227,179,65,0.15)', color: 'var(--orange)' }}>
                ⚠ degraded
              </span>
            )}
          </div>
          <p>{result.summary}</p>
          <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>
            Affected objects: {result.affected_objects.join(', ') || 'none'}
          </p>
        </>
      )}
    </div>
  )
}
