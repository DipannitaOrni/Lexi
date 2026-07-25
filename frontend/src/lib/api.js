const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export class ApiError extends Error {
  constructor(message, code, status) {
    super(message)
    this.code = code
    this.status = status
  }
}

async function request(path, { method = 'GET', body, isForm = false } = {}) {
  const opts = { method }
  if (body !== undefined) {
    if (isForm) {
      opts.body = body
    } else {
      opts.headers = { 'Content-Type': 'application/json' }
      opts.body = JSON.stringify(body)
    }
  }

  let res
  try {
    res = await fetch(`${BASE}${path}`, opts)
  } catch {
    throw new ApiError("Can't reach the server. Is the backend running?", 'network', 0)
  }

  if (res.status === 429) {
    throw new ApiError('Too many requests. Wait a moment and try again.', 'rate_limited', 429)
  }

  if (!res.ok) {
    let msg = `Request failed (${res.status})`
    let code = 'unknown'
    try {
      const data = await res.json()
      const err = data?.detail?.error || data?.error || data?.detail
      if (err?.message) { msg = err.message; code = err.code || code }
      else if (typeof err === 'string') { msg = err }
    } catch { /* keep default */ }
    throw new ApiError(msg, code, res.status)
  }

  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return res.json()
  return res.blob()
}

export const api = {
  health: () => request('/health'),
  modes: () => request('/modes'),

  uploadText: (pasted_text) =>
    request('/upload/text', { method: 'POST', body: { pasted_text } }),

  uploadFile: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return request('/upload', { method: 'POST', body: fd, isForm: true })
  },

  process: (document_id, mode, reading_level) =>
    request('/process', { method: 'POST', body: { document_id, mode, reading_level } }),

  ask: (document_id, question) =>
    request('/ask', { method: 'POST', body: { document_id, question } }),

  keyPoints: (document_id) =>
    request('/key-points', { method: 'POST', body: { document_id } }),

  glossary: (document_id) =>
    request('/glossary', { method: 'POST', body: { document_id, max_terms: 20 } }),

  flashcards: (document_id) =>
    request('/flashcards', { method: 'POST', body: { document_id, max_total: 15 } }),

  visualize: (document_id) =>
    request('/visualize', { method: 'POST', body: { document_id } }),

  ttsTimed: ({ document_id, text, mode, reading_level = 3, voice, speed = 1.0 }) =>
    request('/tts/timed', {
      method: 'POST',
      body: { document_id, text, mode, reading_level, voice, speed },
    }),

  transcribe: (blob) => {
    const fd = new FormData()
    fd.append('file', blob, 'speech.webm')
    return request('/transcribe', { method: 'POST', body: fd, isForm: true })
  },

  exportDoc: (document_id, mode, reading_level, format) =>
    request('/export', { method: 'POST', body: { document_id, mode, reading_level, format } }),
}