import { useState } from 'react';
import { Layers, Play, Plus, Trash2, Camera, Download, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';
import logisticsAPI from '../services/api';
import html2canvas from 'html2canvas';


function ScenariosView() {
  const [orderIds, setOrderIds] = useState('O001,O002,O003,O004,O005');
  const [vehicleIds, setVehicleIds] = useState('V001,V002');
  const [scenarios, setScenarios] = useState([
    {
      id: 'baseline',
      name: 'Baseline',
      description: 'Current conditions with standard parameters',
      config: {},
      active: true
    },
    {
      id: 'fuel_spike',
      name: 'Fuel Price Increase',
      description: '25% increase in fuel prices',
      config: { fuel_price_per_liter: 1.875 },
      active: true
    },
    {
      id: 'rush_hour',
      name: 'Rush Hour Traffic',
      description: '20% reduction in average speed',
      config: { avg_speed_reduction: 0.2 },
      active: true
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  function addScenario() {
    const newId = `scenario_${Date.now()}`;
    setScenarios([...scenarios, {
      id: newId,
      name: 'New Scenario',
      description: 'Custom scenario',
      config: {},
      active: true
    }]);
  }

  function removeScenario(id) {
    setScenarios(scenarios.filter(s => s.id !== id));
  }

  function updateScenario(id, field, value) {
    setScenarios(scenarios.map(s =>
      s.id === id ? { ...s, [field]: value } : s
    ));
  }

  function updateScenarioConfig(id, configKey, configValue) {
    setScenarios(scenarios.map(s =>
      s.id === id ? {
        ...s,
        config: { ...s.config, [configKey]: parseFloat(configValue) || 0 }
      } : s
    ));
  }

  async function runComparison() {
    setLoading(true);
    setResults(null);

    try {
      const ordersList = orderIds.split(',').map(id => id.trim()).filter(Boolean);
      const vehiclesList = vehicleIds.split(',').map(id => id.trim()).filter(Boolean);

      // Build scenarios object
      const scenariosObj = {};
      scenarios.filter(s => s.active).forEach(scenario => {
        scenariosObj[scenario.id] = {
          description: scenario.description,
          ...scenario.config
        };
      });

      const response = await logisticsAPI.compareScenarios(ordersList, vehiclesList, scenariosObj);
      setResults(response);
    } catch (error) {
      console.error('Scenario comparison error:', error);
      alert('Failed to compare scenarios: ' + error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleScreenshot() {
    const element = document.getElementById('scenarios-container');
    if (element) {
      const canvas = await html2canvas(element, { scale: 2 });
      const link = document.createElement('a');
      link.download = `scenarios-${Date.now()}.png`;
      link.href = canvas.toDataURL();
      link.click();
    }
  }

  function exportToCSV() {
    if (!results?.comparison_results) return;

    const data = [
      ['Scenario', 'Description', 'Total Cost ($)', 'Total Distance (km)', 'Total Time (min)', 'Emissions (kg)', 'Cost vs Baseline', 'Status']
    ];

    Object.entries(results.comparison_results).forEach(([scenarioId, scenario]) => {
      if (scenario.status === 'success') {
        const metrics = scenario.metrics;
        const diff = scenario.differences;
        data.push([
          scenarioId,
          scenario.description,
          metrics.total_cost_usd?.toFixed(2) || 'N/A',
          metrics.total_distance_km?.toFixed(2) || 'N/A',
          metrics.total_time_minutes?.toFixed(1) || 'N/A',
          metrics.total_emissions_kg?.toFixed(2) || 'N/A',
          diff ? `${diff.cost_delta_percent > 0 ? '+' : ''}${diff.cost_delta_percent}%` : 'Baseline',
          'Success'
        ]);
      }
    });

    const csv = data.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `scenarios-comparison-${Date.now()}.csv`;
    link.click();
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl shadow-lg p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-3">
              <Layers className="h-10 w-10" />
              <h1 className="text-3xl font-bold">What-If Scenarios</h1>
            </div>
            <p className="text-purple-100">
              Test how different conditions affect routing outcomes - perfect for contingency planning
            </p>
          </div>
          {results && (
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

      {/* Input Configuration */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Base Configuration</h2>

        <div className="grid md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Order IDs (comma-separated)
            </label>
            <input
              type="text"
              value={orderIds}
              onChange={(e) => setOrderIds(e.target.value)}
              placeholder="O001,O002,O003"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vehicle IDs (comma-separated)
            </label>
            <input
              type="text"
              value={vehicleIds}
              onChange={(e) => setVehicleIds(e.target.value)}
              placeholder="V001,V002"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={loading}
            />
          </div>
        </div>
      </div>

      {/* Scenarios Configuration */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Scenarios to Compare</h2>
          <button
            onClick={addScenario}
            disabled={loading}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white font-semibold px-4 py-2 rounded-lg transition text-sm"
          >
            <Plus className="h-4 w-4" />
            <span>Add Scenario</span>
          </button>
        </div>

        <div className="space-y-4">
          {scenarios.map((scenario, idx) => (
            <div key={scenario.id} className={`border ${scenario.active ? 'border-purple-300 bg-purple-50' : 'border-gray-200 bg-gray-50'} rounded-lg p-4`}>
              <div className="flex items-start space-x-4">
                <input
                  type="checkbox"
                  checked={scenario.active}
                  onChange={(e) => updateScenario(scenario.id, 'active', e.target.checked)}
                  disabled={loading}
                  className="mt-1 h-5 w-5 text-purple-600 focus:ring-purple-500 border-gray-300 rounded"
                />

                <div className="flex-1 space-y-3">
                  <div className="grid md:grid-cols-2 gap-3">
                    <input
                      type="text"
                      value={scenario.name}
                      onChange={(e) => updateScenario(scenario.id, 'name', e.target.value)}
                      placeholder="Scenario Name"
                      disabled={loading}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-semibold"
                    />
                    <input
                      type="text"
                      value={scenario.description}
                      onChange={(e) => updateScenario(scenario.id, 'description', e.target.value)}
                      placeholder="Description"
                      disabled={loading}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  {/* Scenario Parameters */}
                  <div className="grid md:grid-cols-4 gap-3">
                    <div>
                      <label className="text-xs text-gray-600">Fuel Price ($/L)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={scenario.config.fuel_price_per_liter || ''}
                        onChange={(e) => updateScenarioConfig(scenario.id, 'fuel_price_per_liter', e.target.value)}
                        placeholder="1.5"
                        disabled={loading}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">Driver Wage ($/hr)</label>
                      <input
                        type="number"
                        step="0.5"
                        value={scenario.config.driver_wage_per_hour || ''}
                        onChange={(e) => updateScenarioConfig(scenario.id, 'driver_wage_per_hour', e.target.value)}
                        placeholder="15.0"
                        disabled={loading}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">Speed Reduction (0-1)</label>
                      <input
                        type="number"
                        step="0.1"
                        min="0"
                        max="1"
                        value={scenario.config.avg_speed_reduction || ''}
                        onChange={(e) => updateScenarioConfig(scenario.id, 'avg_speed_reduction', e.target.value)}
                        placeholder="0.0"
                        disabled={loading}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-600">Max Time (min)</label>
                      <input
                        type="number"
                        value={scenario.config.max_route_time_minutes || ''}
                        onChange={(e) => updateScenarioConfig(scenario.id, 'max_route_time_minutes', e.target.value)}
                        placeholder="480"
                        disabled={loading}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {idx > 0 && (
                  <button
                    onClick={() => removeScenario(scenario.id)}
                    disabled={loading}
                    className="text-red-500 hover:text-red-700 disabled:text-gray-400"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={runComparison}
          disabled={loading || scenarios.filter(s => s.active).length < 2}
          className="mt-6 w-full flex items-center justify-center space-x-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-300 text-white font-semibold px-6 py-3 rounded-lg transition"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Running Comparison...</span>
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              <span>Run Comparison ({scenarios.filter(s => s.active).length} scenarios)</span>
            </>
          )}
        </button>

        {loading && (
          <p className="mt-2 text-center text-sm text-gray-500">
            This may take 30-60 seconds depending on number of scenarios...
          </p>
        )}
      </div>

      {/* Results */}
      {results && results.comparison_results && (
        <div id="scenarios-container" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Scenarios Tested</p>
                  <p className="text-3xl font-bold text-gray-900">{results.successful_scenarios || 0}</p>
                </div>
                <Layers className="h-10 w-10 text-purple-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Best Scenario</p>
                  <p className="text-xl font-bold text-green-600">
                    {(() => {
                      const successfulScenarios = Object.entries(results.comparison_results).filter(
                        ([_, s]) => s.status === 'success'
                      );
                      if (successfulScenarios.length === 0) return 'N/A';
                      const best = successfulScenarios.reduce((min, [id, s]) =>
                        s.metrics.total_cost_usd < min[1].metrics.total_cost_usd ? [id, s] : min
                      );
                      return scenarios.find(s => s.id === best[0])?.name || best[0];
                    })()}
                  </p>
                </div>
                <TrendingUp className="h-10 w-10 text-green-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Execution Time</p>
                  <p className="text-3xl font-bold text-gray-900">{results.execution_time_seconds?.toFixed(1)}s</p>
                </div>
                <AlertTriangle className="h-10 w-10 text-yellow-500" />
              </div>
            </div>
          </div>

          {/* Comparison Table */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Scenario Comparison Table</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scenario</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Cost</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Distance</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Emissions</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">vs Baseline</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.entries(results.comparison_results).map(([scenarioId, scenario]) => {
                    if (scenario.status !== 'success') return null;
                    const scenarioInfo = scenarios.find(s => s.id === scenarioId);
                    const metrics = scenario.metrics;
                    const diff = scenario.differences;

                    return (
                      <tr key={scenarioId} className={scenarioId === 'baseline' ? 'bg-blue-50 font-semibold' : ''}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{scenarioInfo?.name || scenarioId}</div>
                            <div className="text-xs text-gray-500">{scenario.description}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          ${metrics.total_cost_usd?.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {metrics.total_distance_km?.toFixed(1)} km
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {metrics.total_time_minutes?.toFixed(0)} min
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {metrics.total_emissions_kg?.toFixed(1)} kg
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {diff ? (
                            <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                              diff.cost_delta_percent > 10 ? 'bg-red-100 text-red-800' :
                              diff.cost_delta_percent > 0 ? 'bg-yellow-100 text-yellow-800' :
                              'bg-green-100 text-green-800'
                            }`}>
                              {diff.cost_delta_percent > 0 ? '+' : ''}{diff.cost_delta_percent}%
                            </span>
                          ) : (
                            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                              Baseline
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Insights */}
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-xl p-6">
            <h3 className="font-bold text-purple-900 mb-3 flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Key Insights</span>
            </h3>
            <div className="space-y-2 text-sm text-purple-800">
              {(() => {
                const successfulScenarios = Object.entries(results.comparison_results).filter(
                  ([_, s]) => s.status === 'success'
                );
                if (successfulScenarios.length < 2) return <p>Run at least 2 scenarios for insights.</p>;

                const baseline = results.comparison_results['baseline'];
                if (!baseline || baseline.status !== 'success') {
                  return <p>Add a baseline scenario for comparison insights.</p>;
                }

                const baselineCost = baseline.metrics.total_cost_usd;
                const worstScenario = successfulScenarios.reduce((max, [id, s]) =>
                  s.metrics.total_cost_usd > max[1].metrics.total_cost_usd ? [id, s] : max
                );
                const bestScenario = successfulScenarios.reduce((min, [id, s]) =>
                  s.metrics.total_cost_usd < min[1].metrics.total_cost_usd ? [id, s] : min
                );

                const costRange = worstScenario[1].metrics.total_cost_usd - bestScenario[1].metrics.total_cost_usd;
                const percentRange = (costRange / baselineCost * 100).toFixed(1);

                return (
                  <>
                    <p>
                      <strong>Cost Range:</strong> Scenarios vary by <strong>${costRange.toFixed(2)}</strong> ({percentRange}% of baseline)
                    </p>
                    <p>
                      <strong>Best Option:</strong> {scenarios.find(s => s.id === bestScenario[0])?.name || bestScenario[0]} saves ${(baselineCost - bestScenario[1].metrics.total_cost_usd).toFixed(2)} vs baseline
                    </p>
                    <p>
                      <strong>Worst Case:</strong> {scenarios.find(s => s.id === worstScenario[0])?.name || worstScenario[0]} costs ${(worstScenario[1].metrics.total_cost_usd - baselineCost).toFixed(2)} more
                    </p>
                    <p>
                      <strong>Recommendation:</strong> {(() => {
                        const fuelScenarios = successfulScenarios.filter(([id, _]) =>
                          scenarios.find(s => s.id === id)?.config.fuel_price_per_liter
                        );
                        if (fuelScenarios.length > 0) {
                          const avgIncrease = fuelScenarios.reduce((sum, [_, s]) =>
                            sum + (s.differences?.cost_delta_percent || 0), 0
                          ) / fuelScenarios.length;
                          return `Fuel price changes have ${avgIncrease.toFixed(0)}% average impact on costs.`;
                        }
                        return 'Test more parameters for detailed recommendations.';
                      })()}
                    </p>
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      {!results && !loading && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
          <Layers className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to Compare Scenarios</h3>
          <p className="text-gray-600 mb-4">
            Configure your scenarios above and click "Run Comparison" to see how different conditions affect routing outcomes
          </p>
          <div className="text-sm text-gray-500 space-y-1">
            <p>Tip: Start with a baseline scenario, then add variations to test</p>
            <p>Common scenarios: fuel price changes, traffic conditions, vehicle availability</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ScenariosView;
