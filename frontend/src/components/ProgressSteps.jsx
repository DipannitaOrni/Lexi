import { Check } from 'lucide-react'

function ProgressSteps({ hasText, hasResults }) {
  const steps = ['Add your text', 'Simplify', 'Review & listen']
  let activeIndex = 0
  if (hasText && !hasResults) activeIndex = 1
  if (hasResults) activeIndex = 2

  return (
    <div className="progress-steps">
      {steps.map((label, i) => {
        const state = i < activeIndex ? 'done' : i === activeIndex ? 'active' : 'upcoming'
        return (
          <div className={`pstep ${state}`} key={i}>
            <span className="pstep-dot">{state === 'done' ? <Check size={12} /> : i + 1}</span>
            <span className="pstep-label">{label}</span>
            {i < steps.length - 1 && <span className="pstep-line" />}
          </div>
        )
      })}
    </div>
  )
}

export default ProgressSteps