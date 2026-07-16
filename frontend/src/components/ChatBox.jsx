import { useState } from 'react'
import { MessageCircle, Lightbulb, Send } from 'lucide-react'

function ChatBox({ originalText, chatHistory, setChatHistory }) {
  const [question, setQuestion] = useState('')

  const askQuestion = () => {
    if (!question.trim()) return
    setChatHistory([
      ...chatHistory,
      { role: 'user', text: question },
      { role: 'bot', text: 'Lexi will answer questions about your document once the backend is connected.' },
    ])
    setQuestion('')
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
        <button className="send-btn" onClick={askQuestion}>Send <Send size={15} /></button>
      </div>
    </div>
  )
}

export default ChatBox