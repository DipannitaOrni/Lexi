import { useRef } from 'react'

export default function Editor({ t, text, onText, file, onFile, disabled, onDictate, recording }) {
  const inputRef = useRef(null)
  const words = text.trim() ? text.trim().split(/\s+/).length : 0

  return (
    <div className="ed">
      <label htmlFor="doc-input" className="sr-only">{t.placeholder}</label>
      <textarea
        id="doc-input"
        value={text}
        onChange={(e) => onText(e.target.value)}
        placeholder={t.placeholder}
        disabled={disabled}
      />
      <div className="ed-f">
        <span className="cnt">{file ? file.name : `${words} ${t.words}`}</span>

        <div className="ed-acts">
          <button
            className={`icon-btn ${recording ? 'rec' : ''}`}
            onClick={onDictate}
            disabled={disabled}
            title={recording ? t.listening : t.dictate}
            aria-pressed={recording}
          >
            <svg viewBox="0 0 20 20" fill="none" width="15" height="15">
              <rect x="7.4" y="2.4" width="5.2" height="9.6" rx="2.6" fill="currentColor" />
              <path d="M4.4 9.2a5.6 5.6 0 0011.2 0M10 14.8v2.8" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
            </svg>
            {recording && <span className="rec-dot" />}
          </button>

          <button className="ghost" onClick={() => inputRef.current?.click()} disabled={disabled}>
            {t.openFile}
          </button>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept=".txt,.pdf,.docx"
          style={{ display: 'none' }}
          onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f) }}
        />
      </div>
    </div>
  )
}