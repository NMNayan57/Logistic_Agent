import { Truck, DollarSign, Clock, MapPin, AlertTriangle, CheckCircle, Package, Gauge, Navigation } from 'lucide-react';

/**
 * Clean, paper-ready results display for Logistics Copilot
 * Extracts structured data from AI response and displays in professional cards
 */
function CopilotResults({ result }) {
  // Extract routing data from the structured response
  const routes = result.routes || [];
  const totalCost = result.total_cost || 0;
  const totalDistance = result.total_distance || 0;
  const totalTime = result.total_time || 0;
  const totalEmissions = result.total_emissions || 0;
  const violations = result.metadata?.constraint_violations || [];

  // If no routes, show minimal fallback
  if (routes.length === 0) {
    return (
      <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <CheckCircle className="h-6 w-6 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="font-semibold text-blue-900 mb-2">Copilot Analysis</h4>
            <p className="text-sm text-blue-800 leading-relaxed whitespace-pre-wrap">
              {result.response_text || 'Query completed successfully.'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Metrics Dashboard */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          icon={<DollarSign className="h-5 w-5 text-green-600" />}
          label="Total Cost"
          value={`$${totalCost.toFixed(2)}`}
          color="green"
        />
        <MetricCard
          icon={<MapPin className="h-5 w-5 text-blue-600" />}
          label="Total Distance"
          value={`${totalDistance.toFixed(1)} km`}
          color="blue"
        />
        <MetricCard
          icon={<Clock className="h-5 w-5 text-purple-600" />}
          label="Total Time"
          value={`${Math.floor(totalTime / 60)}h ${Math.round(totalTime % 60)}m`}
          color="purple"
        />
        <MetricCard
          icon={<Gauge className="h-5 w-5 text-orange-600" />}
          label="CO₂ Emissions"
          value={`${totalEmissions.toFixed(1)} kg`}
          color="orange"
        />
      </div>

      {/* Constraint Violations Alert */}
      {violations.length > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-5">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-bold text-red-900 mb-2">
                {violations.length} Constraint Violation{violations.length > 1 ? 's' : ''} Detected
              </h3>
              <div className="space-y-2">
                {violations.map((v, idx) => (
                  <div key={idx} className="bg-white rounded-md p-3 border border-red-200">
                    <p className="text-sm font-semibold text-red-800">
                      {v.type === 'driver_overtime' ? '⏰ Driver Overtime' : '🧊 Cold-Chain Violation'}
                    </p>
                    <p className="text-sm text-gray-700 mt-1">{v.message}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Routes Display */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200 px-6 py-4">
          <h3 className="text-lg font-bold text-gray-900 flex items-center space-x-2">
            <Truck className="h-5 w-5 text-primary-600" />
            <span>Optimized Route Plan ({routes.length} vehicle{routes.length !== 1 ? 's' : ''})</span>
          </h3>
        </div>

        <div className="divide-y divide-gray-200">
          {routes.map((route, idx) => (
            <RouteCard key={idx} route={route} index={idx + 1} />
          ))}
        </div>
      </div>

      {/* AI Insight (condensed summary) */}
      {result.response_text && (
        <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-5">
          <div className="flex items-start space-x-3">
            <CheckCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-blue-900 mb-2">Copilot Summary</h4>
              <p className="text-sm text-blue-800 leading-relaxed">
                {extractInsight(result.response_text)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tools Used */}
      {result.tools_called && result.tools_called.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">Tools Executed:</h4>
          <div className="flex flex-wrap gap-2">
            {result.tools_called.map((tool, idx) => (
              <span key={idx} className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-medium text-gray-700">
                {tool}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Extract key insight from AI response (first 2-3 sentences)
function extractInsight(text) {
  const sentences = text.split(/[.!?]/).filter(s => s.trim().length > 0);
  return sentences.slice(0, 2).join('. ') + (sentences.length > 2 ? '.' : '');
}

// Metric Card Component
function MetricCard({ icon, label, value, color }) {
  const colorClasses = {
    green: 'from-green-50 to-emerald-50 border-green-200',
    blue: 'from-blue-50 to-cyan-50 border-blue-200',
    purple: 'from-purple-50 to-pink-50 border-purple-200',
    orange: 'from-orange-50 to-amber-50 border-orange-200'
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} rounded-lg p-4 border`}>
      <div className="flex items-center space-x-2 mb-2">
        {icon}
        <span className="text-xs font-medium text-gray-600 uppercase tracking-wide">{label}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
    </div>
  );
}

// Route Card Component
function RouteCard({ route, index }) {
  const stops = route.stops || [];
  const distance = route.distance_km || route.total_distance_km || 0;
  const time = route.time_minutes || route.total_time_minutes || 0;
  const vehicleId = route.vehicle_id || `Vehicle ${index}`;
  
  // Get vehicle info
  const vehicleInfo = route.vehicle_info || {};
  const vehicleType = vehicleInfo.vehicle_type || 'Unknown';
  
  // Check for cold-chain capability
  const hasColdChain = vehicleInfo.has_cold_chain || false;

  // Format stops: Depot → C001 → C002 → ... → Depot
  const formatStop = (stop) => {
    if (!stop) return '';
    if (stop.includes('D0') || stop.toLowerCase().includes('depot')) return 'Depot';
    // Format customer IDs nicely
    if (stop.includes('C0')) return stop.replace('Customer ', '');
    if (stop.includes('O0')) return stop.replace('O0', 'C');
    return stop;
  };

  const stopLabels = stops.map(formatStop);

  return (
    <div className="p-5 hover:bg-gray-50 transition">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className="bg-primary-100 text-primary-700 font-bold text-sm w-10 h-10 rounded-full flex items-center justify-center">
            {index}
          </div>
          <div>
            <h4 className="font-bold text-gray-900">{vehicleId}</h4>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs text-gray-600">{vehicleType}</span>
              {hasColdChain && (
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                  🧊 Cold-Chain
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex space-x-4 text-sm">
          <div className="text-center">
            <div className="text-xs text-gray-500">Distance</div>
            <div className="font-semibold text-gray-900">{distance.toFixed(1)} km</div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500">Time</div>
            <div className="font-semibold text-gray-900">
              {Math.floor(time / 60)}h {Math.round(time % 60)}m
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-gray-500">Stops</div>
            <div className="font-semibold text-gray-900">{stops.length}</div>
          </div>
        </div>
      </div>

      {/* Route Visualization */}
      <div className="flex items-center space-x-2 text-sm text-gray-600 overflow-x-auto pb-2">
        {stopLabels.map((stop, idx) => (
          <div key={idx} className="flex items-center space-x-2 flex-shrink-0">
            <span className={`px-3 py-1 rounded font-medium whitespace-nowrap ${
              stop === 'Depot' 
                ? 'bg-primary-100 text-primary-700 border border-primary-300' 
                : 'bg-gray-100 text-gray-700 border border-gray-300'
            }`}>
              {stop}
            </span>
            {idx < stopLabels.length - 1 && (
              <Navigation className="h-3 w-3 text-gray-400" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default CopilotResults;
