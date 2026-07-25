import { useState, useRef, useEffect } from 'react'
import { api } from '../lib/api'
import Mermaid from './Mermaid'

export default function DeeperTabs({ t, docId, onAsk, chat, setChat }) {
  const [tab, setTab] = useState('ask')
  const [cache, setCache] = useState({})
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState(null)
  const [fcIdx, setFcIdx] = useState(0)
  const [flipped, setFlipped] = useState(false)

  const [q, setQ] = useState('')
  const [asking, setAsking] = useState(false)
  const endRef = useRef(null)
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }) }, [chat, asking])

  const open = async (key) => {
    setTab(key); setErr(null)
    if (key === 'ask' || cache[key]) return
    setLoading(true)
    try {
      const fn = {
        key_points: () => api.keyPoints(docId),
        glossary: () => api.glossary(docId),
        flashcards: () => api.flashcards(docId),
        visualize: () => api.visualize(docId),
      }[key]
      const data = await fn()
      setCache((c) => ({ ...c, [key]: data }))
      if (key === 'flashcards') { setFcIdx(0); setFlipped(false) }
    } catch (e) { setErr(e.message) } finally { setLoading(false) }
  }

  const ask = async (question) => {
    if (!question || asking) return
    setQ(''); setAsking(true)
    const withQ = [...chat, { role: 'you', text: question }]
    setChat(withQ)
    const res = await onAsk(question)
    setChat([...withQ, { role: 'lexi', text: res.answer, excerpt: res.excerpt }])
    setAsking(false)
  }

  const TABS = [
    ['ask', t.ask, '◆'],
    ['key_points', t.keyPoints, '❶'],
    ['glossary', t.glossary, '§'],
    ['flashcards', t.flashcards, '▤'],
    ['visualize', t.diagram, '◈'],
  ]

  const data = cache[tab]

  return (
    <section className="deeper">
      <div className="dt-bar" role="tablist">
        {TABS.map(([k, label, ico]) => (
          <button key={k} className={`dt ${tab === k ? 'on' : ''}`} onClick={() => open(k)} role="tab" aria-selected={tab === k}>
            <span className="dt-i">{ico}</span>{label}
          </button>
        ))}
      </div>

      <div className="dt-body">
        {err && <div className="err">{err}</div>}

        {loading && (
          <div className="dt-load">
            <div className="skel" style={{ width: '88%' }} />
            <div className="skel" style={{ width: '72%' }} />
            <div className="skel" style={{ width: '80%' }} />
          </div>
        )}

       {tab === 'ask' && (
          <div className="askbox">
            <div className="thread">
              {chat.length === 0 && !asking && (
                <div className="ask-empty">
                  <div className="ask-orb">
                    <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
                      <path d="M4 5h16M4 11h11M4 17h7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
                    </svg>
                  </div>
                  <p>{t.askHint}</p>
                  <div className="ask-sugg">
                    {[t.suggest1, t.suggest2, t.suggest3].map((s) => (
                      <button key={s} onClick={() => ask(s)}>{s}</button>
                    ))}
                  </div>
                </div>
              )}

              {chat.map((m, i) => (
                <div className={`row ${m.role}`} key={i}>
                  {m.role === 'lexi' && <span className="av">L</span>}
                  <div className="bub-wrap">
                    <div className={`bub ${m.role}`}>{m.text}</div>
                    {m.excerpt && (
                      <div className="src">
                        <span className="src-k">from your document</span>
                        {m.excerpt}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {asking && (
                <div className="row lexi">
                  <span className="av">L</span>
                  <div className="bub-wrap">
                    <div className="bub lexi typing"><span /><span /><span /></div>
                  </div>
                </div>
              )}
              <div ref={endRef} />
            </div>

            <div className="ask-row">
              <input value={q} onChange={(e) => setQ(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && ask(q.trim())}
                placeholder={t.askPlaceholder} disabled={asking} aria-label={t.askPlaceholder} />
              <button onClick={() => ask(q.trim())} disabled={asking || !q.trim()} aria-label={t.ask}>
                <svg viewBox="0 0 20 20" fill="none" width="17" height="17">
                  <path d="M3 10l14-6-6 14-2.2-5.8L3 10z" stroke="currentColor" strokeWidth="1.9" strokeLinejoin="round" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {!loading && tab === 'flashcards' && data?.flashcards?.length > 0 && (
          <div className="fc-wrap">
            <div className="fc-stage">
              <div
                className={`fc-card ${flipped ? 'flip' : ''}`}
                onClick={() => setFlipped((f) => !f)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), setFlipped((f) => !f))}
                aria-label={flipped ? t.answer : t.question}
              >
                <div className="fc-face fc-front">
                  <span className="fc-k">{t.question}</span>
                  <span className="fc-q">{data.flashcards[fcIdx].question}</span>
                  <span className="fc-hint">
                    <svg viewBox="0 0 20 20" fill="none" width="13" height="13">
                      <path d="M3 10a7 7 0 0111.9-5M17 10a7 7 0 01-11.9 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                      <path d="M15 2v3.4h-3.4M5 18v-3.4h3.4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    {t.flip}
                  </span>
                </div>

                <div className="fc-face fc-back">
                  <span className="fc-k">{t.answer}</span>
                  <span className="fc-a">{data.flashcards[fcIdx].answer}</span>
                  <span className="fc-hint">
                    <svg viewBox="0 0 20 20" fill="none" width="13" height="13">
                      <path d="M3 10a7 7 0 0111.9-5M17 10a7 7 0 01-11.9 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                      <path d="M15 2v3.4h-3.4M5 18v-3.4h3.4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                    {t.flip}
                  </span>
                </div>
              </div>
            </div>

            <div className="fc-nav">
              <button
                onClick={() => { setFcIdx((i) => (i - 1 + data.flashcards.length) % data.flashcards.length); setFlipped(false) }}
                aria-label="Previous"
              >‹</button>

              <div className="fc-pips">
                {data.flashcards.map((_, i) => (
                  <button
                    key={i}
                    className={`pip ${i === fcIdx ? 'on' : ''}`}
                    onClick={() => { setFcIdx(i); setFlipped(false) }}
                    aria-label={`Card ${i + 1}`}
                  />
                ))}
              </div>

              <button
                onClick={() => { setFcIdx((i) => (i + 1) % data.flashcards.length); setFlipped(false) }}
                aria-label="Next"
              >›</button>
            </div>

            <div className="fc-count">{fcIdx + 1} / {data.flashcards.length}</div>
          </div>
        )}
      </div>
    </section>
  )
}