import { useEffect } from 'react'

export default function useReveal(dep) {
  useEffect(() => {
    const els = document.querySelectorAll('.rv:not(.in)')
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => e.isIntersecting && e.target.classList.add('in')),
      { threshold: 0.1 }
    )
    els.forEach((el, i) => {
      el.style.transitionDelay = `${(i % 3) * 80}ms`
      io.observe(el)
    })
    return () => io.disconnect()
  }, [dep])
}