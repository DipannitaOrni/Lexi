import { ListChecks } from 'lucide-react'

function KeyPoints({ points, loading }) {
  if (loading || !points || points.length === 0) return null
  return (
    <div className="card">
      <div className="card-header">
        <div className="icon-badge"><ListChecks size={20} /></div>
        <div>
          <h2>Key Points</h2>
          <p className="card-sub">The most important takeaways, pulled out for quick scanning</p>
        </div>
      </div>
      <ul className="keypoints">
        {points.map((p, i) => (
          <li className="keypoint" key={i}>
            <span className="kp-num">{i + 1}</span>
            <span className="kp-text">{p}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default KeyPoints