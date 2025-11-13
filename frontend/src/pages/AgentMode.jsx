import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Bot, Send, Sparkles, Clock, DollarSign, Truck, CheckCircle, AlertCircle, Download, Camera } from 'lucide-react';
import logisticsAPI from '../services/api';
import html2canvas from 'html2canvas';
import CopilotResults from '../components/CopilotResults';

function AgentMode() {
  const location = useLocation();
  const [query, setQuery] = useState(location.state?.query || '');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [thinkingSteps, setThinkingSteps] = useState([]);

  const exampleQueries = logisticsAPI.getExampleQueries();

  useEffect(() => {
    if (location.state?.query) {
      handleSubmit(new Event('submit'));
    }
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setThinkingSteps([]);

    // Simulate thinking steps (in real implementation, we'd stream these from backend)
    const simulateThinking = () => {
      setTimeout(() => setThinkingSteps(prev => [...prev, { step: 1, text: 'Understanding your query...', done: false }]), 500);
      setTimeout(() => setThinkingSteps(prev => prev.map((s, i) => i === 0 ? { ...s, done: true } : s)), 1500);
      setTimeout(() => setThinkingSteps(prev => [...prev, { step: 2, text: 'Analyzing orders and vehicles...', done: false }]), 1600);
      setTimeout(() => setThinkingSteps(prev => prev.map((s, i) => i === 1 ? { ...s, done: true } : s)), 3000);
      setTimeout(() => setThinkingSteps(prev => [...prev, { step: 3, text: 'Calling optimization solver...', done: false }]), 3100);
    };

    simulateThinking();

    try {
      const response = await logisticsAPI.askAgent(query, {
        maxIterations: 5,
        includeExplanation: true
      });

      setThinkingSteps(prev => prev.map(s => ({ ...s, done: true })));
      setTimeout(() => {
        setThinkingSteps(prev => [...prev, { step: 4, text: 'Solution found!', done: true }]);
      }, 100);

      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to process query');
      console.error('Agent query error:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleScreenshot() {
    const element = document.getElementById('results-container');
    if (element) {
      const canvas = await html2canvas(element);
      const link = document.createElement('a');
      link.download = `agent-results-${Date.now()}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-500 to-blue-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center space-x-3 mb-3">
          <Bot className="h-10 w-10" />
          <h1 className="text-3xl font-bold">Logistics Copilot</h1>
        </div>
        <p className="text-primary-50">
          Your AI-powered routing assistant. Describe your delivery needs in plain English and get optimized routes instantly.
        </p>
      </div>

      {/* Query Input */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What would you like to do?
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Example: Route 10 deliveries with 2 vehicles, minimize cost. Prioritize cold-chain items."
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
              disabled={loading}
            />
          </div>

          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-lg transition"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  <span>Ask Copilot</span>
                  <Send className="h-4 w-4" />
                </>
              )}
            </button>

            <div className="text-sm text-gray-500">
              {loading && 'This may take 20-30 seconds...'}
            </div>
          </div>
        </form>

        {/* Example Queries */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-sm font-medium text-gray-700 mb-3">Or try an example:</p>
          <div className="flex flex-wrap gap-2">
            {[...exampleQueries.simple, ...exampleQueries.basic_routing].slice(0, 4).map((example, idx) => (
              <button
                key={idx}
                onClick={() => setQuery(example)}
                disabled={loading}
                className="px-3 py-1.5 bg-gray-100 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg text-xs text-gray-700 hover:text-primary-700 transition disabled:opacity-50"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Thinking Process */}
      {loading && thinkingSteps.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Bot className="h-5 w-5 text-primary-600 animate-pulse" />
            <h3 className="text-lg font-semibold text-gray-900">Copilot is thinking...</h3>
          </div>
          <div className="space-y-3">
            {thinkingSteps.map((step, idx) => (
              <div key={idx} className="flex items-center space-x-3">
                {step.done ? (
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                ) : (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500 flex-shrink-0"></div>
                )}
                <span className={`text-sm ${step.done ? 'text-gray-600' : 'text-gray-900 font-medium'}`}>
                  {step.text}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-6 w-6 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">Error</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {result && (
        <div id="results-container" className="space-y-6">
          {/* Success Banner */}
          <div className="bg-green-50 border border-green-200 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <div>
                  <h3 className="font-semibold text-green-900">Route Plan Ready!</h3>
                  <p className="text-sm text-green-700">
                    Completed in {result.execution_time_seconds?.toFixed(1)}s using {result.tools_called?.length || 0} tools
                  </p>
                </div>
              </div>
              <button
                onClick={handleScreenshot}
                className="flex items-center space-x-2 px-4 py-2 bg-white hover:bg-green-50 border border-green-300 rounded-lg text-sm font-medium text-green-700 transition"
              >
                <Camera className="h-4 w-4" />
                <span>Screenshot</span>
              </button>
            </div>
          </div>

          {/* Copilot Results Component - Displays structured data beautifully */}
          <CopilotResults result={result} />

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button className="flex-1 bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-6 rounded-lg transition">
              Approve & Dispatch
            </button>
            <button className="flex-1 bg-white hover:bg-gray-50 border-2 border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg transition">
              Adjust Routes
            </button>
            <button
              onClick={handleScreenshot}
              className="bg-white hover:bg-gray-50 border-2 border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg transition flex items-center space-x-2"
            >
              <Download className="h-5 w-5" />
              <span>Export</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentMode;
