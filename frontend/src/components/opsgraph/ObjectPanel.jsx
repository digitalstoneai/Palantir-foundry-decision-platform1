const STATUS_COLOR = {
  nominal: 'var(--blue)',
  at_risk: 'var(--orange)',
  degraded: 'var(--orange)',
  critical: 'var(--red)',
}

export default function ObjectPanel({ objects, selectedId, onSelect }) {
  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Objects</h3>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {objects.map((obj) => (
          <li key={obj.id} style={{ marginBottom: 6 }}>
            <button
              onClick={() => onSelect(obj.id)}
              style={{
                width: '100%',
                textAlign: 'left',
                background: obj.id === selectedId ? 'var(--surface-3)' : 'var(--surface-2)',
                border: '1px solid var(--border)',
                borderRadius: 4,
                color: 'var(--text)',
                padding: '8px 10px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                gap: 8,
              }}
            >
              <span>{obj.name}</span>
              <span
                className="badge"
                style={{ background: `${STATUS_COLOR[obj.status]}26`, color: STATUS_COLOR[obj.status] }}
              >
                {obj.status}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
