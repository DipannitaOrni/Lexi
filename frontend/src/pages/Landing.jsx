import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useReveal from '../hooks/useReveal'

const TYPED = 'The rules above still apply. But the first person can §still end this agreement§. They can do this if things change a lot from what was expected.'

const SHOWCASE = [
  ['Dyslexia', 'You must send Form A. You must pay $50. You must show two IDs. Do this before March 1.'],
  ['Focus', '§Three things, before March 1:§\n\n1. Send §Form A§\n2. Pay the §$50§ fee\n3. Show §two IDs§'],
  ['Screen reader', 'Applicants must do three things. First, submit Form A. Second, pay a fee of fifty dollars. Third, provide two forms of identification. The deadline is March the first.'],
  ['Non Native', 'You need to send Form A. You need to pay a fee of $50. You need to bring two ID documents. Finish all of this before 1 March.'],
  ['Civic forms', '§What to do:§ Submit Form A · Pay $50 · Bring 2 IDs\n§Deadline:§ March 1\n§Cost:§ $50'],
  ['Dyscalculia', '§Form A:§ submit\n§Fee:§ $50 (fifty dollars)\n§IDs needed:§ 2\n§Deadline:§ March 1 (the 1st day of March)'],
  ['Low vision', 'Submit Form A.\n\nPay $50.\n\nBring two IDs.\n\nDo this by March 1.'],
]

function render(s) {
  return s.split('§').map((part, i) =>
    i % 2 ? <b key={i}>{part}</b> : <span key={i}>{part}</span>
  )
}

export default function Landing() {
  const nav = useNavigate()
  const [typed, setTyped] = useState('')
  const [tab, setTab] = useState(0)
  const [openQ, setOpenQ] = useState(0)
  useReveal()

  useEffect(() => {
    let n = 0
    let id
    const step = () => {
      setTyped(TYPED.slice(0, n))
      if (n++ < TYPED.length) id = setTimeout(step, 18)
    }
    step()
    return () => clearTimeout(id)
  }, [])

  const faqs = [
    ['Is my document stored anywhere?', "Only for as long as your session lasts. Close the tab and it's gone — nothing is written to a permanent store, and nothing is used for training."],
    ['How accurate is the rewriting?', 'Good, but never perfect — which is exactly why every rewrite is checked by a second pass that flags where meaning may have drifted. For anything legal or medical, read the flags and check them against the original.'],
    ['Does it work in Bangla?', 'Yes. Paste Bangla text and it rewrites in Bangla. You can ask questions in either language, and the whole interface switches between English and বাংলা.'],
  ]

  return (
    <>
      <section className="hero">
        <div>
          <div className="kicker">Reading, on your terms</div>
          <h1 className="hd">Text that adapts<br />to <i>you</i>.</h1>
          <p className="hero-p">
            Paste a form, a contract, a chapter. Lexi rewrites it for the way you
            read — then shows exactly what changed, and tells you where it wasn't certain.
          </p>
          <div className="hero-btns">
            <button className="bp" onClick={() => nav('/app')}>
              Start reading
              <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
                <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
            <button
              className="bs"
              onClick={() => document.getElementById('example')?.scrollIntoView({ behavior: 'smooth' })}
            >
              See an example
            </button>
          </div>
          <div className="hero-meta">
            <div><div className="hm-v">7</div><div className="hm-k">reading modes</div></div>
            <div><div className="hm-v">5</div><div className="hm-k">levels of simplification</div></div>
            <div><div className="hm-v">2</div><div className="hm-k">languages</div></div>
          </div>
        </div>

        <div className="art">
          <div className="badge bd1"><span className="bg-v">↓62%</span><span className="bg-k">reading<br />difficulty</span></div>
          <div className="badge bd2"><span className="bg-v">2</span><span className="bg-k">passages<br />flagged</span></div>
          <div style={{ position: 'relative' }}>
            <div className="sheet b1" />
            <div className="sheet b2" />
            <div className="sheet fr">
              <div className="sh-k"><span>Original</span><span className="tag">dense</span></div>
              <div>
                <div className="ln" style={{ width: '100%' }} />
                <div className="ln" style={{ width: '97%' }} />
                <div className="ln" style={{ width: '99%' }} />
                <div className="ln" style={{ width: '64%' }} />
              </div>
              <div className="hr-div">
                <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
                  <path d="M8 3v10M4 9l4 4 4-4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <div className="sh-k"><span>Rewritten · dyslexia</span><span className="tag">clear</span></div>
              <div className="out-txt">{render(typed)}<span className="cur" /></div>
            </div>
          </div>
        </div>
      </section>

      <section className="sec">
        <div className="sec-h rv">
          <div className="sec-k">The idea</div>
          <h2>One button marked <i>simplify</i> was never going to be enough.</h2>
          <p>A dyslexic reader needs shorter sentences. Someone with ADHD needs the wall broken into pieces. A screen-reader user needs real structure, not visual formatting. These are different problems. Lexi treats them that way.</p>
        </div>
        <div className="cols">
          {[
            ['01', 'Seven distinct rewrites', 'Not one output relabelled seven times. Each mode restructures the text differently — sentence length, ordering, emphasis, vocabulary.'],
            ['02', 'It marks its own work', 'A second pass reads the rewrite against the original and flags where meaning may have shifted, showing both excerpts so you can judge.'],
            ['03', 'Answers, not guesses', "Ask about your document and get an answer drawn from it, with the supporting line quoted. If it isn't in there, Lexi says so plainly."],
          ].map(([n, h, p]) => (
            <div className="col rv" key={n}>
              <div className="col-n">{n}</div>
              <h3>{h}</h3>
              <p>{p}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="sec" id="example" style={{ paddingTop: 0 }}>
        <div className="sec-h mid rv">
          <div className="sec-k">Side by side</div>
          <h2>The same paragraph,<br /><i>seven different ways</i></h2>
        </div>
        <div className="show rv">
          <div className="show-t">
            {SHOWCASE.map(([label], i) => (
              <button key={label} className={`st ${tab === i ? 'on' : ''}`} onClick={() => setTab(i)}>{label}</button>
            ))}
          </div>
          <div className="show-b">
            <div className="sb o">
              <div className="sb-k">As written</div>
              <p>Applicants must submit Form A, remit a fee of $50, and provide two forms of identification prior to the March 1 deadline.</p>
            </div>
            <div className="sb">
              <div className="sb-k n">Rewritten</div>
              <p key={tab} className="fu" style={{ whiteSpace: 'pre-wrap' }}>{render(SHOWCASE[tab][1])}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="sec" style={{ paddingTop: 0 }}>
        <div className="sec-h rv"><div className="sec-k">FAQ</div><h2>Questions, <i>answered</i></h2></div>
        <div className="faq">
          {faqs.map(([q, a], i) => (
            <div className={`q ${openQ === i ? 'op' : ''}`} key={q}>
              <button className="q-h" onClick={() => setOpenQ(openQ === i ? -1 : i)} aria-expanded={openQ === i}>
                {q}<span className="q-i">+</span>
              </button>
              <div className="q-b"><div>{a}</div></div>
            </div>
          ))}
        </div>
      </section>

      <div className="close">
        <div className="close-in rv">
          <h2>Reading shouldn't be<br />the <i>hard part.</i></h2>
          <p>Try it with something you've been putting off.</p>
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