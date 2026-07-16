import { FileText, Clock, BookOpen } from 'lucide-react'

function StatsRow({ text, loading }) {
  if (loading) return null
  const words = text.trim() ? text.trim().split(/\s+/).length : 0
  const minutes = Math.max(1, Math.round(words / 200))

  const stats = [
    { Icon: FileText, val: words, lbl: 'words simplified' },
    { Icon: Clock, val: `~${minutes} min`, lbl: 'reading time' },
    { Icon: BookOpen, val: 'Easy', lbl: 'reading level' },
  ]

  return (
    <div className="stats-row">
      {stats.map(({ Icon, val, lbl }, i) => (
        <div className="stat-pill" key={i}>
          <div className="stat-ico"><Icon size={18} /></div>
          <div>
            <div className="stat-val">{val}</div>
            <div className="stat-lbl">{lbl}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default StatsRow