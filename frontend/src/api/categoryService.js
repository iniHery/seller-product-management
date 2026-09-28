// src/api/categoryService.js
import api from './axios';

/**
 * Get list of categories
 * @returns {Promise} Axios response promise
 */
export function getCategories() {
  return api.get('/categories/');
}

/**
 * Create a new category
 * @param {Object} data - { name: string }
 * @returns {Promise} Axios response promise
 */
export function createCategory(data) {
  return api.post('/categories/', data);
}

/**
 * Update a category (full update)
 * @param {string} id - Category UUID
 * @param {Object} data - { name: string }
 * @returns {Promise} Axios response promise
 */
export function updateCategory(id, data) {
  return api.put(`/categories/${id}/`, data);
}

/**
 * Partial update a category
 * @param {string} id - Category UUID
 * @param {Object} data - Partial fields
 * @returns {Promise} Axios response promise
 */
export function patchCategory(id, data) {
  return api.patch(`/categories/${id}/`, data);
}

/**
 * Delete a category
 * @param {string} id - Category UUID
 * @returns {Promise} Axios response promise
 */
export function deleteCategory(id) {
  return api.delete(`/categories/${id}/`);
}
