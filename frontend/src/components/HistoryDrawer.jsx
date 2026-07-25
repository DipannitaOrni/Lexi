import { timeAgo } from '../lib/session'

export default function HistoryDrawer({ open, onClose, items, onPick, onClear, t }) {
  return (
    <>
      <div className={`scrim ${open ? 'open' : ''}`} onClick={onClose} />
      <aside className={`drawer ${open ? 'open' : ''}`} aria-hidden={!open}>
        <div className="dw-h">
          <h3>This session</h3>
          <button className="ghost" onClick={onClose}>Close</button>
        </div>

        <div className="dw-b">
          {items.length === 0 ? (
            <div className="empty">Nothing yet. Rewrite something and it'll appear here.</div>
          ) : (
            items.map((it) => (
              <div className="hi" key={it.id} onClick={() => onPick(it)} role="button" tabIndex={0}
                onKeyDown={(e) => e.key === 'Enter' && onPick(it)}>
                <div className="hi-t">{it.title}</div>
                <div className="hi-m">
                  <span>{it.mode}</span>
                  <span>lv {it.level}</span>
                  <span>{it.words}w</span>
                  <span>{timeAgo(it.at)}</span>
                </div>
              </div>
            ))
          )}
        </div>

        {items.length > 0 && (
          <div className="dw-f">
            <button className="ghost" onClick={onClear} style={{ width: '100%' }}>Clear history</button>
          </div>
        )}
      </aside>
    </>
  )
}