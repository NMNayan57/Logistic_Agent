import { useState } from 'react';
import { Settings, Play, Clock, TrendingDown, Truck, AlertCircle, CheckCircle, Download } from 'lucide-react';
import logisticsAPI from '../services/api';

function DirectMode() {
  const [orderIds, setOrderIds] = useState('O001,O002,O003,O004,O005');
  const [vehicleIds, setVehicleIds] = useState('V001,V002');
  const [objective, setObjective] = useState('minimize_distance');
  const [maxTime, setMaxTime] = useState(480);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSolve(e) {
    e.preventDefault();
    if (loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const orders = orderIds.split(',').map(id => id.trim()).filter(Boolean);
      const vehicles = vehicleIds.split(',').map(id => id.trim()).filter(Boolean);

      if (orders.length === 0 || vehicles.length === 0) {
        throw new Error('Please provide at least one order and one vehicle');
      }

      const response = await logisticsAPI.solveDirect(orders, vehicles, {
        objective: objective,
        constraints: {
          max_time: maxTime
        }
      });

      setResult(response);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to solve VRP');
      console.error('Direct solver error:', err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-700 to-gray-900 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center space-x-3 mb-3">
          <Settings className="h-10 w-10" />
          <h1 className="text-3xl font-bold">Direct Solver Mode</h1>
        </div>
        <p className="text-gray-200">
          Configure optimization parameters manually for full control over the routing algorithm.
        </p>
      </div>

      {/* Configuration Form */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSolve} className="space-y-6">
          {/* Orders Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Order IDs (comma-separated)
            </label>
            <input
              type="text"
              value={orderIds}
              onChange={(e) => setOrderIds(e.target.value)}
              placeholder="O001,O002,O003"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter order IDs from the database (e.g., O001, O002, O003...)
            </p>
          </div>

          {/* Vehicles Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vehicle IDs (comma-separated)
            </label>
            <input
              type="text"
              value={vehicleIds}
              onChange={(e) => setVehicleIds(e.target.value)}
              placeholder="V001,V002"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              disabled={loading}
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter vehicle IDs from the database (e.g., V001, V002, V003...)
            </p>
          </div>

          {/* Objective Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Optimization Objective
            </label>
            <select
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              disabled={loading}
            >
              <option value="minimize_distance">Minimize Distance</option>
              <option value="minimize_cost">Minimize Cost</option>
              <option value="minimize_time">Minimize Time</option>
            </select>
          </div>

          {/* Constraints */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Route Duration (minutes)
            </label>
            <input
              type="number"
              value={maxTime}
              onChange={(e) => setMaxTime(Number(e.target.value))}
              min="60"
              max="1440"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-500 focus:border-transparent"
              disabled={loading}
            />
          </div>

          {/* Solve Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 bg-gray-700 hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-lg transition"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Solving...</span>
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                <span>Solve VRP</span>
              </>
            )}
          </button>
        </form>

        {loading && (
          <div className="mt-4 text-center text-sm text-gray-500">
            This may take 10-20 seconds...
          </div>
        )}
      </div>

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
        <div className="space-y-6">
          {/* Success Banner */}
          <div className="bg-green-50 border border-green-200 rounded-xl p-6">
            <div className="flex items-center space-x-3">
              <CheckCircle className="h-6 w-6 text-green-600" />
              <div>
                <h3 className="font-semibold text-green-900">Solution Found!</h3>
                <p className="text-sm text-green-700">
                  Status: {result.solver_status} • Time: {result.execution_time_seconds?.toFixed(2)}s
                </p>
              </div>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-1">
                <Clock className="h-4 w-4 text-blue-500" />
                <span className="text-xs font-medium text-gray-500">Execution Time</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{result.execution_time_seconds?.toFixed(2)}s</p>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-1">
                <Truck className="h-4 w-4 text-green-500" />
                <span className="text-xs font-medium text-gray-500">Routes</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">{result.routes?.length || 0}</p>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center space-x-2 mb-1">
                <TrendingDown className="h-4 w-4 text-yellow-500" />
                <span className="text-xs font-medium text-gray-500">Total Cost</span>
              </div>
              <p className="text-2xl font-bold text-gray-900">${result.total_cost?.toFixed(2) || '---'}</p>
            </div>
          </div>

          {/* Constraint Violations Warning */}
          {result.metadata?.constraint_violations && result.metadata.constraint_violations.length > 0 && (
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6">
              <div className="flex items-start space-x-3 mb-4">
                <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-lg font-bold text-red-900">⚠️ Constraint Violations Detected</h3>
                  <p className="text-sm text-red-700">
                    {result.metadata.constraint_violations.length} operational constraint(s) violated. Routes may not be safe for dispatch.
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                {result.metadata.constraint_violations.map((violation, idx) => (
                  <div key={idx} className={`p-3 rounded-lg ${
                    violation.severity === 'critical' ? 'bg-red-100 border border-red-300' : 'bg-yellow-100 border border-yellow-300'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-900">
                          {violation.type === 'driver_overtime' ? '⏰ Driver Overtime' : '🧊 Cold-Chain Limit'}
                        </p>
                        <p className="text-xs text-gray-700 mt-1">{violation.message}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        violation.severity === 'critical' ? 'bg-red-600 text-white' : 'bg-yellow-600 text-white'
                      }`}>
                        {violation.severity === 'critical' ? 'CRITICAL' : 'WARNING'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Routes Details */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Routes</h3>
            <div className="space-y-4">
              {result.routes?.map((route, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-900">Route {idx + 1}</h4>
                    <span className="px-2 py-1 bg-gray-100 rounded text-sm font-medium text-gray-700">
                      {route.vehicle_id}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Distance:</span>
                      <p className="font-semibold text-gray-900">{route.total_distance_km?.toFixed(2)} km</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Time:</span>
                      <p className="font-semibold text-gray-900">{route.total_time_minutes?.toFixed(0)} min</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Cost:</span>
                      <p className="font-semibold text-gray-900">${route.total_cost_usd?.toFixed(2)}</p>
                    </div>
                    <div>
                      <span className="text-gray-500">Stops:</span>
                      <p className="font-semibold text-gray-900">{route.stops?.length || 0}</p>
                    </div>
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Stop Sequence:</p>
                    <p className="text-sm text-gray-700">{route.stops?.join(' → ') || 'No stops'}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Raw JSON Output */}
          <details className="bg-gray-50 rounded-xl border border-gray-200 p-6">
            <summary className="font-semibold text-gray-900 cursor-pointer">
              View Raw JSON Output
            </summary>
            <pre className="mt-4 p-4 bg-white border border-gray-200 rounded-lg overflow-x-auto text-xs">
              {JSON.stringify(result.metadata, null, 2)}
            </pre>
          </details>

          {/* Actions */}
          <div className="flex space-x-4">
            <button className="flex-1 bg-gray-700 hover:bg-gray-800 text-white font-semibold py-3 px-6 rounded-lg transition">
              Approve Solution
            </button>
            <button className="bg-white hover:bg-gray-50 border-2 border-gray-300 text-gray-700 font-semibold py-3 px-6 rounded-lg transition flex items-center space-x-2">
              <Download className="h-5 w-5" />
              <span>Export JSON</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DirectMode;
