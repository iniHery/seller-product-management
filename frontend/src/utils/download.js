/**
 * Formats a Date object into DD-MM-YYYY string.
 *
 * @param {Date} [date=new Date()]
 * @returns {string} e.g. "22-10-2026"
 */
export function formatDateDMY(date = new Date()) {
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}-${month}-${year}`;
}

/**
 * Generates a formatted CSV filename: [prefix]-[tgl]-[bulan]-[tahun].csv
 *
 * @param {string} prefix - The base filename (e.g. "produk", "produk-stok-kritis", "template-import-produk")
 * @param {Date} [date=new Date()]
 * @returns {string} e.g. "produk-22-10-2026.csv"
 */
export function generateCSVFilename(prefix, date = new Date()) {
  return `${prefix}-${formatDateDMY(date)}.csv`;
}

/**
 * Triggers a browser download of a Blob object with the specified filename.
 *
 * @param {Blob} blob - The file content blob
 * @param {string} filename - The default filename for the download
 */
export function triggerFileDownload(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
