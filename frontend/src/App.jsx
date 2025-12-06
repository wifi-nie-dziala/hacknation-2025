import { useState, useEffect } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

function App() {
  const [text, setText] = useState('');
  const [language, setLanguage] = useState('en');
  const [facts, setFacts] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [storedFacts, setStoredFacts] = useState([]);
  const [conversations, setConversations] = useState([
    { id: 1, title: 'Nowa analiza', date: new Date().toISOString() }
  ]);
  const [currentConversation, setCurrentConversation] = useState(1);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    loadFacts();
  }, []);

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

      await response.json();
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

  const newConversation = () => {
    const newId = conversations.length + 1;
    setConversations([
      { id: newId, title: 'Nowa analiza', date: new Date().toISOString() },
      ...conversations
    ]);
    setCurrentConversation(newId);
    setText('');
    setFacts('');
    setError('');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-gray-900 text-white transition-all duration-300 overflow-hidden flex flex-col`}>
        <div className="p-4 border-b border-gray-700">
          <button 
            onClick={newConversation}
            className="w-full bg-gray-800 hover:bg-gray-700 text-white px-4 py-3 rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Nowa analiza
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3">
          <div className="space-y-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => setCurrentConversation(conv.id)}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  currentConversation === conv.id
                    ? 'bg-gray-800 text-white'
                    : 'text-gray-300 hover:bg-gray-800'
                }`}
              >
                <div className="font-medium truncate">{conv.title}</div>
                <div className="text-xs text-gray-500">
                  {new Date(conv.date).toLocaleDateString('pl-PL')}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 border-t border-gray-700">
          <button 
            onClick={loadFacts}
            className="w-full text-sm text-gray-300 hover:text-white px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Załaduj zapisane fakty
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <h1 className="text-xl font-semibold text-gray-900">HackNation 2025 - Fact Extractor</h1>
              <p className="text-sm text-gray-500">Extract facts from text using AI</p>
            </div>
          </div>
          
          <button
            onClick={checkHealth}
            className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
          >
            Check Health
          </button>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto p-6 space-y-6">
            {/* Language Selector */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <label className="block text-sm font-medium text-gray-700 mb-3">Language / Język</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    value="en"
                    checked={language === 'en'}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-gray-700">English</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    value="pl"
                    checked={language === 'pl'}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-4 h-4 text-blue-600"
                  />
                  <span className="text-gray-700">Polish</span>
                </label>
              </div>
            </div>

            {/* Input Section */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                {language === 'en' ? 'Enter text to analyze' : 'Wprowadź tekst do analizy'}
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={
                  language === 'en'
                    ? 'Enter text to extract facts...'
                    : 'Wprowadź tekst, aby wyodrębnić fakty...'
                }
                rows={8}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
              <div className="mt-4">
                <button
                  onClick={extractFacts}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  {loading ? 'Processing...' : 'Extract Facts'}
                </button>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {/* Results */}
            {facts && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">Extracted Facts:</h2>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 whitespace-pre-wrap">
                  {facts}
                </div>
                <button
                  onClick={saveFacts}
                  disabled={loading}
                  className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-lg font-medium transition-colors"
                >
                  Save to Database
                </button>
              </div>
            )}

            {/* Stored Facts */}
            {storedFacts.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Stored Facts ({storedFacts.length})
                </h2>
                <div className="space-y-3">
                  {storedFacts.map((fact) => (
                    <div
                      key={fact.id}
                      className="bg-gray-50 border border-gray-200 rounded-lg p-4 hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                          {fact.language.toUpperCase()}
                        </span>
                        <div className="flex-1">
                          <p className="text-gray-800">{fact.fact}</p>
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(fact.created_at).toLocaleDateString('pl-PL', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App
