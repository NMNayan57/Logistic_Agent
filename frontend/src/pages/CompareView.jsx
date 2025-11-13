import { useState } from 'react';
import { GitCompare, Bot, Settings, Play, Camera, Download, TrendingUp, Clock, DollarSign } from 'lucide-react';
import logisticsAPI from '../services/api';
import html2canvas from 'html2canvas';

function CompareView() {
  const [query, setQuery] = useState('Route 10 deliveries with 2 vehicles, minimize distance');
  const [loading, setLoading] = useState(false);
  const [agentResult, setAgentResult] = useState(null);
  const [directResult, setDirectResult] = useState(null);

  async function handleCompare() {
    setLoading(true);
    setAgentResult(null);
    setDirectResult(null);

    try {
      // Run both in parallel
      const [agentResponse, directResponse] = await Promise.all([
        logisticsAPI.askAgent(query, { maxIterations: 5 }),
        logisticsAPI.solveDirect(['O001', 'O002', 'O003', 'O004', 'O005', 'O006', 'O007', 'O008', 'O009', 'O010'], ['V001', 'V002'], { objective: 'minimize_distance' })
      ]);

      setAgentResult(agentResponse);
      setDirectResult(directResponse);
    } catch (error) {
      console.error('Comparison error:', error);
      alert('Failed to run comparison: ' + error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleScreenshot() {
    const element = document.getElementById('comparison-container');
    if (element) {
      const canvas = await html2canvas(element, { scale: 2 });
      const link = document.createElement('a');
      link.download = `comparison-${Date.now()}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  }

  function exportToCSV() {
    if (!agentResult || !directResult) return;

    const data = [
      ['Metric', 'AI Agent', 'Direct Solver', 'Difference'],
      ['Execution Time (s)', agentResult.execution_time_seconds?.toFixed(2), directResult.execution_time_seconds?.toFixed(2), ((agentResult.execution_time_seconds - directResult.execution_time_seconds) / directResult.execution_time_seconds * 100).toFixed(1) + '%'],
      ['Total Cost ($)', agentResult.total_cost?.toFixed(2) || 'N/A', directResult.total_cost?.toFixed(2) || 'N/A', 'N/A'],
      ['Routes Generated', agentResult.routes?.length || 0, directResult.routes?.length || 0, (agentResult.routes?.length - directResult.routes?.length)],
      ['Tools Called', agentResult.tools_called?.length || 0, '0', agentResult.tools_called?.length || 0],
      ['Natural Language Input', 'Yes', 'No', '-'],
      ['Explanation Provided', 'Yes', 'No', '-'],
    ];

    const csv = data.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `comparison-data-${Date.now()}.csv`;
    link.click();
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-3">
              <GitCompare className="h-10 w-10" />
              <h1 className="text-3xl font-bold">Comparison Mode</h1>
            </div>
            <p className="text-purple-100">
              Side-by-side comparison of AI Agent vs Direct Solver for research analysis
            </p>
          </div>
          {(agentResult && directResult) && (
            <div className="flex space-x-3">
              <button
                onClick={handleScreenshot}
                className="flex items-center space-x-2 bg-white hover:bg-purple-50 text-purple-600 font-semibold px-4 py-2 rounded-lg transition"
              >
                <Camera className="h-5 w-5" />
                <span>Screenshot</span>
              </button>
              <button
                onClick={exportToCSV}
                className="flex items-center space-x-2 bg-purple-500 hover:bg-purple-700 text-white font-semibold px-4 py-2 rounded-lg transition"
              >
                <Download className="h-5 w-5" />
                <span>Export CSV</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Query Input */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Test Query (for AI Agent)
        </label>
        <div className="flex space-x-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            onClick={handleCompare}
            disabled={loading}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white font-semibold px-6 py-3 rounded-lg transition"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Running...</span>
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                <span>Run Comparison</span>
              </>
            )}
          </button>
        </div>
        {loading && (
          <p className="mt-2 text-sm text-gray-500">
            Running both approaches in parallel... This may take 30-40 seconds
          </p>
        )}
      </div>

      {/* Side-by-Side Comparison */}
      {(agentResult && directResult) && (
        <div id="comparison-container" className="space-y-6">
          {/* Comparison Table */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Performance Comparison</h2>
            </div>
            <div className="grid grid-cols-3 divide-x divide-gray-200">
              {/* Header Column */}
              <div className="p-6 bg-gray-50">
                <h3 className="font-semibold text-gray-700 mb-4">Metric</h3>
                <div className="space-y-6">
                  {['Input Method', 'Execution Time', 'Routes Generated', 'Total Cost', 'Tools Used', 'Explanation', 'User Experience'].map((metric, idx) => (
                    <div key={idx} className="h-12 flex items-center text-sm font-medium text-gray-900">
                      {metric}
                    </div>
                  ))}
                </div>
              </div>

              {/* AI Agent Column */}
              <div className="p-6 bg-blue-50">
                <div className="flex items-center space-x-2 mb-4">
                  <Bot className="h-5 w-5 text-blue-600" />
                  <h3 className="font-semibold text-blue-900">AI Agent</h3>
                </div>
                <div className="space-y-6">
                  <div className="h-12 flex items-center">
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Natural Language</span>
                  </div>
                  <div className="h-12 flex items-center text-sm">
                    <span className="font-bold text-gray-900">{agentResult.execution_time_seconds?.toFixed(2)}s</span>
                    <span className="ml-2 text-gray-500">({(agentResult.execution_time_seconds || 0) > (directResult.execution_time_seconds || 0) ? '+' : ''}{(((agentResult.execution_time_seconds || 0) - (directResult.execution_time_seconds || 0)) / (directResult.execution_time_seconds || 1) * 100).toFixed(1)}%)</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="font-bold text-gray-900">{agentResult.routes?.length || 0} routes</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="font-bold text-gray-900">${agentResult.total_cost?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="font-bold text-gray-900">{agentResult.tools_called?.length || 0} tools</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">✓ Yes</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">Easy (Conversational)</span>
                  </div>
                </div>
              </div>

              {/* Direct Solver Column */}
              <div className="p-6 bg-gray-50">
                <div className="flex items-center space-x-2 mb-4">
                  <Settings className="h-5 w-5 text-gray-600" />
                  <h3 className="font-semibold text-gray-900">Direct Solver</h3>
                </div>
                <div className="space-y-6">
                  <div className="h-12 flex items-center">
                    <span className="px-3 py-1 bg-gray-200 text-gray-800 rounded-full text-xs font-semibold">Structured Parameters</span>
                  </div>
                  <div className="h-12 flex items-center text-sm">
                    <span className="font-bold text-gray-900">{directResult.execution_time_seconds?.toFixed(2)}s</span>
                    <span className="ml-2 text-gray-500">(baseline)</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="font-bold text-gray-900">{directResult.routes?.length || 0} routes</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="font-bold text-gray-900">${directResult.total_cost?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="font-bold text-gray-900">0 tools</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">✗ No</span>
                  </div>
                  <div className="h-12 flex items-center">
                    <span className="px-3 py-1 bg-gray-200 text-gray-800 rounded-full text-xs font-semibold">Technical (Manual)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Key Findings */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Findings for Research Paper</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-semibold text-blue-900 mb-2 flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Solution Quality</span>
                </h4>
                <p className="text-sm text-blue-800">
                  AI Agent produced comparable solution quality with only{' '}
                  <strong>{(((agentResult.total_cost || 0) - (directResult.total_cost || 0)) / (directResult.total_cost || 1) * 100).toFixed(1)}%</strong>{' '}
                  cost difference
                </p>
              </div>

              <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                <h4 className="font-semibold text-purple-900 mb-2 flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Time Overhead</span>
                </h4>
                <p className="text-sm text-purple-800">
                  AI Agent added{' '}
                  <strong>{((agentResult.execution_time_seconds || 0) - (directResult.execution_time_seconds || 0)).toFixed(1)}s</strong>{' '}
                  overhead for natural language processing
                </p>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2 flex items-center space-x-2">
                  <Bot className="h-5 w-5" />
                  <span>User Experience</span>
                </h4>
                <p className="text-sm text-green-800">
                  AI Agent provides <strong>natural language</strong> interface with detailed explanations,
                  making optimization accessible to non-experts
                </p>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-900 mb-2 flex items-center space-x-2">
                  <DollarSign className="h-5 w-5" />
                  <span>Trade-off Analysis</span>
                </h4>
                <p className="text-sm text-yellow-800">
                  Small time overhead (<strong>{(((agentResult.execution_time_seconds || 0) - (directResult.execution_time_seconds || 0)) / (directResult.execution_time_seconds || 1) * 100).toFixed(0)}%</strong>)
                  is acceptable trade-off for improved usability
                </p>
              </div>
            </div>
          </div>

          {/* Research Paper Citation Box */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-2 border-indigo-200 rounded-xl p-6">
            <h3 className="font-bold text-indigo-900 mb-3">For Your Research Paper:</h3>
            <div className="space-y-2 text-sm text-indigo-800">
              <p>
                <strong>RQ1 (Solution Quality):</strong> Agent achieved {((1 - Math.abs((agentResult.total_cost || 0) - (directResult.total_cost || 0)) / (directResult.total_cost || 1)) * 100).toFixed(1)}% solution quality compared to direct solver
              </p>
              <p>
                <strong>RQ2 (Efficiency):</strong> Agent execution time was {(((agentResult.execution_time_seconds || 0) / (directResult.execution_time_seconds || 1)) * 100).toFixed(0)}% of direct solver baseline
              </p>
              <p>
                <strong>RQ3 (Explainability):</strong> Only AI Agent provided natural language explanations and reasoning transparency
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      {!(agentResult && directResult) && !loading && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
          <GitCompare className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to Compare</h3>
          <p className="text-gray-600 mb-4">
            Click "Run Comparison" to see AI Agent vs Direct Solver side-by-side
          </p>
          <p className="text-sm text-gray-500">
            Perfect for generating comparison tables and figures for your research paper
          </p>
        </div>
      )}
    </div>
  );
}

export default CompareView;
