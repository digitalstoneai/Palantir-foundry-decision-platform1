import ConfidenceFlag from '../shared/ConfidenceFlag.jsx'
import ModelTag from '../shared/ModelTag.jsx'

export default function RecommendationCard({ recommendation, options, onApprove, approved }) {
  if (!recommendation) {
    return (
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Recommendation</h3>
        <p style={{ color: 'var(--text-muted)' }}>Select an event and request a recommendation.</p>
      </div>
    )
  }

  const recommendedOption = options.find((o) => o.id === recommendation.recommended_option_id)

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Recommendation</h3>
      <div style={{ display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' }}>
        <ModelTag model={recommendation.ai_model} />
        <ConfidenceFlag confidence={recommendation.confidence} />
        {recommendation.degraded_mode && (
          <span className="badge" style={{ background: 'rgba(227,179,65,0.15)', color: 'var(--orange)' }}>
            ⚠ degraded
          </span>
        )}
      </div>

      <p style={{ fontSize: 15 }}>
        <strong>{recommendedOption?.label ?? recommendation.recommended_option_id}</strong>
      </p>
      <p>{recommendation.rationale}</p>
      <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>{recommendation.tradeoff_summary}</p>

      <h4 style={{ marginBottom: 6 }}>Constraint Scores</h4>
      <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: 13 }}>
        {Object.entries(recommendation.constraint_scores).map(([name, score]) => (
          <li key={name} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ textTransform: 'capitalize', color: 'var(--text-muted)' }}>{name}</span>
            <span>{score.toFixed(2)}</span>
          </li>
        ))}
      </ul>

      <button
        onClick={onApprove}
        disabled={approved}
        style={{
          marginTop: 14,
          width: '100%',
          background: approved ? 'var(--surface-3)' : 'var(--purple)',
          color: approved ? 'var(--text-muted)' : '#0d1117',
          border: 'none',
          borderRadius: 4,
          padding: '8px 12px',
          fontWeight: 600,
          cursor: approved ? 'default' : 'pointer',
        }}
      >
        {approved ? '✓ Approved' : 'Approve Recommendation'}
      </button>
    </div>
  )
}
