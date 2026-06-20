export default function ConfidenceFlag({ confidence }) {
  if (confidence >= 0.7) return null
  return (
    <span className="badge" style={{ background: 'rgba(227,179,65,0.15)', color: 'var(--orange)' }}>
      ⚠ low confidence ({Math.round(confidence * 100)}%)
    </span>
  )
}
