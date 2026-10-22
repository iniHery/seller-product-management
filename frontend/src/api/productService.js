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