import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function CreateAnalysisForm() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [country, setCountry] = useState('');
  const [timeHorizon, setTimeHorizon] = useState({ twelve: false, thirtySix: false });
  const [scenario, setScenario] = useState({ positive: false, negative: false });
  const [textSources, setTextSources] = useState(['', '']);
  const [files, setFiles] = useState([]);

  const isFormValid = name && (files.length > 0 || textSources.some(t => t.trim()));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid) return;
    console.log({ name, country, timeHorizon, scenario, textSources, files });
  };

  const handleFileUpload = (e) => {
    setFiles([...files, ...Array.from(e.target.files)]);
  };

  const addTextSource = () => {
    setTextSources([...textSources, '']);
  };

  return (
    <div className="px-16 py-10">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-sm p-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Przeprowadź nową analizę</h1>
          <p className="text-gray-500 text-base mb-10">Wypełnij formularz aby rozpocząć</p>

          <form onSubmit={handleSubmit} className="space-y-10">
            {/* Section 1: Basic Data */}
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-6 pb-2 border-t-2 border-gray-200 pt-6">
                Podstawowe dane
              </h2>
              
              <div className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Dodaj nazwę</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Nazwa analizy"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Państwo</label>
                  <select
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">Wybierz państwo</option>
                    <option value="PL">Polska</option>
                    <option value="US">USA</option>
                    <option value="DE">Niemcy</option>
                    <option value="RU">Rosja</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Horyzont czasowy</label>
                  <div className="flex gap-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={timeHorizon.twelve}
                        onChange={(e) => setTimeHorizon({ ...timeHorizon, twelve: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">12 miesięcy</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={timeHorizon.thirtySix}
                        onChange={(e) => setTimeHorizon({ ...timeHorizon, thirtySix: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">36 miesięcy</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">Wariant scenariusza</label>
                  <div className="flex gap-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={scenario.positive}
                        onChange={(e) => setScenario({ ...scenario, positive: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">pozytywny</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={scenario.negative}
                        onChange={(e) => setScenario({ ...scenario, negative: e.target.checked })}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">negatywny</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Section 2: Data Sources */}
            <div className="border-t-2 border-gray-200 pt-8">
              <h2 className="text-xl font-bold text-gray-900 mb-2">Źródła do analizy</h2>
              <p className="text-gray-500 text-sm mb-6">Dodaj źródło (plik lub tekst) i określ jego wagę.</p>

              {/* File Upload Area */}
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center bg-gray-50 mb-6">
                <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Dodaj plik</h3>
                <p className="text-sm text-gray-500 mb-4">Przeciągnij pliki tutaj lub</p>
                <label className="inline-block px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-md cursor-pointer hover:bg-gray-50 transition">
                  Wybierz plik z komputera
                  <input type="file" multiple onChange={handleFileUpload} className="hidden" />
                </label>
                <p className="text-xs text-gray-500 mt-4">Dodaj: link, obraz, plik tekstowy lub arkusz kalkulacyjny</p>
                {files.length > 0 && (
                  <div className="mt-4 text-left max-w-md mx-auto">
                    {files.map((file, i) => (
                      <div key={i} className="text-sm text-green-600">✓ {file.name}</div>
                    ))}
                  </div>
                )}
              </div>

              {/* Text Input Areas */}
              <div className="space-y-4">
                {textSources.map((source, index) => (
                  <div key={index}>
                    <textarea
                      value={source}
                      onChange={(e) => {
                        const updated = [...textSources];
                        updated[index] = e.target.value;
                        setTextSources(updated);
                      }}
                      className="w-full px-4 py-4 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                      rows="4"
                      placeholder="Wskaźnik zaistniałej przed miesiącem katastrofy naturalnej wśród państw producenta graficznych karcią 60% względnie..."
                    />
                  </div>
                ))}
                <button
                  type="button"
                  onClick={addTextSource}
                  className="px-5 py-2 text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 transition"
                >
                  + Dodaj
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end gap-4 pt-6">
              <button
                type="button"
                onClick={() => navigate('/')}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition"
              >
                Anuluj
              </button>
              <button
                type="submit"
                disabled={!isFormValid}
                className="px-8 py-3.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition font-semibold text-base"
              >
                Analizuj
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
