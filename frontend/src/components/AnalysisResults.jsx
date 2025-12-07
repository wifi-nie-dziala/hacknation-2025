import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle2, XCircle, Clock, Download, ChevronDown, Info, ArrowRight } from 'lucide-react';

export default function AnalysisResults() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [jobData, setJobData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchJobStatus = async () => {
    try {
      const response = await fetch(`http://localhost:8080/api/jobs/${id}`);
      const data = await response.json();

      if (response.ok) {
        setJobData(data);
        setError(null);
        return data.job.status;
      } else {
        setError(data.error);
        return null;
      }
    } catch (err) {
      setError('Nie udało się pobrać danych');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobStatus();
    const interval = setInterval(async () => {
      const status = await fetchJobStatus();
      if (status === 'completed' || status === 'failed') {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-[#D9A441]" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-600 mb-4">{error}</div>
        <button onClick={() => navigate('/')} className="text-[#0F2743] underline">Wróć do dashboardu</button>
      </div>
    );
  }

  const predictions = jobData?.nodes?.filter(n => n.type === 'prediction') || [];
  const facts = jobData?.nodes?.filter(n => n.type === 'fact') || [];

  return (
    <div className="max-w-[1200px] mx-auto px-6 py-12 font-sans">
      {/* Page header */}
      <div className="mb-12">
        <h1 className="text-[#0F2743] text-3xl font-bold mb-2">Wyniki analizy</h1>
        <p className="text-[#0F2743]/60">ID Analizy: {jobData?.job?.job_uuid}</p>
        <div className="mt-4 flex items-center gap-2">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            jobData?.job?.status === 'completed' ? 'bg-green-100 text-green-800' :
            jobData?.job?.status === 'failed' ? 'bg-red-100 text-red-800' :
            'bg-blue-100 text-blue-800'
          }`}>
            {jobData?.job?.status?.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Filter bar */}
      <div className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 p-5 mb-8">
        <div className="flex items-center gap-4">
          <select className="px-4 py-3 border border-[#0F2743]/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#D9A441] focus:border-transparent bg-white">
            <option>Wszystkie kategorie</option>
            <option>Finansowe</option>
            <option>Operacyjne</option>
          </select>
          
          <button className="px-4 py-3 border border-[#0F2743]/20 rounded-lg text-[#0F2743] hover:bg-[#0F2743]/5 transition-colors flex items-center gap-2">
            Filtry
            <ChevronDown className="w-4 h-4" strokeWidth={1.5} />
          </button>

          <div className="flex-1"></div>

          {jobData?.job?.status?.toUpperCase() === 'COMPLETED' && <button 
            onClick={() => navigate(`/reasoning/${id}`)}
            className="px-6 py-3 bg-[#0F2743] text-white rounded-lg hover:bg-[#0F2743]/90 transition-colors flex items-center gap-2"
          >
            Zobacz ścieżkę rozumowania
            <ArrowRight className="w-4 h-4" />
          </button>}
        </div>
      </div>

      {/* Card: Streszczenie analizy */}
      <div className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 p-8 mb-8">
        <h2 className="text-[#0F2743] text-xl font-bold mb-6">Streszczenie analizy</h2>
        
        <div className="mb-4">
          <p className="text-[#0F2743]/80 mb-4">
            Analiza została zakończona. Przetworzono {jobData?.job?.total_items} elementów. 
            Zidentyfikowano {facts.length} kluczowych faktów oraz wygenerowano {predictions.length} wniosków/predykcji.
          </p>
          {predictions.length > 0 && (
            <p className="text-[#0F2743]/80 mb-4">
              Główny wniosek: {predictions[0].value}
            </p>
          )}
        </div>
      </div>

      <div className="border-t border-[#0F2743]/10 mb-8" />

      {/* Helper text */}
      <div className="flex items-start gap-2 mb-8 text-[#0F2743]/60">
        <Info className="w-5 h-5 mt-0.5 flex-shrink-0" strokeWidth={1.5} />
        <p>Poniżej znajdują się wygenerowane wnioski i predykcje.</p>
      </div>

      {/* Card: Scenariusze / Predictions */}
      <div className="space-y-6">
        {predictions.map((pred, index) => (
          <div key={pred.id} className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 p-6 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-[#0F2743] text-lg font-bold mb-2">Wniosek #{index + 1}</h3>
                <div className="flex gap-2">
                  <span className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded border border-blue-100">
                    {pred.metadata?.period || 'Ogólny'}
                  </span>
                  <span className="px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded border border-purple-100">
                    Pewność: {pred.metadata?.confidence_level || 'N/A'}
                  </span>
                </div>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-[#D9A441]">{pred.metadata?.confidence_level === 'high' ? 'High' : 'Med'}</span>
                <p className="text-xs text-gray-400">Confidence</p>
              </div>
            </div>
            
            <p className="text-[#0F2743]/80 mb-4">
              {pred.value}
            </p>

            <div className="flex justify-end">
              <button 
                onClick={() => navigate(`/reasoning/${id}`)}
                className="text-[#D9A441] hover:text-[#D9A441]/80 text-sm font-medium flex items-center gap-1"
              >
                Szczegóły
                <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
        
        {predictions.length === 0 && (
          <div className="text-center py-12 text-gray-500 bg-white rounded-xl border border-dashed border-gray-300">
            Brak wygenerowanych wniosków.
          </div>
        )}
      </div>
    </div>
  );
}
