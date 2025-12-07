import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, X } from 'lucide-react';
import ReactFlow, {
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';

export default function ReasoningPath() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState('list'); // 'list' | 'diagram'
  const [jobData, setJobData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });

  // ReactFlow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`http://localhost:8080/api/jobs/${id}`);
        const data = await response.json();
        setJobData(data);
        
        if (data.nodes && data.node_relations) {
          prepareGraphData(data.nodes, data.node_relations);
        }
      } catch (error) {
        console.error('Error fetching job data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const prepareGraphData = (apiNodes, apiRelations) => {
    // Simple layout strategy: columns based on type
    const facts = apiNodes.filter(n => n.type === 'fact');
    const predictions = apiNodes.filter(n => n.type === 'prediction');
    const missing = apiNodes.filter(n => n.type === 'missing_information');
    const others = apiNodes.filter(n => !['fact', 'prediction', 'missing_information'].includes(n.type));

    const newNodes = [];
    const xSpacing = 400;
    const ySpacing = 150;

    // Helper to add nodes
    const addNodes = (list, colIndex, startY = 0) => {
      list.forEach((node, index) => {
        let label = node.value;
        if (label.length > 50) label = label.substring(0, 50) + '...';
        
        let bg = '#fff';
        let border = '#0F2743';
        
        if (node.type === 'fact') {
          bg = '#FFFBEB'; // Amber-50
          border = '#D9A441';
        } else if (node.type === 'prediction') {
          bg = '#ECFDF5'; // Emerald-50
          border = '#10B981';
        } else if (node.type === 'missing_information') {
          bg = '#FEF2F2'; // Red-50
          border = '#EF4444';
        }

        newNodes.push({
          id: node.id,
          type: 'default',
          data: { label: (
            <div className="p-2">
              <div className="text-xs font-bold uppercase mb-1 opacity-70">{node.type}</div>
              <div className="text-sm">{label}</div>
            </div>
          ) },
          position: { x: colIndex * xSpacing, y: startY + index * ySpacing },
          style: { 
            background: bg,
            border: `1px solid ${border}`,
            borderRadius: '8px',
            width: 300,
          }
        });
      });
    };

    addNodes(facts, 0);
    addNodes(predictions, 1);
    addNodes(missing, 2);
    addNodes(others, 1, predictions.length * ySpacing);

    const newEdges = apiRelations.map(rel => ({
      id: rel.id,
      source: rel.source_node_id,
      target: rel.target_node_id,
      label: rel.relation_type,
      type: 'smoothstep',
      markerEnd: {
        type: MarkerType.ArrowClosed,
      },
      style: { stroke: '#0F2743', strokeWidth: 1.5 },
      labelStyle: { fill: '#0F2743', fontWeight: 700 }
    }));

    setNodes(newNodes);
    setEdges(newEdges);
  };

  const onNodeMouseEnter = useCallback((event, node) => {
    const rect = event.target.getBoundingClientRect();
    setPopupPosition({ x: rect.right + 10, y: rect.top });
    setHoveredNode(node);
  }, []);

  const onNodeMouseLeave = useCallback(() => {
    setHoveredNode(null);
  }, []);

  const getNodeRelations = useCallback((nodeId) => {
    if (!jobData?.node_relations || !jobData?.nodes) return [];
    return jobData.node_relations
      .filter(rel => rel.source_node_id === nodeId || rel.target_node_id === nodeId)
      .map(rel => {
        const relatedNodeId = rel.source_node_id === nodeId ? rel.target_node_id : rel.source_node_id;
        const relatedNode = jobData.nodes.find(n => n.id === relatedNodeId);
        const direction = rel.source_node_id === nodeId ? 'outgoing' : 'incoming';
        return { ...rel, relatedNode, direction };
      });
  }, [jobData]);

  const getOriginalNode = useCallback((nodeId) => {
    return jobData?.nodes?.find(n => n.id === nodeId);
  }, [jobData]);

  if (loading) {
    return <div className="p-12 text-center">Ładowanie...</div>;
  }

  if (!jobData) {
    return <div className="p-12 text-center">Nie znaleziono danych analizy.</div>;
  }

  const facts = jobData.nodes?.filter(n => n.type === 'fact') || [];
  const predictions = jobData.nodes?.filter(n => n.type === 'prediction') || [];
  const missing = jobData.nodes?.filter(n => n.type === 'missing_information') || [];

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-12 font-sans">
      {/* Header */}
      <div className="mb-12">
        <button
          onClick={() => navigate(`/analysis/${id}`)}
          className="flex items-center gap-2 text-[#D9A441] hover:text-[#D9A441]/80 transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" strokeWidth={1.5} />
          Wróć do wyników
        </button>
        
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-[#0F2743] text-3xl font-bold mb-2">Ścieżka rozumowania</h1>
            <p className="text-[#0F2743]/70">Analiza ID: {jobData.job.job_uuid}</p>
          </div>

          {/* View mode toggle */}
          <div className="flex gap-2 bg-[#0F2743]/5 p-1 rounded-lg">
            <button
              onClick={() => setViewMode('list')}
              className={`px-5 py-2.5 rounded-lg transition-colors font-medium ${
                viewMode === 'list'
                  ? 'bg-white text-[#0F2743] shadow-sm'
                  : 'text-[#0F2743]/60 hover:text-[#0F2743]'
              }`}
            >
              Widok listy
            </button>
            <button
              onClick={() => setViewMode('diagram')}
              className={`px-5 py-2.5 rounded-lg transition-colors font-medium ${
                viewMode === 'diagram'
                  ? 'bg-white text-[#0F2743] shadow-sm'
                  : 'text-[#0F2743]/60 hover:text-[#0F2743]'
              }`}
            >
              Widok diagramu
            </button>
          </div>
        </div>
      </div>

      {viewMode === 'list' ? (
        <div className="grid grid-cols-3 gap-8">
          {/* LEFT COLUMN - Facts */}
          <div className="col-span-2 space-y-8">
            {/* Card: Fakty wejściowe */}
            <div className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 p-8">
              <h2 className="text-[#0F2743] text-xl font-bold mb-6">Fakty wejściowe</h2>
              
              <div className="space-y-5">
                {facts.map(fact => (
                  <div key={fact.id} className="bg-[#D9A441]/5 border border-[#D9A441]/20 rounded-lg p-5">
                    <h3 className="text-[#0F2743] font-medium mb-4">{fact.value}</h3>
                    <div className="flex flex-wrap gap-2 mb-4">
                      <span className="px-3 py-1 bg-white text-[#D9A441] rounded-md border border-[#D9A441]/20 text-sm">
                        {fact.metadata?.category || 'Ogólne'}
                      </span>
                      <span className="px-3 py-1 bg-white text-[#0F2743] rounded-md border border-[#0F2743]/10 text-sm">
                        {fact.metadata?.period || 'N/A'}
                      </span>
                    </div>
                  </div>
                ))}
                {facts.length === 0 && <p className="text-gray-500">Brak faktów.</p>}
              </div>
            </div>

            {/* Card: Wnioski / Predictions */}
            <div className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 p-8">
              <h2 className="text-[#0F2743] text-xl font-bold mb-6">Wnioski i Predykcje</h2>
              
              <div className="space-y-8">
                {predictions.map(pred => (
                  <div key={pred.id}>
                    <h3 className="text-[#0F2743] font-medium mb-3">{pred.value}</h3>
                    <div className="flex gap-2 mb-4">
                       <span className="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-md border border-emerald-200 text-sm">
                        Pewność: {pred.metadata?.confidence_level || 'N/A'}
                      </span>
                    </div>
                    <div className="border-t border-[#0F2743]/10" />
                  </div>
                ))}
                {predictions.length === 0 && <p className="text-gray-500">Brak wniosków.</p>}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN - Missing Info & Stats */}
          <div className="space-y-8">
            {/* Card: Brakujące informacje */}
            <div className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 p-6">
              <h2 className="text-[#0F2743] text-xl font-bold mb-6">Brakujące informacje</h2>
              
              <div className="space-y-3">
                {missing.map(item => (
                  <div key={item.id} className="bg-red-50 text-red-700 px-4 py-3 rounded-lg border border-red-200">
                    <p className="font-medium text-sm">{item.value}</p>
                    <p className="text-xs mt-1 opacity-70">Priorytet: {item.metadata?.priority || 'Normalny'}</p>
                  </div>
                ))}
                {missing.length === 0 && <p className="text-gray-500">Brak brakujących informacji.</p>}
              </div>
            </div>

            {/* Stats Card */}
            <div className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 p-6">
              <h2 className="text-[#0F2743] text-xl font-bold mb-6">Statystyki</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Liczba faktów</span>
                  <span className="font-bold text-[#0F2743]">{facts.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Liczba wniosków</span>
                  <span className="font-bold text-[#0F2743]">{predictions.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Relacje</span>
                  <span className="font-bold text-[#0F2743]">{jobData.node_relations?.length || 0}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Diagram View */
        <div className="bg-white rounded-xl shadow-sm border border-[#0F2743]/10 h-[800px] relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeMouseEnter={onNodeMouseEnter}
            onNodeMouseLeave={onNodeMouseLeave}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>

          {/* Node Details Popup */}
          {hoveredNode && (() => {
            const originalNode = getOriginalNode(hoveredNode.id);
            const relations = getNodeRelations(hoveredNode.id);

            return (
              <div
                className="fixed z-50 bg-white rounded-xl shadow-2xl border border-[#0F2743]/20 p-5 w-[400px] max-h-[500px] overflow-y-auto"
                style={{
                  left: Math.min(popupPosition.x, window.innerWidth - 420),
                  top: Math.min(popupPosition.y, window.innerHeight - 520)
                }}
                onMouseEnter={() => setHoveredNode(hoveredNode)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className={`px-2 py-1 text-xs font-bold uppercase rounded ${
                      originalNode?.type === 'fact' ? 'bg-amber-100 text-amber-700' :
                      originalNode?.type === 'prediction' ? 'bg-emerald-100 text-emerald-700' :
                      originalNode?.type === 'missing_information' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {originalNode?.type || 'Unknown'}
                    </span>
                  </div>
                  <button
                    onClick={() => setHoveredNode(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <h3 className="text-[#0F2743] font-bold mb-3">{originalNode?.value}</h3>

                {originalNode?.metadata && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {originalNode.metadata.category && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                        {originalNode.metadata.category}
                      </span>
                    )}
                    {originalNode.metadata.confidence_level && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-600 text-xs rounded">
                        Pewność: {originalNode.metadata.confidence_level}
                      </span>
                    )}
                    {originalNode.metadata.period && (
                      <span className="px-2 py-1 bg-purple-100 text-purple-600 text-xs rounded">
                        {originalNode.metadata.period}
                      </span>
                    )}
                  </div>
                )}

                {relations.length > 0 && (
                  <>
                    <div className="border-t border-gray-200 my-4" />
                    <h4 className="text-sm font-bold text-[#0F2743] mb-3">
                      Relacje ({relations.length})
                    </h4>
                    <div className="space-y-3">
                      {relations.map((rel, idx) => (
                        <div key={idx} className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`text-xs ${rel.direction === 'outgoing' ? 'text-green-600' : 'text-blue-600'}`}>
                              {rel.direction === 'outgoing' ? '→' : '←'}
                            </span>
                            <span className="px-2 py-0.5 bg-[#0F2743] text-white text-xs rounded font-medium">
                              {rel.relation_type}
                            </span>
                          </div>
                          <div className="text-sm text-[#0F2743]">
                            <span className={`inline-block px-1.5 py-0.5 text-xs rounded mr-2 ${
                              rel.relatedNode?.type === 'fact' ? 'bg-amber-100 text-amber-700' :
                              rel.relatedNode?.type === 'prediction' ? 'bg-emerald-100 text-emerald-700' :
                              rel.relatedNode?.type === 'missing_information' ? 'bg-red-100 text-red-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {rel.relatedNode?.type}
                            </span>
                            <span className="text-gray-700">
                              {rel.relatedNode?.value}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}

                {relations.length === 0 && (
                  <p className="text-gray-500 text-sm italic">Brak relacji dla tego węzła.</p>
                )}
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
