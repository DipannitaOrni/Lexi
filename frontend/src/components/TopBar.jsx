import { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import Wordmark from './Wordmark'

const CAPS = [
  ['01', 'Adaptive rewriting', 'Seven modes, five levels of simplification'],
  ['02', 'Self-verification', 'Flags where meaning may have drifted'],
  ['03', 'Grounded answers', 'Ask questions about your document'],
  ['04', 'Study tools', 'Key points, glossary, flashcards'],
  ['05', 'Read aloud', 'Audio with word-by-word highlighting'],
  ['06', 'English & বাংলা', 'Full bilingual interface and rewriting'],
]

export default function TopBar() {
  const [stuck, setStuck] = useState(false)
  const [mobOpen, setMobOpen] = useState(false)
  const { pathname } = useLocation()
  const nav = useNavigate()
  const isApp = pathname === '/app'

  useEffect(() => {
    const onScroll = () => setStuck(window.scrollY > 8)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => { setMobOpen(false) }, [pathname])

  const is = (p) => (pathname === p ? 'mi act' : 'mi')

  return (
    <header className={`top ${stuck ? 'stuck' : ''}`}>
      <div className="top-in">
        <Link to="/" aria-label="Lexi home"><Wordmark size={30} /></Link>

        <nav className={`menu ${isApp ? 'hide' : ''}`} aria-label="Main">
          <div className={is('/')}><Link to="/">Home</Link></div>

          <div className="mi">
            <button aria-haspopup="true">
              What it does
              <svg className="caret" viewBox="0 0 10 10" fill="none">
                <path d="M2 4l3 3 3-3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
            </button>
            <div className="drop">
              {CAPS.map(([n, t, d]) => (
                <button className="di" key={n} onClick={() => nav('/app')}>
                  <span className="di-n">{n}</span>
                  <span>
                    <span className="di-t">{t}</span>
                    <span className="di-d">{d}</span>
                  </span>
                </button>
              ))}
            </div>
          </div>

          <div className={is('/about')}><Link to="/about">About</Link></div>
          <div className={is('/faq')}><Link to="/faq">FAQ</Link></div>
        </nav>

        <div className="top-r">
          {!isApp && (
            <button className="burger" onClick={() => setMobOpen((o) => !o)} aria-label="Menu" aria-expanded={mobOpen}>
              <svg width="17" height="17" viewBox="0 0 18 18" fill="none">
                <path d="M2 5h14M2 9h14M2 13h14" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
          )}
          {isApp ? (
            <Link to="/" className="top-back">← Back to site</Link>
          ) : (
            <button className="top-cta" onClick={() => nav('/app')}>Open Lexi</button>
          )}
        </div>
      </div>

      {!isApp && (
        <div className={`mob ${mobOpen ? 'open' : ''}`}>
          <Link to="/">Home</Link>
          <Link to="/about">About</Link>
          <Link to="/faq">FAQ</Link>
          <Link to="/app">Open Lexi</Link>
        </div>
      )}
    </header>
  )
}