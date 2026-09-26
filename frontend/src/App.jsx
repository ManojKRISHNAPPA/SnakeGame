import { useEffect, useRef, useState } from 'react'
import { api } from './api.js'

const blankRegistration = { username: '', email: '', password: '', confirmPassword: '', firstName: '', lastName: '' }

function AuthForm({ mode, onSubmit, onSwitch, error }) {
  const [form, setForm] = useState(mode === 'register' ? blankRegistration : { username: '', password: '' })
  const update = (event) => setForm({ ...form, [event.target.name]: event.target.value })
  return <main className="auth-shell"><section className="auth-panel">
    <p className="eyebrow">GameApp</p><h1>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h1><p className="muted">{mode === 'login' ? 'Sign in to play.' : 'One account gives you the whole arcade.'}</p>
    {error && <p className="notice error">{error}</p>}
    <form onSubmit={(event) => { event.preventDefault(); onSubmit(form) }}>
      {mode === 'register' && <><label>First name<input name="firstName" value={form.firstName} onChange={update} /></label><label>Last name<input name="lastName" value={form.lastName} onChange={update} /></label><label>Email<input type="email" name="email" required value={form.email} onChange={update} /></label></>}
      <label>Username<input name="username" required minLength="3" value={form.username} onChange={update} /></label><label>Password<input type="password" name="password" required minLength="6" value={form.password} onChange={update} /></label>
      {mode === 'register' && <label>Confirm password<input type="password" name="confirmPassword" required minLength="6" value={form.confirmPassword} onChange={update} /></label>}
      <button type="submit">{mode === 'login' ? 'Sign in' : 'Create account'}</button>
    </form><button className="text-button" onClick={onSwitch}>{mode === 'login' ? 'Need an account? Register' : 'Already registered? Sign in'}</button>
  </section></main>
}

function Snake() {
  const canvas = useRef(null); const direction = useRef({ x: 1, y: 0 }); const [running, setRunning] = useState(false); const [score, setScore] = useState(0)
  useEffect(() => {
    if (!running) return undefined
    const context = canvas.current.getContext('2d'); const size = 20; let snake = [{ x: 8, y: 8 }]; let food = { x: 14, y: 8 }; let points = 0
    const keydown = (event) => { const moves = { ArrowUp: [0, -1], ArrowDown: [0, 1], ArrowLeft: [-1, 0], ArrowRight: [1, 0] }; const next = moves[event.key]; if (next && next[0] !== -direction.current.x && next[1] !== -direction.current.y) { direction.current = { x: next[0], y: next[1] }; event.preventDefault() } }
    const tick = () => { const head = { x: snake[0].x + direction.current.x, y: snake[0].y + direction.current.y }; if (head.x < 0 || head.x >= size || head.y < 0 || head.y >= size || snake.some((part) => part.x === head.x && part.y === head.y)) { setRunning(false); return } snake.unshift(head); if (head.x === food.x && head.y === food.y) { points += 1; setScore(points); do { food = { x: Math.floor(Math.random() * size), y: Math.floor(Math.random() * size) } } while (snake.some((part) => part.x === food.x && part.y === food.y)) } else snake.pop(); context.fillStyle = '#102a43'; context.fillRect(0, 0, 400, 400); context.fillStyle = '#f6bd60'; context.fillRect(food.x * 20 + 2, food.y * 20 + 2, 16, 16); context.fillStyle = '#38a169'; snake.forEach((part) => context.fillRect(part.x * 20 + 2, part.y * 20 + 2, 16, 16)) }
    window.addEventListener('keydown', keydown); const interval = window.setInterval(tick, 115); return () => { window.removeEventListener('keydown', keydown); window.clearInterval(interval) }
  }, [running])
  const start = () => { direction.current = { x: 1, y: 0 }; setScore(0); setRunning(true) }
  return <section className="game-view"><div><p className="eyebrow">Snake</p><h2>Score: {score}</h2><p className="muted">Use the arrow keys to steer.</p><button onClick={start}>{running ? 'Restart game' : 'Start game'}</button></div><canvas ref={canvas} width="400" height="400" aria-label="Snake game board" /></section>
}

function Calculator() {
  const [display, setDisplay] = useState('0'); const add = (value) => setDisplay((current) => current === '0' ? value : current + value)
  const calculate = () => { try { if (!/^[0-9+\-*/(). ]+$/.test(display)) throw new Error(); setDisplay(String(Function(`'use strict'; return (${display})`)())) } catch { setDisplay('Error') } }
  return <section className="calculator"><p className="eyebrow">Calculator</p><output>{display}</output><div className="keys">{['C', '(', ')', '/', '7', '8', '9', '*', '4', '5', '6', '-', '1', '2', '3', '+', '0', '.', '='].map((key) => <button key={key} className={key === '=' ? 'accent' : ''} onClick={() => key === 'C' ? setDisplay('0') : key === '=' ? calculate() : add(key)}>{key}</button>)}</div></section>
}

function Dashboard({ data, onLogout }) {
  const [view, setView] = useState('dashboard')
  return <main><header><strong>GameApp</strong><nav><button onClick={() => setView('dashboard')}>Dashboard</button><button onClick={() => setView('snake')}>Snake</button><button onClick={() => setView('calculator')}>Calculator</button><button className="text-button" onClick={onLogout}>Sign out</button></nav></header>
    {view === 'dashboard' && <section className="dashboard"><p className="eyebrow">Player dashboard</p><h1>Hello, {data.user.displayName}</h1><div className="stat"><span>Players registered</span><strong>{data.totalUsers}</strong></div><div className="tiles"><button onClick={() => setView('snake')}><b>Snake</b><span>Classic arcade action</span></button><button onClick={() => setView('calculator')}><b>Calculator</b><span>Fast calculations</span></button></div></section>}
    {view === 'snake' && <Snake />}{view === 'calculator' && <Calculator />}
  </main>
}

export default function App() {
  const [mode, setMode] = useState('loading'); const [error, setError] = useState(''); const [dashboard, setDashboard] = useState(null)
  const loadDashboard = async () => { try { setDashboard(await api.dashboard()); setMode('dashboard') } catch { setMode('login') } }
  useEffect(() => { loadDashboard() }, [])
  const authenticate = async (form) => { setError(''); try { if (mode === 'register') { await api.register(form); setMode('login'); setError('Account created. Sign in to continue.'); return } await api.login(form); await loadDashboard() } catch (requestError) { setError(requestError.message) } }
  const logout = async () => { await api.logout(); setDashboard(null); setMode('login') }
  if (mode === 'loading') return <main className="loading">Loading GameApp...</main>
  if (mode === 'dashboard') return <Dashboard data={dashboard} onLogout={logout} />
  return <AuthForm mode={mode} error={error} onSubmit={authenticate} onSwitch={() => { setError(''); setMode(mode === 'login' ? 'register' : 'login') }} />
}