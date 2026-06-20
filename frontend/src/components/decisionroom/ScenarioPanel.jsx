export default function ScenarioPanel({ events, eventOptionCounts, selectedEventId, onSelectEvent, options }) {
  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Event</h3>
      <select
        value={selectedEventId ?? ''}
        onChange={(e) => onSelectEvent(e.target.value)}
        style={{
          width: '100%',
          background: 'var(--surface-2)',
          color: 'var(--text)',
          border: '1px solid var(--border)',
          borderRadius: 4,
          padding: 8,
          marginBottom: 16,
        }}
      >
        <option value="" disabled>
          Select an event...
        </option>
        {events.map((evt) => {
          const hasOptions = (eventOptionCounts[evt.id] ?? 0) > 0
          return (
            <option key={evt.id} value={evt.id} disabled={!hasOptions}>
              [{evt.severity}] {evt.description.slice(0, 50)}
              {!hasOptions ? ' — no response options' : ''}
            </option>
          )
        })}
      </select>

      <h3>Response Options</h3>
      {!options.length && (
        <p style={{ color: 'var(--text-muted)' }}>
          No response options are defined for this event — DecisionRoom only has options seeded for the
          urgent conveyor failure event.
        </p>
      )}
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {options.map((opt) => (
          <li key={opt.id} className="panel" style={{ marginBottom: 8, padding: 10 }}>
            <strong>{opt.label}</strong>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '6px 0' }}>{opt.description}</p>
            <div style={{ display: 'flex', gap: 12, fontSize: 12, color: 'var(--text-muted)' }}>
              <span>cost: ${opt.cost_impact}</span>
              <span>service: {opt.service_impact}</span>
              <span>risk: {opt.risk_score}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
