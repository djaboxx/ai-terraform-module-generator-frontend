import '@testing-library/jest-dom';

if (typeof globalThis.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = require('util');
  Object.assign(globalThis, { TextEncoder, TextDecoder });
}