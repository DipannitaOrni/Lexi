import { Routes, Route, useLocation } from 'react-router-dom'
import TopBar from './components/TopBar'
import Footer from './components/Footer'
import Landing from './pages/Landing'
import About from './pages/About'
import FAQ from './pages/FAQ'
import AppPage from './pages/AppPage'

export default function App() {
  const { pathname } = useLocation()
  const isApp = pathname === '/app'

  return (
    <>
      <div className="paper-tex" aria-hidden="true" />
      <TopBar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/about" element={<About />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/app" element={<AppPage />} />
      </Routes>
      {!isApp && <Footer />}
    </>
  )
}