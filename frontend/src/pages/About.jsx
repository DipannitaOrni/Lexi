import { useNavigate } from 'react-router-dom'
import useReveal from '../hooks/useReveal'

export default function About() {
  const nav = useNavigate()
  useReveal()

  return (
    <>
      <section className="sec" style={{ paddingBottom: 40 }}>
        <div className="sec-h">
          <div className="sec-k">About</div>
          <h2>Text was never written<br />with <i>every reader</i> in mind.</h2>
          <p>
            Forms, contracts, medical letters, coursework — almost all of it assumes
            one kind of reader. Someone who can hold long sentences in working memory,
            decode unfamiliar words on the fly, and follow structure that only exists visually.
          </p>
        </div>

        <div className="cols">
          {[
            ['01', 'The problem', 'Existing tools treat every reading difficulty as the same problem. One "simplify" button, one output. But a dyslexic reader and a screen-reader user need almost opposite things from the same paragraph.'],
            ['02', 'The approach', 'Seven modes that genuinely restructure text differently, and five levels controlling how far to go. Which barrier and how much help are separate questions, so they get separate controls.'],
            ['03', 'The caution', "Simplification can quietly change meaning — and the people who most need it are least placed to notice. So every rewrite is checked, and anything uncertain is flagged with both versions shown."],
          ].map(([n, h, p]) => (
            <div className="col rv" key={n}>
              <div className="col-n">{n}</div>
              <h3>{h}</h3>
              <p>{p}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="sec" style={{ paddingTop: 40 }}>
        <div className="sec-h rv">
          <div className="sec-k">Who it's for</div>
          <h2>Written for people who<br />are usually <i>an afterthought</i>.</h2>
        </div>

        <div className="show rv">
          <div className="show-b" style={{ gridTemplateColumns: '1fr' }}>
            <div className="sb">
              {[
                ['Dyslexia', 'Long sentences and dense blocks make decoding harder. Shorter sentences, common words, and generous spacing measurably help.'],
                ['ADHD and focus', 'A wall of text is an executive-function problem before it is a comprehension one. Chunked sections with the essentials marked make it approachable.'],
                ['Screen reader users', 'Scanned documents and visual-only formatting are unreadable by ear. Real structure and speech-friendly punctuation change that.'],
                ['Non-native readers', 'The concepts are rarely the barrier — idiom, register, and jargon are. Plain vocabulary with terms explained inline keeps meaning intact.'],
                ['Civic forms', 'Bureaucratic language hides deadlines, fees, and required documents. Pulling them out changes whether someone gets a benefit they are owed.'],
                ['Dyscalculia', 'Numbers, tables, and percentages presented as prose are hard to hold. Explaining them in plain language makes them usable.'],
                ['Low vision', 'Long paragraphs and wide tables are hard to track at magnification. Short scannable blocks and lists work far better.'],
              ].map(([t, d], i) => (
                <div className="kp-i" key={t}>
                  <span className="kp-n">{String(i + 1).padStart(2, '0')}</span>
                  <span>
                    <span style={{ fontFamily: 'var(--serif)', fontSize: 17, fontWeight: 600, display: 'block', marginBottom: 4 }}>{t}</span>
                    <span style={{ fontSize: 14.5, color: 'var(--ink2)', fontWeight: 300, lineHeight: 1.7 }}>{d}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="sec" style={{ paddingTop: 0 }}>
        <div className="sec-h rv">
          <div className="sec-k">How it works</div>
          <h2>Three passes, <i>not one</i>.</h2>
        </div>
        <div className="cols">
          {[
            ['I', 'Read and split', 'Your document is extracted and split into chunks small enough to be rewritten carefully, rather than summarised loosely.'],
            ['II', 'Rewrite', 'Each chunk is rewritten against the rules for your chosen mode and level — sentence length, structure, vocabulary, emphasis.'],
            ['III', 'Verify', 'A separate pass compares rewrite to original and reports a confidence score plus any passage where meaning may have shifted.'],
          ].map(([n, h, p]) => (
            <div className="col rv" key={n}>
              <div className="col-n">{n}</div>
              <h3>{h}</h3>
              <p>{p}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="close">
        <div className="close-in rv">
          <h2>Try it with something<br /><i>actually difficult.</i></h2>
          <p>A government form. A contract. A chapter you've reread three times.</p>
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