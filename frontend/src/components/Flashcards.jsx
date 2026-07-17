import { useState } from 'react'
import { Layers, ChevronLeft, ChevronRight } from 'lucide-react'

function Flashcards({ cards, loading }) {
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)

  if (loading || !cards || cards.length === 0) return null

  const card = cards[index]
  const go = (dir) => {
    setFlipped(false)
    setIndex((prev) => (prev + dir + cards.length) % cards.length)
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon-badge"><Layers size={20} /></div>
        <div>
          <h2>Flashcards</h2>
          <p className="card-sub">One idea at a time — click a card to flip it and reveal the meaning</p>
        </div>
      </div>
      <div className="flashcard-area">
        <button
          className="flashcard"
          onClick={() => setFlipped(!flipped)}
          aria-label={flipped ? 'Show term' : 'Show definition'}
        >
          {!flipped ? (
            <>
              <div className="fc-hint">Term</div>
              <div className="fc-term">{card.term}</div>
              <div className="fc-def">Click to see meaning</div>
            </>
          ) : (
            <>
              <div className="fc-hint">Meaning</div>
              <div className="fc-def">{card.definition}</div>
            </>
          )}
        </button>
        <div className="fc-controls">
          <button className="fc-btn" onClick={() => go(-1)} aria-label="Previous card"><ChevronLeft size={20} /></button>
          <span className="fc-counter">{index + 1} / {cards.length}</span>
          <button className="fc-btn" onClick={() => go(1)} aria-label="Next card"><ChevronRight size={20} /></button>
        </div>
      </div>
    </div>
  )
}

export default Flashcards