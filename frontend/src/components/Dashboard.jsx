import { useNavigate, useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [jobDetails, setJobDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) {
      setJobDetails(null);
      return;
    }
    const fetchJobDetails = async () => {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8080/api/processing/status/${id}`);
        const data = await res.json();
        setJobDetails(data);
      } catch (err) {
        console.error('Failed to fetch job details:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchJobDetails();
    const interval = setInterval(fetchJobDetails, 3000);
    return () => clearInterval(interval);
  }, [id]);

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      processing: 'bg-blue-100 text-blue-800 border-blue-300',
      completed: 'bg-green-100 text-green-800 border-green-300',
      failed: 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('pl-PL', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  if (id && loading && !jobDetails) {
    return (
      <div className="px-20 py-16">
        <div className="max-w-5xl mx-auto">
          <div className="bg-white rounded-xl shadow-sm p-12 text-center">
            <div className="text-gray-500">Ładowanie...</div>
          </div>
        </div>
      </div>
    );
  }

  if (id && jobDetails) {
    return (
      <div className="px-20 py-16">
        <div className="max-w-5xl mx-auto space-y-8">
          <div className="bg-white rounded-xl shadow-sm p-8">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Job Details</h2>
                <div className="text-sm text-gray-500 font-mono">{jobDetails.job_uuid}</div>
              </div>
              <span className={`px-4 py-2 rounded-lg border-2 font-semibold ${getStatusColor(jobDetails.status)}`}>
                {jobDetails.status.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-6 mb-8">
              <div>
                <div className="text-sm text-gray-500 mb-1">Created</div>
                <div className="font-medium">{formatDate(jobDetails.created_at)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500 mb-1">Updated</div>
                <div className="font-medium">{formatDate(jobDetails.updated_at)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500 mb-1">Completed</div>
                <div className="font-medium">{formatDate(jobDetails.completed_at)}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500 mb-1">Progress</div>
                <div className="font-medium">
                  {jobDetails.completed_items}/{jobDetails.total_items} items completed
                  {jobDetails.failed_items > 0 && ` (${jobDetails.failed_items} failed)`}
                </div>
              </div>
            </div>

            {jobDetails.error_message && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-sm font-semibold text-red-800 mb-1">Error</div>
                <div className="text-sm text-red-700">{jobDetails.error_message}</div>
              </div>
            )}

            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Items ({jobDetails.items?.length || 0})</h3>
              <div className="space-y-3">
                {jobDetails.items?.map((item) => (
                  <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-mono text-gray-500">#{item.id}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(item.status)}`}>
                          {item.status}
                        </span>
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                          {item.type}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-600">${item.wage}</span>
                    </div>
                    <div className="text-sm text-gray-700 mb-2">
                      <span className="font-medium">Content:</span> {item.content.substring(0, 100)}
                      {item.content.length > 100 && '...'}
                    </div>
                    {item.processed_content && (
                      <div className="text-sm text-green-700 bg-green-50 p-2 rounded">
                        <span className="font-medium">Processed:</span> {item.processed_content}
                      </div>
                    )}
                    {item.error_message && (
                      <div className="text-sm text-red-700 bg-red-50 p-2 rounded">
                        <span className="font-medium">Error:</span> {item.error_message}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-12">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Wyniki Analizy</h3>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-16 text-center">
              <div className="text-gray-400 text-lg">
                Placeholder na wyniki analizy
              </div>
              <div className="text-gray-400 text-sm mt-2">
                To będzie zawierać szczegółowe wyniki przetwarzania
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="px-20 py-16">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* New Analysis Card */}
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Przeprowadź nową analizę</h2>
          <button
            onClick={() => navigate('/create')}
            className="px-8 py-3 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 font-medium transition"
          >
            + nowa analiza
          </button>
        </div>
      </div>
    </div>
  );
}
