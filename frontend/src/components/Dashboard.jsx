import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const navigate = useNavigate();
  
  const analyses = [
    { id: 1, title: 'Atlantis-Trump-kupuje-kopalnię-w-Polsce', date: '1 grudnia 2025r.', time: 'godz.12:43' },
    { id: 2, title: 'Ropa-Rosja', date: '30 listopada 2025r.', time: 'godz.11:13' }
  ];

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

        {/* Previous Analyses Card */}
        <div className="bg-white rounded-xl shadow-sm p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Wcześniejsze analizy</h3>
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                onClick={() => navigate(`/analysis/${analysis.id}`)}
                className="flex items-center gap-6 p-5 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md cursor-pointer transition"
              >
                <div className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-900 rounded-full flex items-center justify-center font-bold">
                  {analysis.id}
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{analysis.title}</h4>
                </div>
                <div className="text-right text-sm text-gray-500">
                  <div>{analysis.date}</div>
                  <div>{analysis.time}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
