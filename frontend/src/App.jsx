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

const FONT_SIZE_PX = { small: '13.5px', medium: '16px', large: '19px' }
const LINE_HEIGHT = { normal: '1.85', relaxed: '2.3' }

function App() {
  const [originalText, setOriginalText] = useState('')
  const [simplifiedText, setSimplifiedText] = useState('')
  const [mode, setMode] = useState('dyslexia')
  const [confidenceFlags, setConfidenceFlags] = useState([])
  const [keyPoints, setKeyPoints] = useState([])
  const [flashcards, setFlashcards] = useState([])
  const [loading, setLoading] = useState(false)
  const [chatHistory, setChatHistory] = useState([])
  const [view, setView] = useState('landing')

  const [fontSize, setFontSize] = useState('medium')
  const [lineSpacing, setLineSpacing] = useState('normal')
  const [darkMode, setDarkMode] = useState(false)

  const handleSimplify = () => {
    if (!originalText.trim()) return
    setLoading(true)
    setTimeout(() => {
      setSimplifiedText('This is where the simplified version will appear once the backend is connected. Lexi rewrites your text to match your chosen reading mode — shorter sentences, clearer words, and a calmer structure.')
      setConfidenceFlags(['This sentence was shortened significantly — please check the meaning is preserved.'])
      setKeyPoints([
        'This is the first key takeaway Lexi found in your document.',
        'The second most important point appears here.',
        'A third essential idea, pulled out for quick scanning.',
      ])
      setFlashcards([
        { term: 'Example Term', definition: 'A clear, simple definition of the term will appear here once connected to the backend.' },
        { term: 'Second Concept', definition: 'Another concept broken down into an easy-to-remember card.' },
        { term: 'Third Idea', definition: 'One idea per card keeps things calm and focused.' },
      ])
      setLoading(false)
    }, 1500)
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
      <div className="app">
        <header className="page-intro">
          <h1 className="page-title">Let's simplify your text</h1>
          <p className="page-sub">Add your document, pick a reading mode, and Lexi does the rest.</p>
        </header>

        <ProgressSteps hasText={!!originalText.trim()} hasResults={!!simplifiedText} />
        <ReadingControls
          fontSize={fontSize} setFontSize={setFontSize}
          lineSpacing={lineSpacing} setLineSpacing={setLineSpacing}
          darkMode={darkMode} setDarkMode={setDarkMode}
        />

        <UploadArea setOriginalText={setOriginalText} originalText={originalText} />
        <ModeSelector mode={mode} setMode={setMode} />

        <div className="simplify-wrapper">
          <button className="simplify-btn" onClick={handleSimplify} disabled={loading || !originalText.trim()}>
            <Sparkles size={18} />
            {loading ? 'Simplifying your text...' : 'Simplify with Lexi'}
          </button>
          {!originalText.trim() && <p className="hint">Add your text above to get started</p>}
        </div>

        {hasResults && (
          <div className="results-section">
            <StatsRow text={simplifiedText} loading={loading} />
            <SplitView original={originalText} simplified={simplifiedText} loading={loading} />
            <KeyPoints points={keyPoints} loading={loading} />
            <Flashcards cards={flashcards} loading={loading} />
            <ConfidencePanel flags={confidenceFlags} />
            <AudioControls text={simplifiedText} />
            <ChatBox originalText={originalText} chatHistory={chatHistory} setChatHistory={setChatHistory} />
          </div>
        )}
      </div>
    </div>
  )
}

export default App