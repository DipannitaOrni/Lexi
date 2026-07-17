import { Moon, Sun, Type, AlignJustify } from 'lucide-react'

const SIZES = [
  { id: 'small', px: '13.5px' },
  { id: 'medium', px: '16px' },
  { id: 'large', px: '19px' },
]

function ReadingControls({ fontSize, setFontSize, lineSpacing, setLineSpacing, darkMode, setDarkMode }) {
  return (
    <div className="reading-controls">
      <div className="rc-group">
        <span className="rc-label"><Type size={14} /> Text size</span>
        <div className="rc-size-btns">
          {SIZES.map((s) => (
            <button
              key={s.id}
              className={`rc-size-btn ${fontSize === s.id ? 'active' : ''}`}
              style={{ fontSize: s.px }}
              onClick={() => setFontSize(s.id)}
              aria-label={`${s.id} text size`}
              aria-pressed={fontSize === s.id}
            >A</button>
          ))}
        </div>
      </div>

      <button
        className={`rc-toggle-btn ${lineSpacing === 'relaxed' ? 'active' : ''}`}
        onClick={() => setLineSpacing(lineSpacing === 'relaxed' ? 'normal' : 'relaxed')}
        aria-pressed={lineSpacing === 'relaxed'}
      >
        <AlignJustify size={15} /> Relaxed spacing
      </button>

      <button className="rc-toggle-btn" onClick={() => setDarkMode(!darkMode)} aria-pressed={darkMode}>
        {darkMode ? <Sun size={15} /> : <Moon size={15} />}
        {darkMode ? 'Light mode' : 'Dark mode'}
      </button>
    </div>
  )
}

export default ReadingControls