import { Type, Target, Volume2, Globe, Check } from 'lucide-react'

const MODES = [
  { id: 'dyslexia', label: 'Dyslexia', Icon: Type, desc: 'Shorter sentences, simpler words' },
  { id: 'focus', label: 'Focus / ADHD', Icon: Target, desc: 'Chunked sections, key terms bold' },
  { id: 'screenreader', label: 'Screen Reader', Icon: Volume2, desc: 'Clean structure, logical order' },
  { id: 'nonnative', label: 'Simple English', Icon: Globe, desc: 'Plain language, no jargon' },
]

function ModeSelector({ mode, setMode }) {
  return (
    <div className="card">
      <div className="card-header">
        <div className="icon-badge"><Target size={20} /></div>
        <div>
          <h2>Choose Your Reading Mode</h2>
          <p className="card-sub">Lexi adapts the rewriting style to your specific need</p>
        </div>
      </div>
      <div className="mode-grid" role="group" aria-label="Reading mode">
        {MODES.map(({ id, label, Icon, desc }) => (
          <button
            key={id}
            onClick={() => setMode(id)}
            aria-pressed={mode === id}
            className={`mode-btn ${mode === id ? 'selected' : ''}`}
          >
            <span className="mode-ico"><Icon size={24} /></span>
            <span className="mode-label">{label}</span>
            <span className="mode-desc">{desc}</span>
            {mode === id && <span className="mode-check"><Check size={12} /></span>}
          </button>
        ))}
      </div>
    </div>
  )
}

export default ModeSelector