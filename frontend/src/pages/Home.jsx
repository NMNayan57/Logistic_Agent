import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bot, Settings, TrendingUp, Package, Truck, MapPin, ArrowRight, Zap, Brain } from 'lucide-react';
import logisticsAPI from '../services/api';

function Home() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ orders: 0, vehicles: 0, totalQueries: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await logisticsAPI.getQuickStats();
        console.log('Stats fetched:', data);
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
        console.error('Error details:', error.response || error.message);
        // Set default values on error so user sees something
        setStats({ orders: 0, vehicles: 0, totalQueries: 0 });
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  const exampleQueries = logisticsAPI.getExampleQueries();

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900">
          Logistics Copilot
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          AI-powered routing assistant using natural language • Powered by GPT-4 and OR-Tools
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Orders in Database</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {loading ? '...' : stats.orders}
              </p>
            </div>
            <div className="bg-blue-50 p-3 rounded-lg">
              <Package className="h-8 w-8 text-blue-500" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Available Vehicles</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {loading ? '...' : stats.vehicles}
              </p>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <Truck className="h-8 w-8 text-green-500" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Queries</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">
                {loading ? '...' : stats.totalQueries}
              </p>
            </div>
            <div className="bg-purple-50 p-3 rounded-lg">
              <TrendingUp className="h-8 w-8 text-purple-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Choice - AI vs Manual */}
      <div className="grid md:grid-cols-2 gap-6 mt-8">
        {/* AI Mode Card */}
        <div
          onClick={() => navigate('/agent')}
          className="bg-gradient-to-br from-primary-50 to-blue-50 rounded-2xl shadow-lg border-2 border-primary-200 p-8 cursor-pointer hover:shadow-xl hover:scale-105 transition-all duration-300"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="bg-primary-500 p-3 rounded-xl">
              <Bot className="h-10 w-10 text-white" />
            </div>
            <div className="bg-green-100 px-3 py-1 rounded-full">
              <span className="text-xs font-semibold text-green-700">RECOMMENDED</span>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-3">
            Copilot Mode
          </h2>

          <p className="text-gray-600 mb-6">
            Just describe what you need in plain English. Your AI copilot will understand your requirements and create optimal routes.
          </p>

          <div className="space-y-3 mb-6">
            <div className="flex items-start space-x-2">
              <Brain className="h-5 w-5 text-primary-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">Natural language interface - no technical knowledge needed</span>
            </div>
            <div className="flex items-start space-x-2">
              <Zap className="h-5 w-5 text-primary-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">Automatic tool selection and optimization</span>
            </div>
            <div className="flex items-start space-x-2">
              <MapPin className="h-5 w-5 text-primary-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">Detailed explanations of routing decisions</span>
            </div>
          </div>

          <button className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-6 rounded-lg flex items-center justify-center space-x-2 transition">
            <span>Start with Copilot</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>

        {/* Manual Mode Card */}
        <div
          onClick={() => navigate('/direct')}
          className="bg-gradient-to-br from-gray-50 to-slate-50 rounded-2xl shadow-lg border-2 border-gray-200 p-8 cursor-pointer hover:shadow-xl hover:scale-105 transition-all duration-300"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="bg-gray-600 p-3 rounded-xl">
              <Settings className="h-10 w-10 text-white" />
            </div>
            <div className="bg-gray-100 px-3 py-1 rounded-full">
              <span className="text-xs font-semibold text-gray-700">ADVANCED</span>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-3">
            Direct Solver Mode
          </h2>

          <p className="text-gray-600 mb-6">
            Directly configure optimization parameters and constraints. Full control over the routing algorithm.
          </p>

          <div className="space-y-3 mb-6">
            <div className="flex items-start space-x-2">
              <Settings className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">Manual parameter selection and fine-tuning</span>
            </div>
            <div className="flex items-start space-x-2">
              <Zap className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">Slightly faster execution (no LLM overhead)</span>
            </div>
            <div className="flex items-start space-x-2">
              <MapPin className="h-5 w-5 text-gray-600 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-700">Raw optimization output for analysis</span>
            </div>
          </div>

          <button className="w-full bg-gray-700 hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-lg flex items-center justify-center space-x-2 transition">
            <span>Use Direct Solver</span>
            <ArrowRight className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Example Queries Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Example Queries to Try</h3>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Simple Queries:</h4>
            <div className="space-y-2">
              {exampleQueries.simple.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => navigate('/agent', { state: { query } })}
                  className="w-full text-left px-4 py-2 bg-gray-50 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg text-sm text-gray-700 hover:text-primary-700 transition"
                >
                  "{query}"
                </button>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Routing Queries:</h4>
            <div className="space-y-2">
              {exampleQueries.basic_routing.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => navigate('/agent', { state: { query } })}
                  className="w-full text-left px-4 py-2 bg-gray-50 hover:bg-primary-50 border border-gray-200 hover:border-primary-300 rounded-lg text-sm text-gray-700 hover:text-primary-700 transition"
                >
                  "{query}"
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Research Note */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <div className="bg-amber-100 p-2 rounded-lg flex-shrink-0">
            <Brain className="h-5 w-5 text-amber-600" />
          </div>
          <div>
            <h4 className="font-semibold text-amber-900 mb-1">Research Demo</h4>
            <p className="text-sm text-amber-800">
              This is a research prototype comparing LLM-based agent routing with traditional optimization algorithms.
              Use the "Compare" page to see side-by-side performance metrics for your research paper.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
