// src/api/productService.js
import api from './axios';

/**
 * Get list of products with optional query params (e.g., pagination, filters)
 * @param {Object} params - query parameters object
 * @returns {Promise} Axios response promise
 */
export function getProducts(params = {}) {
  return api.get('/products/', { params });
}

/**
 * Get a single product by its UUID
 * @param {string} id - product UUID
 */
export function getProduct(id) {
  return api.get(`/products/${id}/`);
}

/**
 * Create a new product
 * @param {Object} data - product payload
 */
export function createProduct(data) {
  return api.post('/products/', data);
}

/**
 * Update a product (full update)
 * @param {string} id - product UUID
 * @param {Object} data - updated product data
 */
export function updateProduct(id, data) {
  return api.put(`/products/${id}/`, data);
}

/**
 * Partially update a product
 * @param {string} id - product UUID
 * @param {Object} data - partial fields to update
 */
export function patchProduct(id, data) {
  return api.patch(`/products/${id}/`, data);
}

/**
 * Delete a product
 * @param {string} id - product UUID
 */
export function deleteProduct(id) {
  return api.delete(`/products/${id}/`);
}
