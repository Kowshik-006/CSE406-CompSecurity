/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;

function readNlines(n) {

  /*
   * Implement this function to read n cache lines.
   * 1. Allocate a buffer of size n * LINESIZE.
   * 2. Read each cache line (read the buffer in steps of LINESIZE) 10 times.
   * 3. Collect total time taken in an array using `performance.now()`.
   * 4. Return the median of the time taken in milliseconds.
   */
  // Allocate a buffer of size n * LINESIZE
  const buffer = new ArrayBuffer(n * LINESIZE);
  // To access the buffer as a byte array
  const view = new Uint8Array(buffer);
  
  // Array to store time measurements
  const times = [];
  
  for (let iteration = 0; iteration < 10; iteration++) {
    const startTime = performance.now();
    
    for (let i = 0; i < n * LINESIZE; i += LINESIZE) {
      const value = view[i]; // Accessing the first byte of the cache line to ensure it's read
    }
    
    const endTime = performance.now();
    times.push(endTime - startTime);
  }
  
  // Calculate median time
  // Sorting in ascending order
  times.sort((a, b) => a - b);
  const median = times.length % 2 === 0
    ? (times[times.length / 2 - 1] + times[times.length / 2]) / 2
    : times[Math.floor(times.length / 2)];
    
  return median;
}

self.addEventListener("message", function (e) {
  if (e.data === "start") {
    const results = {};
    /* Call the readNlines function for n = 1, 10, ... 10,000,000 and store the result */
    // Test with n = 1, 10, 100, 1000, 10000, 100000, 1000000, 10000000
    const testSizes = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000];
    
    for (const n of testSizes) {
      // key = n , value = readNlines(n)
      results[n] = readNlines(n);  
    }

    self.postMessage(results);
  }
});
