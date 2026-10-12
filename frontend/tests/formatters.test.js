import test from 'node:test';
import assert from 'node:assert/strict';

import { formatCurrency, formatDateTime } from '../src/utils/formatters.js';

test('formats currency with Indonesian Rupiah and grouped digits', () => {
  const formatted = formatCurrency(1234567).replace(/\s/g, ' ');

  assert.match(formatted, /Rp 1\.234\.567/);
});

test('returns a fallback for missing or invalid date values', () => {
  assert.equal(formatDateTime(''), '-');
  assert.equal(formatDateTime('not-a-date'), '-');
});
