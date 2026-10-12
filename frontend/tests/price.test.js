import test from 'node:test';
import assert from 'node:assert/strict';

import { parsePriceInput } from '../src/utils/price.js';

test('parses Indonesian thousands and decimal separators', () => {
  assert.deepEqual(parsePriceInput('1.234,56'), {
    formattedValue: '1.234,56',
    numericValue: '1234.56',
    hasDecimalSeparator: true,
    separatorIndex: 5,
  });
});

test('accepts a dot as a decimal separator when it is not a thousands group', () => {
  const result = parsePriceInput('12.50');

  assert.equal(result.formattedValue, '12,50');
  assert.equal(result.numericValue, '12.50');
});

test('treats a three-digit dot group as thousands', () => {
  const result = parsePriceInput('12.500');

  assert.equal(result.formattedValue, '12.500');
  assert.equal(result.numericValue, '12500');
});

test('accepts pasted values using US separators', () => {
  const result = parsePriceInput('1,234.50');

  assert.equal(result.formattedValue, '1.234,50');
  assert.equal(result.numericValue, '1234.50');
});

test('limits fractional input to two digits and keeps incomplete decimals editable', () => {
  const result = parsePriceInput('10,999');

  assert.equal(result.formattedValue, '10,99');
  assert.equal(result.numericValue, '10.99');
  assert.equal(parsePriceInput('10,').formattedValue, '10,');
  assert.equal(parsePriceInput('10.').formattedValue, '10,');
});

test('preserves negative values for form validation and clears non-numeric input', () => {
  assert.equal(parsePriceInput('-5').numericValue, '-5');
  assert.equal(parsePriceInput('abc').numericValue, '');
});
