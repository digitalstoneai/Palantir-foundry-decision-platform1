import ModelTag from '../shared/ModelTag.jsx'

function renderMarkdownBold(text) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((chunk, i) =>
    chunk.startsWith('**') && chunk.endsWith('**') ? <strong key={i}>{chunk.slice(2, -2)}</strong> : chunk,
  )
}

export default function BriefingPanel({ briefing, loading }) {
  if (loading) {
    return (
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Briefing</h3>
        <p style={{ color: 'var(--text-muted)' }}>Generating briefing...</p>
      </div>
    )
  }

  if (!briefing) {
    return (
      <div className="panel">
        <h3 style={{ marginTop: 0 }}>Briefing</h3>
        <p style={{ color: 'var(--text-muted)' }}>Select a role to generate a briefing.</p>
      </div>
    )
  }

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Briefing</h3>
      <ModelTag model={briefing.ai_model} />
      <p style={{ marginTop: 12, lineHeight: 1.5 }}>{renderMarkdownBold(briefing.content)}</p>
      <h4 style={{ marginBottom: 6 }}>Top Exceptions</h4>
      <ul style={{ margin: 0, paddingLeft: 18, color: 'var(--text-muted)', fontSize: 13 }}>
        {briefing.top_exceptions.map((id) => (
          <li key={id}>{id}</li>
        ))}
      </ul>
    </div>
  )
}
