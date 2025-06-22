function app() {
  return {
    /* This is the main app object containing all the application state and methods. */
    // The following properties are used to store the state of the application

    // results of cache latency measurements
    latencyResults: null,
    // local collection of trace data
    traceData: [],
    // Local collection of heapmap images
    heatmaps: [],

    // Current status message
    status: "",
    // Is any worker running?
    isCollecting: false,
    // Is the status message an error?
    statusIsError: false,
    // Show trace data in the UI?
    showingTraces: false,

    // Collect latency data using warmup.js worker
    async collectLatencyData() {
      this.isCollecting = true;
      this.status = "Collecting latency data...";
      this.latencyResults = null;
      this.statusIsError = false;
      this.showingTraces = false;

      try {
        // Create a worker
        let worker = new Worker("warmup.js");

        // Start the measurement and wait for result
        const results = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data);
          worker.postMessage("start");
        });

        // Update results
        this.latencyResults = results;
        this.status = "Latency data collection complete!";

        // Terminate worker
        worker.terminate();
      } catch (error) {
        console.error("Error collecting latency data:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.isCollecting = false;
      }
    },

    // Collect trace data using worker.js and send to backend
    async collectTraceData() {
       /* 
        * Implement this function to collect trace data.
        * 1. Create a worker to run the sweep function.
        * 2. Collect the trace data from the worker.
        * 3. Send the trace data to the backend for temporary storage and heatmap generation.
        * 4. Fetch the heatmap from the backend and add it to the local collection.
        * 5. Handle errors and update the status.
        */
      this.isCollecting = true;
      this.status = "Collecting trace data...";
      this.traceData = [];
      this.statusIsError = false;
      this.showingTraces = false;
      try {
        // Create a worker
        let worker = new Worker("worker.js");

        // Start the measurement and wait for result
        const results = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data);
          worker.postMessage("start");
        });

        // Update results
        this.traceData = results;
        this.status = "Trace data collection complete!";

        // Terminate worker
        worker.terminate();

        // Send trace data to backend
        const response = await fetch('/collect_trace', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(results)
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Add the new heatmap to the collection
        this.heatmaps.push({
          image: data.heatmap,
          statistics: data.statistics,
          timestamp: new Date().toISOString(),
          prediction: data.prediction
        });

        // Show the traces
        this.showingTraces = true;
        this.status = "Heatmap generated successfully!";

      } catch (error) {
        console.error("Error collecting trace data:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.isCollecting = false;
      }
    },

    // Download the trace data as JSON (array of arrays format for ML)
    async downloadTraces() {
      /* 
        * Implement this function to download the trace data.
        * 1. Fetch the latest data from the backend API.
        * 2. Create a download file with the trace data in JSON format.
        * 3. Handle errors and update the status.
        */
      try {
        // Fetch the latest trace data from the backend
        const response = await fetch('/api/get_results');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const traceData = await response.json();
        
        // Create a blob with the trace data
        const blob = new Blob([JSON.stringify(traceData, null, 2)], { type: 'application/json' });
        
        // Create a download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trace_data_${new Date().toISOString()}.json`;
        
        // Trigger the download
        document.body.appendChild(a);
        a.click();
        
        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        this.status = "Trace data downloaded successfully!";
      } catch (error) {
        console.error("Error downloading trace data:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      }
    },

    // Clear all results from the server
    async clearResults() {
      /* 
       * Implement this function to clear all results from the server.
       * 1. Send a request to the backend API to clear all results.
       * 2. Clear local copies of trace data and heatmaps.
       * 3. Handle errors and update the status.
       */

      try {
        const response = await fetch('/api/clear_results', {
          method: 'POST',
        });
        this.showingTraces = false;
        this.traceData = [];
        this.heatmaps = [];
        this.status = "Results cleared successfully!";
      } catch (error) {
        console.error("Error clearing results:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      }
    },
  };
}
