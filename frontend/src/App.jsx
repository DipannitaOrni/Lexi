import { useState } from 'react'
import { Sparkles, ArrowLeft } from 'lucide-react'
import UploadArea from './components/UploadArea'
import ModeSelector from './components/ModeSelector'
import StatsRow from './components/StatsRow'
import SplitView from './components/SplitView'
import KeyPoints from './components/KeyPoints'
import Flashcards from './components/Flashcards'
import ConfidencePanel from './components/ConfidencePanel'
import AudioControls from './components/AudioControls'
import ChatBox from './components/ChatBox'
import Landing from './components/Landing'
import ReadingControls from './components/ReadingControls'
import ProgressSteps from './components/ProgressSteps'

const API_BASE = 'http://localhost:8000'

const FONT_SIZE_PX = { small: '13.5px', medium: '16px', large: '19px' }
const LINE_HEIGHT = { normal: '1.85', relaxed: '2.3' }

function App() {
  const [originalText, setOriginalText] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [documentId, setDocumentId] = useState(null)

  const [simplifiedText, setSimplifiedText] = useState('')
  const [mode, setMode] = useState('dyslexia')
  const [confidenceFlags, setConfidenceFlags] = useState([])
  const [keyPoints, setKeyPoints] = useState([])
  const [flashcards, setFlashcards] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [chatHistory, setChatHistory] = useState([])
  const [view, setView] = useState('landing')

  const [fontSize, setFontSize] = useState('medium')
  const [lineSpacing, setLineSpacing] = useState('normal')
  const [darkMode, setDarkMode] = useState(false)

  const handleTextChange = (text) => {
    setOriginalText(text)
    setSelectedFile(null)
    setDocumentId(null)
    setSimplifiedText('')
  }

  const handleFileChange = (file) => {
    setSelectedFile(file)
    setOriginalText('')
    setDocumentId(null)
    setSimplifiedText('')
  }

  const uploadContent = async () => {
    if (selectedFile) {
      const formData = new FormData()
      formData.append('file', selectedFile)
      const res = await fetch(`${API_BASE}/upload`, { method: 'POST', body: formData })
      if (!res.ok) throw new Error('upload_failed')
      const data = await res.json()
      setOriginalText(data.extracted_text_preview)
      return data.document_id
    } else {
      const res = await fetch(`${API_BASE}/upload/text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pasted_text: originalText }),
      })
      if (!res.ok) throw new Error('upload_failed')
      const data = await res.json()
      return data.document_id
    }
  }

  const handleSimplify = async () => {
    if (!originalText.trim() && !selectedFile) return
    setLoading(true)
    setError(null)
    try {
      let docId = documentId
      if (!docId) {
        docId = await uploadContent()
        setDocumentId(docId)
      }
      const res = await fetch(`${API_BASE}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: docId, mode }),
      })
      if (!res.ok) throw new Error('process_failed')
      const data = await res.json()
      setSimplifiedText(data.rewritten_text)
      if (data.verification) {
        setConfidenceFlags(data.verification.warnings.map((w) => w.description))
      } else if (data.verification_error) {
        setConfidenceFlags(['Verification was unavailable for this result — review carefully.'])
      } else {
        setConfidenceFlags([])
      }
    } catch (err) {
      console.error('Simplify failed:', err)
      setError('Something went wrong simplifying your text. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAsk = async (question) => {
    if (!documentId) return "Simplify a document first so I have something to answer questions about."
    try {
      const res = await fetch(`${API_BASE}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: documentId, question }),
      })
      const data = await res.json()
      if (!data.found_in_document) {
        return "I couldn't find that in the document. Try rephrasing your question."
      }
      return data.answer
    } catch (err) {
      console.error('Ask failed:', err)
      return "Something went wrong answering that — please try again."
    }
  }

  const hasResults = simplifiedText || loading

  if (view === 'landing') {
    return <Landing onStart={() => setView('tool')} />
  }

  return (
    <div
      className={`app-shell ${darkMode ? 'dark' : ''}`}
      style={{
        '--content-font-size': FONT_SIZE_PX[fontSize],
        '--content-line-height': LINE_HEIGHT[lineSpacing],
      }}
    >
      <button className="back-btn" onClick={() => setView('landing')} aria-label="Back to home">
        <ArrowLeft size={20} />
      </button>

      <div className="bg" aria-hidden="true"></div>
      <div className="grain" aria-hidden="true"></div>
      <div className="tool-blob tb1" aria-hidden="true"></div>
      <div className="tool-blob tb2" aria-hidden="true"></div>
      <div className="tool-blob tb3" aria-hidden="true"></div>
      <div className="tool-blob tb4" aria-hidden="true"></div>
      <div className="app">
        <header className="page-intro">
          <h1 className="page-title">Let's simplify your text</h1>
          <p className="page-sub">Add your document, pick a reading mode, and Lexi does the rest.</p>
        </header>

        <ProgressSteps hasText={!!originalText.trim() || !!selectedFile} hasResults={!!simplifiedText} />
        <ReadingControls
          fontSize={fontSize} setFontSize={setFontSize}
          lineSpacing={lineSpacing} setLineSpacing={setLineSpacing}
          darkMode={darkMode} setDarkMode={setDarkMode}
        />

        <UploadArea
          originalText={originalText}
          onTextChange={handleTextChange}
          onFileChange={handleFileChange}
          selectedFileName={selectedFile?.name}
        />
        <ModeSelector mode={mode} setMode={setMode} />

        <div className="simplify-wrapper">
          <button className="simplify-btn" onClick={handleSimplify} disabled={loading || (!originalText.trim() && !selectedFile)}>
            <Sparkles size={18} />
            {loading ? 'Simplifying your text...' : 'Simplify with Lexi'}
          </button>
          {!originalText.trim() && !selectedFile && <p className="hint">Add your text above to get started</p>}
          {error && <p className="hint" style={{ color: '#d97706' }}>{error}</p>}
        </div>

        {hasResults && (
          <div className="results-section">
            <StatsRow text={simplifiedText} loading={loading} />
            <SplitView original={originalText} simplified={simplifiedText} loading={loading} />
            <KeyPoints points={keyPoints} loading={loading} />
            <Flashcards cards={flashcards} loading={loading} />
            <ConfidencePanel flags={confidenceFlags} />
            <AudioControls text={simplifiedText} />
            <ChatBox chatHistory={chatHistory} setChatHistory={setChatHistory} onAsk={handleAsk} />
          </div>
        )}
      </div>
    </div>
  )
}

export default App