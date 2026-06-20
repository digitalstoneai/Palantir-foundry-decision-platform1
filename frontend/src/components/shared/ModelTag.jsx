export default function ModelTag({ model }) {
  return (
    <span className="badge" style={{ background: 'rgba(188,140,255,0.15)', color: 'var(--purple)' }}>
      {model}
    </span>
  )
}
