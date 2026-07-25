import { useState, useEffect, useCallback, useRef } from 'react'
import { api, ApiError } from '../lib/api'
import { STRINGS, hasBangla } from '../lib/strings'
import { loadHistory, saveHistory, newEntry } from '../lib/session'
import ControlRail from '../components/ControlRail'
import Editor from '../components/Editor'
import ModePicker from '../components/ModePicker'
import ResultView from '../components/ResultView'
import DeeperTabs from '../components/DeeperTabs'
import HistoryDrawer from '../components/HistoryDrawer'

const SIZES = { s: '14px', m: '16px', l: '19.5px' }
const LEADS = { 1: '1.7', 2: '2.0', 3: '2.35' }

const SAMPLE = 'Notwithstanding the aforementioned provisions, the party of the first part shall retain the right to terminate this agreement should circumstances materially deviate from the anticipated parameters set forth herein.'

export default function AppPage() {
  const [lang, setLang] = useState('en')
  const t = STRINGS[lang]

  const [size, setSize] = useState('m')
  const [leading, setLeading] = useState(1)
  const [theme, setTheme] = useState('light')
  const [health, setHealth] = useState('checking')

  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [docId, setDocId] = useState(null)

  const [modes, setModes] = useState([])
  const [mode, setMode] = useState('dyslexia')
  const [level, setLevel] = useState(3)

  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)

  const [chat, setChat] = useState([])
  const [history, setHistory] = useState(() => loadHistory())
  const [drawer, setDrawer] = useState(false)
  const entryId = useRef(null)

  const [audio, setAudio] = useState(null)
  const [wordIdx, setWordIdx] = useState(-1)
  const audioRef = useRef(null)
  const timerRef = useRef(null)
  const [recording, setRecording] = useState(false)
  const recRef = useRef(null)

  useEffect(() => { document.documentElement.setAttribute('data-theme', theme) }, [theme])
  useEffect(() => {
    document.documentElement.style.setProperty('--doc-size', SIZES[size])
    document.documentElement.style.setProperty('--doc-lh', LEADS[leading])
  }, [size, leading])

  useEffect(() => {
    api.health().then((d) => setHealth(d.llm_api === 'reachable' ? 'ok' : 'bad')).catch(() => setHealth('bad'))
    api.modes().then((d) => {
      if (d?.modes?.length) {
        setModes(d.modes)
        if (!d.modes.find((m) => m.id === mode)) setMode(d.modes[0].id)
      }
    }).catch(() => {})
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => { saveHistory(history) }, [history])

  const stopAudio = useCallback(() => {
    if (audioRef.current) { audioRef.current.pause(); audioRef.current = null }
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null }
    setAudio(null); setWordIdx(-1)
  }, [])

  const resetDoc = () => {
    setDocId(null); setResult(null); setError(null); setChat([])
    entryId.current = null; stopAudio()
  }
  const onText = (v) => { setText(v); setFile(null); resetDoc() }
  const onFile = (f) => { setFile(f); setText(''); resetDoc() }

  const ensureUploaded = async () => {
    if (docId) return docId
    const res = file ? await api.uploadFile(file) : await api.uploadText(text)
    setDocId(res.document_id)
    if (file) setText(res.extracted_text_preview || '')
    return res.document_id
  }

  const rewrite = async () => {
    if (!text.trim() && !file) return
    setBusy(true); setError(null); stopAudio()
    try {
      const id = await ensureUploaded()
      const data = await api.process(id, mode, level)
      setResult(data)
      const entry = newEntry({ text, mode, level, rewritten: data.rewritten_text, chat: [] })
      entryId.current = entry.id
      setHistory((h) => [entry, ...h])
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong.')
    } finally {
      setBusy(false)
    }
  }

  const askQuestion = useCallback(async (q) => {
    if (!docId) return { answer: t.emptyFirst, excerpt: null }
    try {
      const d = await api.ask(docId, q)
      return { answer: d.found_in_document ? d.answer : t.notFound, excerpt: d.supporting_excerpt || null }
    } catch (e) {
      return { answer: e instanceof ApiError ? e.message : 'Error.', excerpt: null }
    }
  }, [docId, t])

  const onChatChange = useCallback((next) => {
    setChat(next)
    if (!entryId.current) return
    setHistory((h) => h.map((it) => (it.id === entryId.current ? { ...it, chat: next } : it)))
  }, [])

  const restore = (item) => {
    stopAudio()
    setText(item.text); setFile(null); setDocId(null)
    setMode(item.mode); setLevel(item.level)
    setResult(item.rewritten ? { rewritten_text: item.rewritten, verification: null, stats: null } : null)
    setChat(item.chat || []); entryId.current = item.id
    setDrawer(false)
  }

  const readAloud = async () => {
    if (audio) return stopAudio()
    const src = result?.rewritten_text || text
    if (!src.trim()) return
    try {
      const d = await api.ttsTimed({ text: src, reading_level: level })
      const el = new Audio(`data:audio/mpeg;base64,${d.audio_base64}`)
      audioRef.current = el; setAudio(d)
      try {
        await el.play()
      } catch {
        setError('Audio is ready but the browser blocked playback. Click again.')
        return
      }
      timerRef.current = setInterval(() => {
        const now = el.currentTime
        setWordIdx(d.words.findIndex((w) => now >= w.start && now < w.end))
      }, 80)
      el.onended = stopAudio
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Audio failed.')
    }
  }

  const toggleDictate = async () => {
    if (recording) { recRef.current?.stop(); setRecording(false); return }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream)
      const chunks = []
      rec.ondataavailable = (e) => chunks.push(e.data)
      rec.onstop = async () => {
        stream.getTracks().forEach((tr) => tr.stop())
        try {
          const d = await api.transcribe(new Blob(chunks, { type: 'audio/webm' }))
          if (d.text) onText((text ? text + ' ' : '') + d.text)
        } catch { setError('Transcription failed.') }
      }
      recRef.current = rec; rec.start(); setRecording(true)
    } catch { setError('Microphone unavailable.') }
  }

  const isBn = hasBangla(result?.rewritten_text || text)
  const canRun = (text.trim().length > 0 || !!file) && !busy

  return (
    <>
      <ControlRail
        t={t} lang={lang} setLang={setLang}
        size={size} setSize={setSize}
        leading={leading} setLeading={setLeading}
        theme={theme} setTheme={setTheme}
        health={health}
        historyCount={history.length}
        onOpenHistory={() => setDrawer(true)}
      />

      <div className="split">
        <aside className="pane-l">
          <div className="pl-in">
            <Editor
              t={t} text={text} onText={onText} file={file} onFile={onFile}
              disabled={busy} onDictate={toggleDictate} recording={recording}
            />

            <ModePicker
              t={t} modes={modes} mode={mode}
              setMode={(m) => { setMode(m); setResult(null) }}
              level={level} setLevel={(l) => { setLevel(l); setResult(null) }}
            />

            <button className="bp big full" onClick={rewrite} disabled={!canRun}>
              {busy ? (<><span className="spin" />{t.rewriting}</>) : (
                <>{t.rewriteBtn}
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </>
              )}
            </button>

            {error && <div className="err" role="alert">{error}</div>}
          </div>
        </aside>

        <section className="pane-r">
          {!busy && !result && (
            <div className="blank">
              <div className="blank-in">
                <div className="blank-k">{t.blankK}</div>
                <h2>{t.blankH1}<br />{t.blankH2} <i>{t.blankEm}</i></h2>
                <p>{t.blankP}</p>
                <button className="bs" onClick={() => onText(SAMPLE)}>{t.trySample}</button>

                <div className="blank-steps">
                  {[
                    ['01', t.step1h, t.step1p],
                    ['02', t.step2h, t.step2p],
                    ['03', t.step3h, t.step3p],
                  ].map(([n, h, p]) => (
                    <div className="bstep" key={n}>
                      <span className="bstep-n">{n}</span>
                      <span><b>{h}</b>{p}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {(busy || result) && (
            <ResultView
              t={t} busy={busy} result={result} original={text}
              mode={mode} level={level} docId={docId} isBangla={isBn}
              words={audio?.words} wordIdx={wordIdx} modes={modes}
              onReadAloud={readAloud} audioOn={!!audio}
            />
          )}

          {result && (
            <DeeperTabs
              t={t} docId={docId}
              onAsk={askQuestion} chat={chat} setChat={onChatChange}
            />
          )}
        </section>
      </div>

      <HistoryDrawer
        open={drawer} onClose={() => setDrawer(false)}
        items={history} onPick={restore}
        onClear={() => { setHistory([]); setDrawer(false) }}
        t={t}
      />
    </>
  )
}