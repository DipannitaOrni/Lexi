import { useState } from 'react'
import { BarChart3, Sparkles, Copy, Download, Check } from 'lucide-react'

function SplitView({ original, simplified, loading }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(simplified)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (e) { /* clipboard unavailable, fail silently */ }
  }

  const handleDownload = () => {
    const blob = new Blob([simplified], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'lexi-simplified.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon-badge"><BarChart3 size={20} /></div>
        <div>
          <h2>Before &amp; After</h2>
          <p className="card-sub">Compare your original text with Lexi's simplified version</p>
        </div>
      </div>
      <div className="split-grid">
        <div className="split-panel original-panel">
          <div className="panel-tag">Original</div>
          <p>{original}</p>
        </div>
        <div className="split-panel simplified-panel">
          <div className="panel-tag-row">
            <div className="panel-tag simplified-tag"><Sparkles size={13} /> Simplified by Lexi</div>
            {!loading && simplified && (
              <div className="panel-actions">
                <button className="panel-action-btn" onClick={handleCopy} aria-label="Copy simplified text">
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                </button>
                <button className="panel-action-btn" onClick={handleDownload} aria-label="Download simplified text">
                  <Download size={14} />
                </button>
              </div>
            )}
          </div>
          {loading ? (
            <div className="loading-state">
              <div className="dots"><span /><span /><span /></div>
              <p>Lexi is reading your document...</p>
            </div>
          ) : (
            <p className="simplified-text">{simplified}</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default SplitView