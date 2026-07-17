import { useState } from 'react'
import { MessageCircle, Lightbulb, Send } from 'lucide-react'

function ChatBox({ chatHistory, setChatHistory, onAsk }) {
  const [question, setQuestion] = useState('')
  const [asking, setAsking] = useState(false)

  const askQuestion = async () => {
    if (!question.trim() || asking) return
    const q = question
    setChatHistory((prev) => [...prev, { role: 'user', text: q }])
    setQuestion('')
    setAsking(true)
    const answer = await onAsk(q)
    setChatHistory((prev) => [...prev, { role: 'bot', text: answer }])
    setAsking(false)
  }

  return (
    <div className="card">
      <div className="card-header">
        <div className="icon-badge"><MessageCircle size={20} /></div>
        <div>
          <h2>Ask Lexi Anything</h2>
          <p className="card-sub">Have a question about the document? Lexi answers in plain language</p>
        </div>
      </div>
      <div className="chat-history">
        {chatHistory.length === 0 && (
          <div className="chat-empty">
            <Lightbulb size={20} />
            <div>
              <p className="chat-empty-title">Start a conversation</p>
              <p className="chat-empty-sub">Try: "What is the main point?" or "What do I need to do next?"</p>
            </div>
          </div>
        )}
        {chatHistory.map((msg, i) => (
          <div key={i} className={`bubble-wrap ${msg.role}`}>
            <div className="bubble-label">{msg.role === 'user' ? 'You' : 'Lexi'}</div>
            <div className={`bubble ${msg.role}`}>{msg.text}</div>
          </div>
        ))}
        {asking && (
          <div className="bubble-wrap bot">
            <div className="bubble-label">Lexi</div>
            <div className="bubble bot">Thinking...</div>
          </div>
        )}
      </div>
      <div className="chat-input-row">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
          placeholder="Ask anything about this document..."
          aria-label="Ask a question"
        />
        <button className="send-btn" onClick={askQuestion} disabled={asking}>Send <Send size={15} /></button>
      </div>
    </div>
  )
}

export default ChatBox