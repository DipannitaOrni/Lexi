const FALLBACK = [
  { id: 'dyslexia', label: 'Dyslexia-Friendly', description: 'Short sentences, simple words, clear spacing.' },
  { id: 'focus', label: 'Focus Mode', description: 'Key points up front, bullets, bolded essentials.' },
  { id: 'screen_reader', label: 'Screen Reader', description: 'Speech-friendly punctuation and structure.' },
  { id: 'non_native', label: 'Non-Native English', description: 'Simpler vocabulary with inline clarifications.' },
  { id: 'civic', label: 'Civic / Forms', description: 'Requirements, deadlines, fees, and steps.' },
  { id: 'dyscalculia', label: 'Dyscalculia', description: 'Numbers and tables in plain language.' },
  { id: 'low_vision', label: 'Low Vision', description: 'Short scannable paragraphs, lists over tables.' },
]

const GLYPH = {
  dyslexia: (
    <svg viewBox="0 0 24 24" fill="none">
      <rect x="3" y="5" width="18" height="2.6" rx="1.3" fill="currentColor" />
      <rect x="3" y="10.7" width="12" height="2.6" rx="1.3" fill="currentColor" opacity=".62" />
      <rect x="3" y="16.4" width="7" height="2.6" rx="1.3" fill="currentColor" opacity=".38" />
    </svg>
  ),
  focus: (
    <svg viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" opacity=".3" />
      <circle cx="12" cy="12" r="5" stroke="currentColor" strokeWidth="2" opacity=".6" />
      <circle cx="12" cy="12" r="1.8" fill="currentColor" />
    </svg>
  ),
  screen_reader: (
    <svg viewBox="0 0 24 24" fill="none">
      <path d="M4 9.5h3.5L12 6v12l-4.5-3.5H4z" fill="currentColor" />
      <path d="M16 9.4a4 4 0 010 5.2M18.6 7a7.5 7.5 0 010 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" opacity=".55" />
    </svg>
  ),
  non_native: (
    <svg viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
      <path d="M3 12h18M12 3c2.6 2.6 2.6 15.4 0 18M12 3c-2.6 2.6-2.6 15.4 0 18" stroke="currentColor" strokeWidth="1.7" opacity=".55" />
    </svg>
  ),
  civic: (
    <svg viewBox="0 0 24 24" fill="none">
      <rect x="5" y="3" width="14" height="18" rx="2.5" stroke="currentColor" strokeWidth="2" />
      <path d="M9 9h6M9 13h6M9 17h3" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" opacity=".6" />
    </svg>
  ),
  dyscalculia: (
    <svg viewBox="0 0 24 24" fill="none">
      <rect x="4" y="13" width="4" height="8" rx="1.4" fill="currentColor" opacity=".45" />
      <rect x="10" y="8" width="4" height="13" rx="1.4" fill="currentColor" opacity=".7" />
      <rect x="16" y="4" width="4" height="17" rx="1.4" fill="currentColor" />
    </svg>
  ),
  low_vision: (
    <svg viewBox="0 0 24 24" fill="none">
      <path d="M2 12s3.8-6.5 10-6.5S22 12 22 12s-3.8 6.5-10 6.5S2 12 2 12z" stroke="currentColor" strokeWidth="2" />
      <circle cx="12" cy="12" r="3" fill="currentColor" />
    </svg>
  ),
}

export default function ModePicker({ t, modes, mode, setMode, level, setLevel }) {
  const base = modes.length ? modes : FALLBACK
  const list = base.map((m) => ({
    ...m,
    label: t.modeNames?.[m.id] || m.label,
    description: t.modeDescs?.[m.id] || m.description,
  }))

  return (
    <>
      <div className="sec-h2">
        <h2>{t.rewriteFor}</h2>
        <span>{t.rewriteForNote}</span>
      </div>

      <div className="modes" role="radiogroup" aria-label={t.rewriteFor}>
        {list.map((m, i) => (
          <button
            key={m.id}
            className={`mode ${mode === m.id ? 'on' : ''}`}
            onClick={() => setMode(m.id)}
            role="radio"
            aria-checked={mode === m.id}
            style={{ '--i': i }}
          >
            <span className="mode-ico">{GLYPH[m.id] || GLYPH.dyslexia}</span>
            <span className="mode-txt">
              <span className="mn">{m.label}</span>
              <span className="md">{m.description}</span>
            </span>
            <span className="mode-tick" aria-hidden="true">
              <svg viewBox="0 0 16 16" fill="none"><path d="M3 8.5l3.2 3.2L13 5" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </span>
          </button>
        ))}
      </div>

      <div className="lvl">
        <div className="lvl-top">
          <span className="lvl-k">{t.howFar}</span>
          <span className="lvl-val">{t.levels[level - 1]}</span>
        </div>
        <input
          className="slider"
          type="range" min="1" max="5" step="1"
          value={level}
          onChange={(e) => setLevel(Number(e.target.value))}
          aria-label={t.howFar}
          aria-valuetext={`${level} — ${t.levels[level - 1]}`}
          style={{ '--fill': `${((level - 1) / 4) * 100}%` }}
        />
        <div className="lvl-ticks">
          {[1, 2, 3, 4, 5].map((n) => (
            <span key={n} className={n <= level ? 'on' : ''}>{n}</span>
          ))}
        </div>
      </div>
    </>
  )
}