import { useState, useRef, useEffect } from 'react'

export default function AskPanel({ t, onAsk, chat, setChat }) {
  const [q, setQ] = useState('')
  const [busy, setBusy] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }) }, [chat])

  const send = async () => {
    const question = q.trim()
    if (!question || busy) return
    setQ(''); setBusy(true)
    const withQ = [...chat, { role: 'you', text: question }]
    setChat(withQ)
    const res = await onAsk(question)
    setChat([...withQ, { role: 'lexi', text: res.answer, excerpt: res.excerpt }])
    setBusy(false)
  }

  return (
    <section className="ask">
      <h2>{t.askTitle}</h2>
      <p className="hint">{t.askHint}</p>

      <div className="thread">
        {chat.length === 0 && !busy && (
          <div className="empty">{t.askPlaceholder}</div>
        )}
        {chat.map((m, i) => (
          <div className="turn" key={i}>
            <span className={`tk ${m.role === 'lexi' ? 'lx' : ''}`}>{m.role === 'lexi' ? 'Lexi' : t.you}</span>
            <div className="tb">
              {m.text}
              {m.excerpt && <div className="cite">{m.excerpt}</div>}
            </div>
          </div>
        ))}
        {busy && (
          <div className="turn">
            <span className="tk lx">Lexi</span>
            <div className="tb" style={{ color: 'var(--ink3)' }}>{t.thinking}</div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="ask-row">
        <label htmlFor="ask-input" className="sr-only">{t.askPlaceholder}</label>
        <input id="ask-input" value={q} onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && send()}
          placeholder={t.askPlaceholder} disabled={busy} />
        <button onClick={send} disabled={busy || !q.trim()}>{t.ask}</button>
      </div>
    </section>
  )
}