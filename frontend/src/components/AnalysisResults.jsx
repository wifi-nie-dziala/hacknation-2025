import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle2, XCircle, Clock, Download } from 'lucide-react';

export default function AnalysisResults() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [jobData, setJobData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const isBase64 = (str) => {
    if (!str || str.length < 100) return false;
    const base64Pattern = /^[A-Za-z0-9+/]+={0,2}$/;
    return base64Pattern.test(str.substring(0, 200));
  };

  const downloadBase64File = (base64Content, itemId) => {
    try {
      const byteCharacters = atob(base64Content);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/octet-stream' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `file-${itemId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      console.error('Failed to download file:', e);
    }
  };

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
    }, 1000);

    return () => clearInterval(interval);
  }, [id]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
      case 'processing':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-600" />;
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'Oczekuje';
      case 'processing':
        return 'Przetwarzanie...';
      case 'completed':
        return 'Ukończono';
      case 'failed':
        return 'Błąd';
      default:
        return status;
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-8 py-12">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-3 text-lg">Ładowanie...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-8 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">Błąd: {error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
          >
            Powrót do dashboardu
          </button>
        </div>
      </div>
    );
  }

  if (!jobData) return null;

  const { job, steps, facts } = jobData;

  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      <div className="mb-8">
        <button
          onClick={() => navigate('/')}
          className="text-blue-600 hover:text-blue-700 mb-4"
        >
          ← Powrót do dashboardu
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Wyniki analizy</h1>
        <p className="text-gray-600 mt-2">Job UUID: {job.job_uuid}</p>
      </div>

      {/* Status Section */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          {getStatusIcon(job.status)}
          <h2 className="text-xl font-semibold">{getStatusText(job.status)}</h2>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Utworzono:</span>
            <span className="ml-2 font-medium">
              {new Date(job.created_at).toLocaleString('pl-PL')}
            </span>
          </div>
          {job.completed_at && (
            <div>
              <span className="text-gray-600">Ukończono:</span>
              <span className="ml-2 font-medium">
                {new Date(job.completed_at).toLocaleString('pl-PL')}
              </span>
            </div>
          )}
          <div>
            <span className="text-gray-600">Liczba źródeł:</span>
            <span className="ml-2 font-medium">{job.total_items}</span>
          </div>
          <div>
            <span className="text-gray-600">Przetworzone:</span>
            <span className="ml-2 font-medium">
              {job.completed_items} / {job.total_items}
            </span>
          </div>
        </div>

        {job.error_message && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800 text-sm">{job.error_message}</p>
          </div>
        )}
      </div>

      {/* Items Section */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Źródła</h2>
        <div className="space-y-3">
          {job.items.map((item, idx) => (
            <div key={item.id} className="border border-gray-200 rounded-md p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">
                  #{idx + 1} - {item.type.toUpperCase()}
                </span>
                <span className={`px-2 py-1 text-xs rounded ${
                  item.status === 'completed' ? 'bg-green-100 text-green-800' :
                  item.status === 'failed' ? 'bg-red-100 text-red-800' :
                  item.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {item.status}
                </span>
              </div>
              <div className="text-sm text-gray-600">
                {item.type === 'file' && isBase64(item.content) ? (
                  <button
                    onClick={() => downloadBase64File(item.content, item.id)}
                    className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition"
                  >
                    <Download size={16} />
                    Download file
                  </button>
                ) : (
                  <p className="truncate">{item.content}</p>
                )}
              </div>
              {item.wage && (
                <p className="text-xs text-gray-500 mt-1">Waga: {item.wage}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Facts Section */}
      {facts && facts.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Wyekstrahowane fakty ({facts.length})</h2>
          <div className="space-y-3">
            {facts.map((fact, idx) => (
              <div key={fact.id} className="border-l-4 border-blue-500 pl-4 py-2">
                <p className="text-sm">{fact.fact}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span>Confidence: {(fact.confidence * 100).toFixed(0)}%</span>
                  <span>Language: {fact.language}</span>
                  <span className={`px-2 py-0.5 rounded ${
                    fact.validation_status === 'validated' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {fact.validation_status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Steps Section */}
      {steps && steps.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4">Kroki przetwarzania</h2>
          <div className="space-y-2">
            {steps.map((step) => (
              <div key={step.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                {getStatusIcon(step.status)}
                <div className="flex-1">
                  <span className="font-medium">Step {step.step_number}: {step.step_type}</span>
                  {step.error_message && (
                    <p className="text-xs text-red-600 mt-1">{step.error_message}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
