import api from './axios';

export function getProducts(params = {}) {
  return api.get('/products/', {
    params,
  });
}

export function getProduct(id) {
  return api.get(`/products/${id}/`);
}

export function createProduct(data) {
  return api.post('/products/', data);
}

export function updateProduct(id, data) {
  return api.put(`/products/${id}/`, data);
}

export function patchProduct(id, data) {
  return api.patch(`/products/${id}/`, data);
}

export function deleteProduct(id) {
  return api.delete(`/products/${id}/`);
}

export function toggleProductFavorite(id) {
  return api.post(`/products/${id}/favorite/`);
}

export function exportProductsCSV(params = {}) {
  return api.get('/products/export/', {
    params,
    responseType: 'blob',
  });
}

export function downloadProductTemplateCSV() {
  return api.get('/products/template/', {
    responseType: 'blob',
  });
}

export function importProductsCSV(file) {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/products/import/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

/**
 * Melakukan aksi massal (bulk) pada produk yang dipilih.
 *
 * @param {Object} payload
 * @param {string[]} payload.ids - Daftar UUID produk yang dipilih.
 * @param {string} payload.action - Aksi: 'delete' | 'set_status'.
 * @param {string} [payload.status] - Status baru ('active'|'inactive'), wajib saat action='set_status'.
 * @returns {Promise} Response dari API.
 */
export function bulkProductAction(payload) {
  return api.post('/products/bulk-action/', payload);
}