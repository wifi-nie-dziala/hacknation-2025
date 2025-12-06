import { useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

function App() {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('en');
  const [facts, setFacts] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [storedFacts, setStoredFacts] = useState([]);

  const extractFacts = async () => {
    if (!text.trim()) {
      setError('Please enter some text');
      return;
    }

    setLoading(true);
    setError('');
    setFacts('');

    try {
      const endpoint = language === 'en' ? '/api/extract-facts-en' : '/api/extract-facts-pl';
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to extract facts');
      }

      const data = await response.json();
      setFacts(data.facts);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const saveFacts = async () => {
    if (!facts.trim()) {
      setError('No facts to save');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/facts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fact: facts, language }),
      });

      if (!response.ok) {
        throw new Error('Failed to save facts');
      }

      const data = await response.json();
      alert('Facts saved successfully!');
      loadFacts();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadFacts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/facts`);
      
      if (!response.ok) {
        throw new Error('Failed to load facts');
      }

      const data = await response.json();
      setStoredFacts(data.facts || []);
    } catch (err) {
      console.error('Error loading facts:', err);
    }
  };

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();
      alert(`Backend status: ${data.status}`);
    } catch (err) {
      alert('Backend is not reachable');
    }
  };

  return (
    <div className="app">
      <header>
        <h1>HackNation 2025 - Fact Extractor</h1>
        <p>Extract facts from text using AI (English/Polish)</p>
      </header>

      <main>
        <div className="controls">
          <button onClick={checkHealth} className="btn-secondary">
            Check Backend Health
          </button>
          <button onClick={loadFacts} className="btn-secondary">
            Load Stored Facts
          </button>
        </div>

        <div className="language-selector">
          <label>
            <input
              type="radio"
              value="en"
              checked={language === 'en'}
              onChange={(e) => setLanguage(e.target.value)}
            />
            English
          </label>
          <label>
            <input
              type="radio"
              value="pl"
              checked={language === 'pl'}
              onChange={(e) => setLanguage(e.target.value)}
            />
            Polish
          </label>
        </div>

        <div className="input-section">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={
              language === 'en'
                ? 'Enter text to extract facts...'
                : 'Wprowadź tekst, aby wyodrębnić fakty...'
            }
            rows={8}
          />
        </div>

        <button onClick={extractFacts} disabled={loading} className="btn-primary">
          {loading ? 'Processing...' : 'Extract Facts'}
        </button>

        {error && <div className="error">{error}</div>}

        {facts && (
          <div className="results">
            <h2>Extracted Facts:</h2>
            <div className="facts-box">{facts}</div>
            <button onClick={saveFacts} disabled={loading} className="btn-primary">
              Save to Database
            </button>
          </div>
        )}

        {storedFacts.length > 0 && (
          <div className="stored-facts">
            <h2>Stored Facts ({storedFacts.length}):</h2>
            <div className="facts-list">
              {storedFacts.map((fact) => (
                <div key={fact.id} className="fact-item">
                  <span className="fact-lang">[{fact.language}]</span>
                  <span className="fact-text">{fact.fact}</span>
                  <span className="fact-date">
                    {new Date(fact.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App
