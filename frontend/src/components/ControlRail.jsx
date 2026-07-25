export default function ControlRail({
  t, lang, setLang, size, setSize, leading, setLeading, theme, setTheme,
  health, historyCount, onOpenHistory,
}) {
  const dot = health === 'ok' ? 'dot ok' : health === 'bad' ? 'dot bad' : 'dot'
  const label = health === 'ok' ? t.connected : health === 'bad' ? t.offline : t.checking

  return (
    <div className="rail">
      <div className="rail-in">
        <div className="rg">
          <span className="rk">{t.size}</span>
          <div className="steps" role="group" aria-label={t.size}>
            {[['s', '10px'], ['m', '12.5px'], ['l', '15px']].map(([k, fs]) => (
              <button key={k} className={size === k ? 'on' : ''} style={{ fontSize: fs }}
                onClick={() => setSize(k)} aria-pressed={size === k} aria-label={`Text size ${k}`}>A</button>
            ))}
          </div>
        </div>

        <div className="rg">
          <span className="rk">{t.spacing}</span>
          <div className="steps" role="group" aria-label={t.spacing}>
            {[1, 2, 3].map((n) => (
              <button key={n} className={leading === n ? 'on' : ''}
                onClick={() => setLeading(n)} aria-pressed={leading === n}>{n}</button>
            ))}
          </div>
        </div>

        <div className="rg">
          <button
            className={`tg ${theme === 'dark' ? 'on' : ''}`}
            onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
            aria-pressed={theme === 'dark'}
          >
            {theme === 'light' ? t.dark : t.light}
          </button>
        </div>

        <div className="rg">
          <button className="tg hist-btn" onClick={onOpenHistory}>
            {t.history}
            {historyCount > 0 && <span className="hist-n">{historyCount}</span>}
          </button>
        </div>

        <div className="rg">
          <span className="status"><span className={dot} aria-hidden="true" />{label}</span>

          <button
            className={`lang-sw ${lang === 'bn' ? 'bn' : ''}`}
            onClick={() => setLang(lang === 'en' ? 'bn' : 'en')}
            role="switch"
            aria-checked={lang === 'bn'}
            aria-label="Language"
          >
            <span className="lang-track">
              <span className="lang-thumb" />
              <span className="lang-o en">EN</span>
              <span className="lang-o bn">বাং</span>
            </span>
          </button>
        </div>
      </div>
    </div>
  )
}