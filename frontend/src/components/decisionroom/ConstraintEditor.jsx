const DEFAULT_THRESHOLDS = { cost: 5000, service: 0.3, risk: 0.5 }

export default function ConstraintEditor({ constraints, onChange }) {
  const updateWeight = (name, weight) => {
    onChange(constraints.map((c) => (c.name === name ? { ...c, weight } : c)))
  }

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Constraint Weights</h3>
      {constraints.map((c) => (
        <div key={c.name} style={{ marginBottom: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
            <span style={{ textTransform: 'capitalize' }}>{c.name}</span>
            <span style={{ color: 'var(--text-muted)' }}>
              weight {c.weight.toFixed(2)} · threshold {DEFAULT_THRESHOLDS[c.name]}
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={c.weight}
            onChange={(e) => updateWeight(c.name, parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>
      ))}
    </div>
  )
}

export { DEFAULT_THRESHOLDS }
