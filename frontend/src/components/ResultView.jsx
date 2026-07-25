import { useState } from 'react'
import { api } from '../lib/api'

function Stat({ label, now, was, better }) {
  const improved = better && was != null && now < was
  return (
    <div className="dcell">
      <div className="dk">{label}</div>
      <div className="dv">
        <span className={improved ? 'good' : ''}>{now ?? '—'}</span>
        {was != null && <span className="was">was {was}</span>}
      </div>
    </div>
  )
}

function Rich({ text }) {
  const blocks = []
  let list = null

  const inline = (s) =>
    s.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
      part.startsWith('**') && part.endsWith('**')
        ? <b key={i}>{part.slice(2, -2)}</b>
        : <span key={i}>{part}</span>
    )

  ;(text || '').split('\n').forEach((raw, i) => {
    const line = raw.trim()

    if (!line) { if (list) { blocks.push(list); list = null } return }

    const num = line.match(/^(\d+)[.)]\s+(.*)$/)
    const bul = line.match(/^[-•*]\s+(.*)$/)

    if (num || bul) {
      const body = num ? num[2] : bul[1]
      if (!list) list = { type: num ? 'ol' : 'ul', items: [], key: `l${i}` }
      list.items.push(body)
      return
    }

    if (list) { blocks.push(list); list = null }

    if (/^#{1,3}\s/.test(line)) {
      blocks.push({ type: 'h', text: line.replace(/^#{1,3}\s/, ''), key: `h${i}` })
      return
    }

    blocks.push({ type: 'p', text: line, key: `p${i}` })
  })
  if (list) blocks.push(list)

  return (
    <div className="doc rich">
      {blocks.map((b) => {
        if (b.type === 'h') return <h4 key={b.key} className="d-h">{inline(b.text)}</h4>
        if (b.type === 'p') return <p key={b.key} className="d-p">{inline(b.text)}</p>
        const Tag = b.type === 'ol' ? 'ol' : 'ul'
        return (
          <Tag key={b.key} className={`d-list ${b.type}`}>
            {b.items.map((it, j) => <li key={j}>{inline(it)}</li>)}
          </Tag>
        )
      })}
    </div>
  )
}

function Highlighted({ text, words, wordIdx }) {
  if (!words || wordIdx < 0) return <Rich text={text} />
  return (
    <div className="doc">
      {words.map((w, i) => (
        <span key={i} className={i === wordIdx ? 'w-on' : ''}>{w.word} </span>
      ))}
    </div>
  )
}

export default function ResultView({
  t, busy, result, original, mode, level, docId, isBangla, words, wordIdx, modes,
  onReadAloud, audioOn,
}) {
  const [copied, setCopied] = useState(false)
  const [downloading, setDownloading] = useState(null)

  if (busy && !result) {
    return (
      <section className="res">
        <div className="res-h"><h2>{t.whatChanged}</h2></div>
        <div style={{ padding: '26px 0' }}>
          <div className="skel" style={{ width: '92%' }} />
          <div className="skel" style={{ width: '78%' }} />
          <div className="skel" style={{ width: '85%' }} />
          <div className="skel" style={{ width: '60%' }} />
        </div>
      </section>
    )
  }

  if (!result) return null

  const s = result.stats
  const o = s?.original || {}
  const r = s?.rewritten || {}
  const v = result.verification
  const warns = v?.warnings || []
  const modeLabel = t.modeNames?.[mode] || modes.find((m) => m.id === mode)?.label || mode
  const restored = !s && !v

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(result.rewritten_text)
      setCopied(true); setTimeout(() => setCopied(false), 1800)
    } catch { /* clipboard blocked */ }
  }

  const download = async (fmt) => {
    if (!docId) return
    setDownloading(fmt)
    try {
      const blob = await api.exportDoc(docId, mode, level, fmt)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `lexi-${mode}.${fmt === 'audio' ? 'mp3' : fmt}`
      a.click()
      URL.revokeObjectURL(url)
    } catch { /* surfaced by caller */ }
    finally { setDownloading(null) }
  }

  return (
    <section className="res">
      <div className="res-h">
        <h2>{t.whatChanged}</h2>
        <div className="res-a">
          <button className={`play-btn ${audioOn ? 'on' : ''}`} onClick={onReadAloud}>
            {audioOn ? (
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12">
                <rect x="3" y="3" width="4" height="10" rx="1" />
                <rect x="9" y="3" width="4" height="10" rx="1" />
              </svg>
            ) : (
              <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12">
                <path d="M4.5 3.2v9.6l8-4.8z" />
              </svg>
            )}
            {audioOn ? t.stop : t.readAloud}
          </button>
          <button onClick={copy}>{copied ? t.copied : t.copy}</button>
          <button onClick={() => download('txt')} disabled={!docId || downloading === 'txt'}>.txt</button>
          <button
            onClick={() => download('pdf')}
            disabled={!docId || downloading === 'pdf'}
            title={isBangla ? t.pdfBanglaWarn : undefined}
          >.pdf</button>
          <button onClick={() => download('audio')} disabled={!docId || downloading === 'audio'}>.mp3</button>
        </div>
      </div>

      {s && (
        <div className="delta">
          <Stat label={t.grade} now={r.flesch_kincaid_grade} was={o.flesch_kincaid_grade} better />
          <Stat label={t.wps} now={r.avg_words_per_sentence} was={o.avg_words_per_sentence} better />
          <Stat label={t.sentences} now={r.sentence_count} was={o.sentence_count} />
          <Stat label={t.confidence} now={v ? v.confidence_score : '—'} />
        </div>
      )}

      <div className="panes">
        <div className="pane old">
          <div className="pk">{t.asWritten}</div>
          <div className="doc">{original}</div>
        </div>
        <div className="pane">
          <div className="pk new">{t.rewritten} · {modeLabel} · {t.level} {level}</div>
          <Highlighted text={result.rewritten_text} words={words} wordIdx={wordIdx} />
        </div>
      </div>

      {!restored && (
        <div className="flags">
          <div className="fk">{t.flags}</div>
          {warns.length === 0 ? (
            <div className="ok-note">{t.noFlags}</div>
          ) : (
            warns.map((w, i) => (
              <div className="flag" key={i}>
                <span className="fn">{String(i + 1).padStart(2, '0')}</span>
                <div>
                  <div className="ft-x">{w.description}</div>
                  {(w.original_excerpt || w.rewritten_excerpt) && (
                    <div className="fx">
                      <div>{w.original_excerpt}</div>
                      <div>{w.rewritten_excerpt}</div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </section>
  )
}