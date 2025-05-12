import './App.css'

import { useEffect, useRef, useState } from 'react'

function generateSessionId() {
  // Simple UUID generator
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Hello! How can I help you today?' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessionId] = useState(() => generateSessionId())
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (input.trim() === '' || loading) return
    setMessages([...messages, { sender: 'user', text: input }])
    setLoading(true)
    setError(null)
    const userMessage = input
    setInput('')
    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, session_id: sessionId })
      })
      if (!res.ok) throw new Error('Server error')
      const data = await res.json()
      setMessages(msgs => [...msgs, { sender: 'bot', text: data.response }])
    } catch (err) {
      setMessages(msgs => [...msgs, { sender: 'bot', text: 'Sorry, there was an error.' }])
      setError('Failed to get response from server: ' + (err?.message || err))
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSend()
  }

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.sender}`}>{msg.text}</div>
        ))}
        {loading && <div className="chat-message bot">...</div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-row">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={loading ? "Waiting for response..." : "Type your message..."}
          className="chat-input"
          disabled={loading}
        />
        <button onClick={handleSend} className="send-btn" disabled={loading || !input.trim()}>Send</button>
      </div>
      {error && <div style={{color: '#ff6b6b', textAlign: 'center', marginTop: 8}}>{error}</div>}
    </div>
  )
}

export default App
