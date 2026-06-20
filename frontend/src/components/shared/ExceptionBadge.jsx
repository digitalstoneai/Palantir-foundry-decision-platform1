const SEVERITY_COLOR = {
  urgent: 'var(--red)',
  high: 'var(--orange)',
  normal: 'var(--blue)',
}

export default function ExceptionBadge({ severity }) {
  const color = SEVERITY_COLOR[severity] ?? 'var(--text-muted)'
  return (
    <span className="badge" style={{ background: `${color}26`, color }}>
      {severity}
    </span>
  )
}
