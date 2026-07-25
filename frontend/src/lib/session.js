const KEY = 'lexi.history.v1'

export function loadHistory() {
  try {
    const raw = sessionStorage.getItem(KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export function saveHistory(items) {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(items.slice(0, 25)))
  } catch {
    /* quota or private mode — history just won't persist */
  }
}

export function newEntry({ text, mode, level, rewritten, chat }) {
  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    at: Date.now(),
    title: (text || '').trim().slice(0, 60) || 'Untitled',
    words: (text || '').trim().split(/\s+/).filter(Boolean).length,
    text, mode, level, rewritten,
    chat: chat || [],
  }
}

export function timeAgo(ts) {
  const s = Math.floor((Date.now() - ts) / 1000)
  if (s < 60) return 'just now'
  if (s < 3600) return `${Math.floor(s / 60)}m ago`
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`
  return `${Math.floor(s / 86400)}d ago`
}