import { useState } from 'react'
import { Volume2, Play, Square } from 'lucide-react'

function AudioControls({ text }) {
  const [playing, setPlaying] = useState(false)

  const speak = () => {
    if (!text) return
    speechSynthesis.cancel()
    const u = new SpeechSynthesisUtterance(text)
    u.rate = 0.92
    u.onend = () => setPlaying(false)
    speechSynthesis.speak(u)
    setPlaying(true)
  }
  const stop = () => { speechSynthesis.cancel(); setPlaying(false) }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon-badge"><Volume2 size={20} /></div>
        <div>
          <h2>Listen to Your Text</h2>
          <p className="card-sub">Have Lexi read the simplified version aloud at a comfortable pace</p>
        </div>
      </div>
      <div className="audio-row">
        <button className={`audio-play-btn ${playing ? 'playing' : ''}`} onClick={speak}>
          <Play size={16} fill="currentColor" /> {playing ? 'Playing...' : 'Read Aloud'}
        </button>
        <button className="audio-stop-btn" onClick={stop}>
          <Square size={14} fill="currentColor" /> Stop
        </button>
      </div>
    </div>
  )
}

export default AudioControls