/**
 * Membuat fungsi debounce yang menunda eksekusi fn selama `delay` ms
 * setelah pemanggilan terakhir.
 *
 * @param {Function} fn - Fungsi yang ingin di-debounce.
 * @param {number} delay - Jeda waktu dalam milidetik.
 * @returns {Function} Fungsi debounced.
 */
export default function debounce(fn, delay) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

