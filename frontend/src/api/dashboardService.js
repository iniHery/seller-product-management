// src/api/dashboardService.js
import api from './axios';

/**
 * Get dashboard statistics for the authenticated seller
 * @returns {Promise} Axios response promise
 */
export function getDashboardStats() {
  return api.get('/dashboard/');
}
