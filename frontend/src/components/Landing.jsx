import { Sparkles, ArrowRight, ArrowDown } from 'lucide-react'

function Landing({ onStart }) {
  return (
    <div className="landing">
      <div className="l-bg" aria-hidden="true"></div>
      <div className="grain" aria-hidden="true"></div>

<nav className="nav">
  <div className="nav-brand">
    <span className="nav-mark"><Sparkles size={18} /></span>
    <span className="nav-word">Lexi</span>
  </div>
</nav>

      <div className="hero-split">
        <div className="hero-left">
          <div className="badge-plain">Built for dyslexia &amp; ADHD readers</div>
          <h1 className="big-title">Reading, <span className="hl">rewritten</span> for your brain.</h1>
          <p className="sub">
            Lexi turns dense documents, forms, and articles into text that's easy
            for you — clearer sentences, calmer structure, your pace.
          </p>
         <div className="hero-ctas">
           <button className="cta" onClick={onStart}>Get Started <ArrowRight size={18} /></button>
         </div>
          <div className="trust-row">
            <div className="avatars">
              <div className="avatar a1"></div>
              <div className="avatar a2"></div>
              <div className="avatar a3"></div>
            </div>
            <div className="trust-text"><b>Free</b> · No sign-up · Built for students</div>
          </div>
        </div>

        <div className="hero-right">
          <div className="annotation">
            try it yourself
            <svg width="60" height="40" viewBox="0 0 60 40" fill="none">
              <path d="M5 5 C20 25, 35 30, 52 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M44 12 L52 15 L47 22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
            </svg>
          </div>
          <div className="demo-card">
            <div className="demo-label">A real example</div>
            <div className="demo-original">"Notwithstanding the aforementioned provisions, the party of the first part shall retain the right to terminate..."</div>
            <div className="demo-arrow-row"><ArrowDown size={20} /></div>
            <div className="demo-tag"><Sparkles size={13} /> Simplified by Lexi</div>
            <div className="demo-simplified">"Even with the rules above, the first person can end this agreement early."</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Landing