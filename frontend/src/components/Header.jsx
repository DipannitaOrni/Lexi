export default function Header({ lang, setLang, health, t }) {
  const dotClass = health === 'ok' ? 'dot ok' : health === 'bad' ? 'dot bad' : 'dot'
  const label = health === 'ok' ? t.connected : health === 'bad' ? t.offline : t.checking

  return (
    <header className="hdr">
      <div className="hdr-in">
        <div className="brand">
          <span className="brand-n">Lexi</span>
          <span className="brand-t">{t.tagline}</span>
        </div>
        <div className="hdr-r">
          <span className="status">
            <span className={dotClass} aria-hidden="true" />
            {label}
          </span>
          <div className="seg" role="group" aria-label="Language">
            <button className={lang === 'en' ? 'on' : ''} onClick={() => setLang('en')} aria-pressed={lang === 'en'}>EN</button>
            <button className={lang === 'bn' ? 'on' : ''} onClick={() => setLang('bn')} aria-pressed={lang === 'bn'}>বাংলা</button>
          </div>
        </div>
      </div>
    </header>
  )
}