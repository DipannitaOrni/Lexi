import { FileText, UploadCloud } from 'lucide-react'

function UploadArea({ setOriginalText, originalText }) {
  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    const text = await file.text()
    setOriginalText(text)
  }

  const wordCount = originalText.trim() ? originalText.trim().split(/\s+/).length : 0

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon-badge"><FileText size={20} /></div>
        <div>
          <h2>Add Your Document</h2>
          <p className="card-sub">Supports plain text, PDF, and Word documents</p>
        </div>
      </div>
      <div className="upload-body">
        <label className="dropzone" htmlFor="file-upload">
          <UploadCloud size={28} />
          <div className="drop-title">Click to upload a file</div>
          <div className="drop-sub">TXT · PDF · DOCX</div>
          <input id="file-upload" type="file" accept=".txt,.pdf,.docx" onChange={handleFileUpload} style={{ display: 'none' }} />
        </label>
        <div className="or-divider">or</div>
        <div className="paste-section">
          <label htmlFor="paste-text">Paste your text directly</label>
          <textarea
            id="paste-text"
            placeholder="Paste any article, assignment, government form, or document here..."
            onChange={(e) => setOriginalText(e.target.value)}
            value={originalText}
            rows={6}
          />
          {wordCount > 0 && <div className="char-count">{wordCount} words</div>}
        </div>
      </div>
    </div>
  )
}

export default UploadArea