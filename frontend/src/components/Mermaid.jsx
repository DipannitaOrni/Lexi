import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

let booted = false

function boot(dark) {
  const css = getComputedStyle(document.documentElement)
  const v = (n, f) => css.getPropertyValue(n).trim() || f

  mermaid.initialize({
    startOnLoad: false,
    securityLevel: 'strict',
    theme: 'base',
    fontFamily: "'Poppins','Noto Sans Bengali',sans-serif",
    flowchart: { curve: 'basis', padding: 18, nodeSpacing: 42, rankSpacing: 52, useMaxWidth: true },
    themeVariables: {
      background: 'transparent',
      primaryColor: v('--plum-s', '#F2E9EF'),
      primaryBorderColor: v('--plum', '#5A3A52'),
      primaryTextColor: v('--ink', '#221C18'),
      lineColor: v('--terra', '#B85C38'),
      secondaryColor: v('--sand-s', '#F7EEDF'),
      tertiaryColor: v('--moss-s', '#EAF0E7'),
      fontSize: '14px',
      nodeBorder: v('--plum', '#5A3A52'),
      clusterBkg: v('--paper-2', '#F4EFE6'),
      clusterBorder: v('--rule', '#E4DACB'),
      edgeLabelBackground: dark ? v('--card', '#211C18') : '#FFFFFF',
    },
  })
  booted = true
}

export default function Mermaid({ code }) {
  const ref = useRef(null)
  const [err, setErr] = useState(null)
  const [svg, setSvg] = useState('')

  useEffect(() => {
    if (!code) return
    let alive = true
    const dark = document.documentElement.getAttribute('data-theme') === 'dark'
    boot(dark)

    const id = `mmd-${Math.random().toString(36).slice(2, 9)}`
    mermaid
      .render(id, code)
      .then(({ svg }) => { if (alive) { setSvg(svg); setErr(null) } })
      .catch((e) => { if (alive) setErr(e?.message || 'Could not draw this diagram.') })

    return () => { alive = false }
  }, [code])

  if (err) {
    return (
      <>
        <div className="mm-err">{err}</div>
        <pre className="mm-src">{code}</pre>
      </>
    )
  }

  return (
    <div className="mm-wrap">
      <div className="mm-canvas" ref={ref} dangerouslySetInnerHTML={{ __html: svg }} />
    </div>
  )
}