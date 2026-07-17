import { AlertTriangle } from 'lucide-react'

function ConfidencePanel({ flags }) {
  if (!flags || flags.length === 0) return null
  return (
    <div className="card confidence-card">
      <div className="card-header">
        <div className="icon-badge warn"><AlertTriangle size={20} /></div>
        <div>
          <h2>Please Double-Check These</h2>
          <p className="card-sub">Lexi simplified these parts but wants you to verify the meaning</p>
        </div>
      </div>
      <ul className="flag-list">
        {flags.map((flag, i) => (
          <li key={i}><span className="flag-dot" />{flag}</li>
        ))}
      </ul>
    </div>
  )
}

export default ConfidencePanel