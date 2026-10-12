export function parsePriceInput(value) {
  const input = String(value).trim();
  const isNegative = input.startsWith('-');
  const unsignedInput = input.replace(/-/g, '').replace(/[^\d.,]/g, '');
  const lastCommaIndex = unsignedInput.lastIndexOf(',');
  const lastDotIndex = unsignedInput.lastIndexOf('.');
  const separatorIndex = Math.max(lastCommaIndex, lastDotIndex);
  const separator = separatorIndex === -1
    ? ''
    : unsignedInput[separatorIndex];
  const digitsAfterSeparator = separator
    ? unsignedInput.slice(separatorIndex + 1).replace(/\D/g, '').length
    : 0;
  const hasDecimalSeparator = separator === ','
    || (separator === '.' && digitsAfterSeparator <= 2);
  const integerInput = hasDecimalSeparator
    ? unsignedInput.slice(0, separatorIndex)
    : unsignedInput;
  const fractionalInput = hasDecimalSeparator
    ? unsignedInput.slice(separatorIndex + 1)
    : '';
  const integerPart = integerInput.replace(/\D/g, '').replace(/^0+(?=\d)/, '');
  const fractionalPart = fractionalInput.replace(/\D/g, '').slice(0, 2);
  const normalizedInteger = integerPart || (hasDecimalSeparator ? '0' : '');
  const displayInteger = normalizedInteger.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const formattedValue = `${isNegative ? '-' : ''}${displayInteger}${
    hasDecimalSeparator ? `,${fractionalPart}` : ''
  }`;
  const numericValue = normalizedInteger
    ? `${isNegative ? '-' : ''}${normalizedInteger}${
      hasDecimalSeparator ? `.${fractionalPart}` : ''
    }`
    : '';

  return {
    formattedValue,
    numericValue,
    hasDecimalSeparator,
    separatorIndex: hasDecimalSeparator ? input.lastIndexOf(separator) : -1,
  };
}
