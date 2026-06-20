import { useEffect, useState } from 'react'
import { apiFetch } from '../../api/client.js'
import ConstraintEditor from './ConstraintEditor.jsx'
import RecommendationCard from './RecommendationCard.jsx'
import ScenarioPanel from './ScenarioPanel.jsx'

const INITIAL_CONSTRAINTS = [
  { name: 'cost', threshold: 5000, weight: 0.4 },
  { name: 'service', threshold: 0.3, weight: 0.4 },
  { name: 'risk', threshold: 0.5, weight: 0.2 },
]

export default function DecisionRoomView() {
  const [events, setEvents] = useState([])
  const [selectedEventId, setSelectedEventId] = useState(null)
  const [options, setOptions] = useState([])
  const [constraints, setConstraints] = useState(INITIAL_CONSTRAINTS)
  const [recommendation, setRecommendation] = useState(null)
  const [approved, setApproved] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiFetch('/api/opsgraph/events').then(setEvents)
  }, [])

  useEffect(() => {
    if (!selectedEventId) return
    apiFetch(`/api/decision/options/${selectedEventId}`).then(setOptions)
    setRecommendation(null)
    setApproved(false)
  }, [selectedEventId])

  const requestRecommendation = () => {
    setLoading(true)
    setError(null)
    apiFetch('/api/decision/recommend', {
      method: 'POST',
      body: JSON.stringify({ event_id: selectedEventId, constraints }),
    })
      .then(setRecommendation)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  const approveRecommendation = () => {
    apiFetch('/api/decision/record', {
      method: 'POST',
      body: JSON.stringify({
        event_id: selectedEventId,
        option_id: recommendation.recommended_option_id,
        rationale: recommendation.rationale,
        decided_by: 'operations_manager',
      }),
    })
      .then(() => setApproved(true))
      .catch((err) => setError(err.message))
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px 1fr', gap: 16 }}>
      <ScenarioPanel
        events={events}
        selectedEventId={selectedEventId}
        onSelectEvent={setSelectedEventId}
        options={options}
      />
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        <ConstraintEditor constraints={constraints} onChange={setConstraints} />
        <button
          onClick={requestRecommendation}
          disabled={!selectedEventId || !options.length || loading}
          style={{
            background: 'var(--surface-3)',
            color: 'var(--text)',
            border: '1px solid var(--border)',
            borderRadius: 4,
            padding: '10px 12px',
            cursor: selectedEventId ? 'pointer' : 'default',
          }}
        >
          {loading ? 'Evaluating...' : 'Get Recommendation'}
        </button>
        {error && <p style={{ color: 'var(--red)', fontSize: 13 }}>{error}</p>}
      </div>
      <RecommendationCard
        recommendation={recommendation}
        options={options}
        onApprove={approveRecommendation}
        approved={approved}
      />
    </div>
  )
}
