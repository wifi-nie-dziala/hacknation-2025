import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link2, Image, FileText, Paperclip, Eye, Trash2 } from 'lucide-react';

export default function CreateAnalysisForm() {
  const navigate = useNavigate();
  const [analysisName, setAnalysisName] = useState('');
  const [country, setCountry] = useState('Atlantis');
  const [timeHorizon12, setTimeHorizon12] = useState(true);
  const [timeHorizon36, setTimeHorizon36] = useState(false);
  const [positiveScenario, setPositiveScenario] = useState(true);
  const [negativeScenario, setNegativeScenario] = useState(true);
  const [sourceScope, setSourceScope] = useState('added');
  const [sources, setSources] = useState([]);

  const handleCancel = () => {
    navigate('/');
  };

  const handleSaveDraft = () => {
    console.log('Zapisano jako szkic');
  };

  const handleRunAnalysis = () => {
    if (!timeHorizon12 && !timeHorizon36) {
      alert('Wybierz co najmniej jeden horyzont czasowy');
      return;
    }
    if (!positiveScenario && !negativeScenario) {
      alert('Wybierz co najmniej jeden wariant scenariusza');
      return;
    }
    console.log('Uruchomiono analizę', { 
      analysisName, 
      country, 
      timeHorizon: { twelve: timeHorizon12, thirtySix: timeHorizon36 },
      positiveScenario, 
      negativeScenario,
      sourceScope,
      sources
    });
  };

  const addSource = (type, file = null) => {
    const newSource = {
      id: Date.now().toString(),
      type,
      name: file ? file.name : (type === 'link' ? 'https://' : ''),
      file: file,
      description: '',
      weight: 50
    };
    setSources([...sources, newSource]);
  };

  const handleFileInput = (type) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = type === 'image' ? 'image/*' : '*/*';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (file) {
        addSource(type, file);
      }
    };
    input.click();
  };

  const updateSourceName = (id, name) => {
    setSources(sources.map(s => s.id === id ? { ...s, name } : s));
  };

  const updateSourceWeight = (id, weight) => {
    setSources(sources.map(s => s.id === id ? { ...s, weight } : s));
  };

  const updateSourceDescription = (id, description) => {
    setSources(sources.map(s => s.id === id ? { ...s, description } : s));
  };

  const deleteSource = (id) => {
    setSources(sources.filter(s => s.id !== id));
  };

  const sourceIcons = {
    link: Link2,
    image: Image,
    text: FileText,
    file: Paperclip,
  };

  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      {/* Page Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">Nowa analiza scenariuszy</h1>
        <p className="text-gray-600 max-w-3xl">
          Wybierz parametry analizy i dodaj źródła, na podstawie których system
          przygotuje scenariusze dla państwa Atlantis.
        </p>
      </div>

      {/* Sections */}
      <div className="space-y-6">
        {/* Basic Parameters Section */}
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Podstawowe parametry analizy</h2>

          <div className="space-y-6">
            {/* Analysis Name */}
            <div className="space-y-2">
              <label htmlFor="analysis-name" className="block text-sm font-medium text-gray-700">
                Nazwa analizy
              </label>
              <input
                id="analysis-name"
                type="text"
                value={analysisName}
                onChange={(e) => setAnalysisName(e.target.value)}
                placeholder="Wpływ cen ropy na bezpieczeństwo Atlantis"
                className="max-w-2xl w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Country */}
            <div className="space-y-2">
              <label htmlFor="country" className="block text-sm font-medium text-gray-700">
                Państwo
              </label>
              <select
                id="country"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                className="max-w-xs w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Atlantis">Atlantis</option>
                <option value="Pacifica">Pacifica</option>
                <option value="Nordica">Nordica</option>
              </select>
            </div>

            {/* Time Horizon */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Horyzont czasowy
                {!timeHorizon12 && !timeHorizon36 && (
                  <span className="text-red-600 text-xs ml-2">Wybierz co najmniej jedną opcję</span>
                )}
              </label>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setTimeHorizon12(!timeHorizon12)}
                  className={`px-6 py-2 rounded-md border transition-colors ${
                    timeHorizon12
                      ? 'bg-blue-50 border-blue-600 text-blue-700'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  12 miesięcy
                </button>
                <button
                  type="button"
                  onClick={() => setTimeHorizon36(!timeHorizon36)}
                  className={`px-6 py-2 rounded-md border transition-colors ${
                    timeHorizon36
                      ? 'bg-blue-50 border-blue-600 text-blue-700'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  36 miesięcy
                </button>
              </div>
            </div>

            {/* Scenario Variants */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Wariant scenariusza
                {!positiveScenario && !negativeScenario && (
                  <span className="text-red-600 text-xs ml-2">Wybierz co najmniej jedną opcję</span>
                )}
              </label>
              <div className="flex gap-6">
                <div className="flex items-center gap-2">
                  <input
                    id="positive"
                    type="checkbox"
                    checked={positiveScenario}
                    onChange={(e) => setPositiveScenario(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="positive" className="text-sm cursor-pointer">
                    Pozytywny dla interesów Atlantis
                  </label>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    id="negative"
                    type="checkbox"
                    checked={negativeScenario}
                    onChange={(e) => setNegativeScenario(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="negative" className="text-sm cursor-pointer">
                    Negatywny dla interesów Atlantis
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sources Section */}
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-5">Źródła do analizy</h2>

          {/* Action Buttons */}
          <div className="flex gap-2 mb-6">
            <button
              type="button"
              onClick={() => addSource('link')}
              className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition flex items-center gap-2"
            >
              <Link2 className="w-4 h-4" />+ Link
            </button>
            <button
              type="button"
              onClick={() => handleFileInput('image')}
              className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition flex items-center gap-2"
            >
              <Image className="w-4 h-4" />+ Obraz
            </button>
            <button
              type="button"
              onClick={() => addSource('text')}
              className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />+ Tekst
            </button>
            <button
              type="button"
              onClick={() => handleFileInput('file')}
              className="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition flex items-center gap-2"
            >
              <Paperclip className="w-4 h-4" />+ Plik
            </button>
          </div>

          {/* Sources List */}
          {sources.length > 0 && (
            <div className="space-y-0 divide-y divide-gray-100">
              {sources.map((source) => {
                const Icon = sourceIcons[source.type];
                return (
                  <div
                    key={source.id}
                    className="py-4 first:pt-0 hover:bg-gray-50 transition-colors px-3 -mx-3 rounded-md"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 mt-1">
                        <Icon className="w-5 h-5 text-gray-500" />
                      </div>

                      <div className="flex-1 min-w-0 space-y-2">
                        <div>
                          {source.type === 'link' ? (
                            <>
                              <input
                                type="text"
                                value={source.name}
                                onChange={(e) => updateSourceName(source.id, e.target.value)}
                                placeholder="https://example.com"
                                className="text-sm h-8 w-full px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              />
                              <input
                                type="text"
                                value={source.description}
                                onChange={(e) => updateSourceDescription(source.id, e.target.value)}
                                placeholder="Krótki opis"
                                className="mt-1.5 text-sm h-8 w-full px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              />
                            </>
                          ) : source.type === 'text' ? (
                            <textarea
                              value={source.description}
                              onChange={(e) => updateSourceDescription(source.id, e.target.value)}
                              placeholder="Wpisz tekst do analizy..."
                              rows="4"
                              className="text-sm w-full px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                            />
                          ) : (
                            <>
                              <p className="text-sm break-all">{source.name}</p>
                              <input
                                type="text"
                                value={source.description}
                                onChange={(e) => updateSourceDescription(source.id, e.target.value)}
                                placeholder="Krótki opis"
                                className="mt-1.5 text-sm h-8 w-full px-2 py-1 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                              />
                            </>
                          )}
                        </div>

                        {/* Weight Slider */}
                        <div className="flex items-center gap-4 max-w-md">
                          <span className="text-sm text-gray-600 whitespace-nowrap">
                            Waga źródła
                          </span>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            step="5"
                            value={source.weight}
                            onChange={(e) => updateSourceWeight(source.id, parseInt(e.target.value))}
                            className="flex-1"
                          />
                          <span className="text-sm w-8 text-right">{source.weight}</span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          type="button"
                          className="text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 px-2 py-1 rounded transition flex items-center gap-1"
                        >
                          <Eye className="w-4 h-4" />
                          Podgląd
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteSource(source.id)}
                          className="text-sm text-red-600 hover:text-red-700 hover:bg-red-50 px-2 py-1 rounded transition flex items-center gap-1"
                        >
                          <Trash2 className="w-4 h-4" />
                          Usuń
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Scope Section */}
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-5">Zakres źródeł w analizie</h2>

          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <input
                id="added"
                type="radio"
                name="sourceScope"
                value="added"
                checked={sourceScope === 'added'}
                onChange={(e) => setSourceScope(e.target.value)}
                className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <label htmlFor="added" className="text-sm cursor-pointer">
                Analiza tylko na dodanych źródłach
              </label>
            </div>
            <div className="flex items-center space-x-3">
              <input
                id="extended"
                type="radio"
                name="sourceScope"
                value="extended"
                checked={sourceScope === 'extended'}
                onChange={(e) => setSourceScope(e.target.value)}
                className="w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <label htmlFor="extended" className="text-sm cursor-pointer">
                Dodane źródła + dodatkowe wartościowe źródła MSZ
              </label>
            </div>
          </div>

          <p className="text-sm text-gray-500 mt-4 ml-7">
            W drugim wariancie system automatycznie dobierze dodatkowe, sprawdzone źródła pasujące do
            tematu analizy.
          </p>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="flex items-center justify-end gap-3 mt-10 pt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={handleCancel}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition"
        >
          Anuluj
        </button>
        <button
          type="button"
          onClick={handleSaveDraft}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition"
        >
          Zapisz jako szkic
        </button>
        <button
          type="button"
          onClick={handleRunAnalysis}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
        >
          Uruchom analizę
        </button>
      </div>
    </div>
  );
}
