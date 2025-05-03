import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '';

/**
 * API Service for interacting with the Flask backend
 */
class ApiService {
  /**
   * Get all available asset categories and symbols
   */
  static async getAssets() {
    try {
      const response = await axios.get(`${API_URL}/api/assets`);
      return response.data;
    } catch (error) {
      console.error('Error fetching assets:', error);
      throw error;
    }
  }
  
  /**
   * Get available parameter sets
   */
  static async getParameters() {
    try {
      const response = await axios.get(`${API_URL}/api/parameters`);
      return response.data;
    } catch (error) {
      console.error('Error fetching parameters:', error);
      throw error;
    }
  }
  
  /**
   * Get raw price data for a symbol
   * @param {string} symbol - The trading symbol
   * @param {string} period - Time period (e.g., '1y', '6mo')
   * @param {string} interval - Data interval (e.g., '1d', '1h')
   */
  static async getData(symbol, period = '1y', interval = '1d') {
    try {
      const response = await axios.get(`${API_URL}/api/data/${symbol}`, {
        params: { period, interval }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching data for ${symbol}:`, error);
      throw error;
    }
  }
  
  /**
   * Get calculated indicators for a symbol
   * @param {string} symbol - The trading symbol
   * @param {string} parameterSet - Parameter set to use
   * @param {string} period - Time period
   * @param {string} interval - Data interval
   */
  static async getIndicators(symbol, parameterSet = 'default', period = '1y', interval = '1d') {
    try {
      const response = await axios.get(`${API_URL}/api/indicators/${symbol}`, {
        params: { parameter_set: parameterSet, period, interval }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching indicators for ${symbol}:`, error);
      throw error;
    }
  }
  
  /**
   * Generate charts for a symbol
   * @param {string} symbol - The trading symbol
   * @param {Array} parameterSets - Array of parameter sets
   * @param {string} period - Time period
   * @param {string} interval - Data interval
   */
  static async generateCharts(symbol, parameterSets = ['default'], period = '1y', interval = '1d') {
    try {
      const parameterSetsStr = parameterSets.join(',');
      const response = await axios.get(`${API_URL}/api/charts/${symbol}`, {
        params: { parameter_sets: parameterSetsStr, period, interval }
      });
      return response.data;
    } catch (error) {
      console.error(`Error generating charts for ${symbol}:`, error);
      throw error;
    }
  }
  
  /**
   * Get optimal indicators for an asset type
   * @param {string} assetType - The asset type (forex, commodities, indices)
   */
  static async getOptimalIndicators(assetType) {
    try {
      const response = await axios.get(`${API_URL}/api/optimal_indicators/${assetType}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching optimal indicators for ${assetType}:`, error);
      throw error;
    }
  }
  
  /**
   * Get market summary data for dashboard
   * @returns {Array} Latest market data for key assets
   */
  static async getMarketSummary() {
    try {
      const response = await axios.get(`${API_URL}/api/market_summary`);
      return response.data;
    } catch (error) {
      console.error('Error fetching market summary:', error);
      throw error;
    }
  }

  /**
   * Get recent reports for the dashboard
   * @param {number} limit - Maximum number of reports to return
   * @returns {Array} Recent report data
   */
  static async getRecentReports(limit = 5) {
    try {
      const response = await axios.get(`${API_URL}/api/recent_reports`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching recent reports:', error);
      // If API endpoint not yet implemented, return mock data
      if (error.response && error.response.status === 404) {
        return [
          {
            symbol: 'EURUSD',
            parameterSet: 'trend_following',
            date: '2025-05-02',
            filename: 'EURUSD_interactive_report_20250502_trend_following.html',
            url: '/reports/EURUSD_interactive_report_20250502_trend_following.html'
          },
          {
            symbol: 'GOLD',
            parameterSet: 'default',
            date: '2025-05-03',
            filename: 'GOLD_interactive_report_20250503_default.html',
            url: '/reports/GOLD_interactive_report_20250503_default.html'
          },
          {
            symbol: 'GBPUSD',
            parameterSet: 'momentum',
            date: '2025-05-01',
            filename: 'GBPUSD_interactive_report_20250501_momentum.html',
            url: '/reports/GBPUSD_interactive_report_20250501_momentum.html'
          }
        ];
      }
      throw error;
    }
  }

  /**
   * General purpose GET request to API
   * @param {string} endpoint - The API endpoint URL (including any path parameters)
   * @param {Object} params - Optional query parameters
   */
  static async get(endpoint, params = {}) {
    try {
      const response = await axios.get(`${API_URL}${endpoint}`, { params });
      return response.data;
    } catch (error) {
      console.error(`Error making GET request to ${endpoint}:`, error);
      throw error;
    }
  }
}

export default ApiService;