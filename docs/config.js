// Raw traces are kept outside the Pages build and fetched only on selection.
// The immutable dataset-v1 tag identifies the exact published collection.
export const traceBase = location.hostname === '127.0.0.1' || location.hostname === 'localhost'
  ? '../data/traces/'
  : 'https://raw.githubusercontent.com/IvanPanzera/fnmr-qwen3.8-flash-next/dataset-v1/data/traces/';

