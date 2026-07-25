import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useReveal from '../hooks/useReveal'

const GROUPS = [
  ['Using Lexi', [
    ['What can I put into it?', 'Plain text, PDF, and Word documents — or just paste text straight in. You can also dictate out loud and let Lexi transcribe it for you.'],
    ['How long can a document be?', 'Long documents are split into chunks and rewritten piece by piece, so length is not a hard limit. Longer documents simply take longer to process.'],
    ['What do the five levels do?', 'They control how far the rewriting goes. Level 1 barely touches the text — mostly punctuation and sentence breaks. Level 5 rewrites aggressively for the simplest possible reading. Level 3 is a sensible default.'],
    ['Can I change mode after rewriting?', 'Yes. Pick a different mode or level and rewrite again — the document stays loaded, so it only re-runs the rewriting step.'],
  ]],
  ['Accuracy and trust', [
    ['How accurate is it?', 'Good, but never perfect. That is precisely why a second pass checks every rewrite against the original and flags anything where meaning may have drifted, showing both excerpts side by side so you can judge for yourself.'],
    ['What does the confidence score mean?', 'It is the verification pass reporting how closely the rewrite preserved the original meaning. A lower score is not a failure — it is a signal to read the flagged passages carefully.'],
    ['Should I rely on this for legal or medical documents?', 'Use it to understand them, not to replace them. Read the flags, check anything important against the original, and consult a professional for decisions that matter.'],
    ['Where do the chat answers come from?', 'Only from your document. If the answer is not in there, Lexi says so rather than guessing or filling in from general knowledge.'],
  ]],
  ['Privacy', [
    ['Is my document stored?', 'Only for the length of your session. Close the tab and it is gone. Nothing is written to a permanent store.'],
    ['Is my text used for training?', 'No.'],
    ['Does chat history persist?', 'Within your browser session, yes — you can revisit earlier documents and conversations from the history panel. It clears when you close the tab.'],
  ]],
  ['Language and access', [
    ['Does it work in Bangla?', 'Yes. Paste Bangla text and it rewrites in Bangla. You can ask questions in either language, and the interface itself switches between English and বাংলা.'],
    ['Can I export the result?', 'Yes — plain text, PDF, or audio. PDF export supports Bangla properly.'],
    ['Does it work with a screen reader?', 'Yes. Every control is labelled and keyboard reachable, and Screen Reader mode restructures documents specifically for listening rather than looking.'],
    ['Is it free?', 'Yes. No account, no sign-up, nothing to install.'],
  ]],
]

export default function FAQ() {
  const [open, setOpen] = useState('0-0')
  const nav = useNavigate()
  useReveal()

  return (
    <>
      <section className="sec" style={{ paddingBottom: 30 }}>
        <div className="sec-h">
          <div className="sec-k">FAQ</div>
          <h2>Questions, <i>answered</i>.</h2>
          <p>If something isn't covered here, the app itself is the fastest way to find out — nothing to sign up for.</p>
        </div>
      </section>

      {GROUPS.map(([group, items], gi) => (
        <section className="sec" style={{ paddingTop: 0, paddingBottom: 44 }} key={group}>
          <div className="sec-k rv" style={{ marginBottom: 18 }}>{group}</div>
          <div className="faq rv">
            {items.map(([q, a], qi) => {
              const key = `${gi}-${qi}`
              return (
                <div className={`q ${open === key ? 'op' : ''}`} key={q}>
                  <button className="q-h" onClick={() => setOpen(open === key ? '' : key)} aria-expanded={open === key}>
                    {q}<span className="q-i">+</span>
                  </button>
                  <div className="q-b"><div>{a}</div></div>
                </div>
              )
            })}
          </div>
        </section>
      ))}

      <div className="close">
        <div className="close-in rv">
          <h2>Still wondering?<br /><i>Just try it.</i></h2>
          <p>It takes about ten seconds to find out whether it helps.</p>
          <button className="bp" onClick={() => nav('/app')}>
            Open Lexi
            <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </>
  )
}