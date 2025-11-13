import axios from 'axios';

// API Base URL - change this for production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minutes for routing queries
});

// API Service
export const logisticsAPI = {
  // Health & Stats
  async getHealth() {
    const response = await api.get('/health');
    return response.data;
  },

  async getStats() {
    const response = await api.get('/stats');
    return response.data;
  },

  async getTools() {
    const response = await api.get('/tools');
    return response.data;
  },

  // Agent Query (Natural Language)
  async askAgent(query, options = {}) {
    const payload = {
      query: query,
      context: options.context || null,
      max_iterations: options.maxIterations || 5,
      include_explanation: options.includeExplanation !== false,
    };

    const response = await api.post('/ask', payload);
    return response.data;
  },

  // Direct VRP Solver (Baseline)
  async solveDirect(orderIds, vehicleIds, options = {}) {
    const payload = {
      order_ids: orderIds,
      vehicle_ids: vehicleIds,
      constraints: options.constraints || {},
      objective: options.objective || 'minimize_distance',
    };

    const response = await api.post('/solve_vrp_direct', payload);
    return response.data;
  },

  // Scenario Comparison (What-If Analysis)
  async compareScenarios(orderIds, vehicleIds, scenarios) {
    const payload = {
      order_ids: orderIds,
      vehicle_ids: vehicleIds,
      scenarios: scenarios,
    };

    const response = await api.post('/compare_scenarios', payload);
    return response.data;
  },

  // Parameter Sensitivity Analysis
  async analyzeSensitivity(orderIds, vehicleIds, parameter, minValue, maxValue, steps = 5) {
    const payload = {
      order_ids: orderIds,
      vehicle_ids: vehicleIds,
      parameter: parameter,
      min_value: minValue,
      max_value: maxValue,
      steps: steps,
    };

    const response = await api.post('/analyze_sensitivity', payload);
    return response.data;
  },

  // Helper functions for common queries
  async getQuickStats() {
    try {
      const stats = await this.getStats();
      return {
        orders: stats.database_stats?.orders_count || 0,
        vehicles: stats.database_stats?.vehicles_count || 0,
        totalQueries: stats.api_stats?.total_queries || 0,
      };
    } catch (error) {
      console.error('Error fetching quick stats:', error);
      return { orders: 0, vehicles: 0, totalQueries: 0 };
    }
  },

  // Example queries
  getExampleQueries() {
    return {
      simple: [
        "How many orders and vehicles do we have?",
        "Show me all cold-chain orders",
        "What vehicles have capacity over 200 units?",
      ],
      basic_routing: [
        "Route 5 deliveries with 1 vehicle",
        "Route 10 deliveries with 2 vehicles, minimize distance",
        "Assign 15 orders to 3 vehicles",
      ],
      complex_routing: [
        "Route 20 deliveries with 3 vehicles, minimize cost. Prioritize cold-chain items.",
        "Create routes for all high-priority orders using fastest vehicles",
        "Balance workload across 5 vehicles for 30 deliveries",
      ],
      cost_analysis: [
        "Calculate cost difference between 2 vs 3 vehicles for 10 deliveries",
        "What would emissions be for 20 deliveries?",
        "Compare cost of minimizing distance vs minimizing time",
      ],
    };
  },
};

export default logisticsAPI;
