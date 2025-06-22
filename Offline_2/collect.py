import time
import json
import os
import signal
import sys
import random
import traceback
import socket
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import database
from database import Database

WEBSITES = [
    # websites of your choice
    "https://cse.buet.ac.bd/moodle/",
    "https://google.com",
    "https://prothomalo.com",
]

TRACES_PER_SITE = 1000
FINGERPRINTING_URL = "http://localhost:5000" 
OUTPUT_PATH = "dataset.json"

# Initialize the database to save trace data reliably
database.db = Database(WEBSITES)

""" Signal handler to ensure data is saved before quitting. """
def signal_handler(sig, frame):
    print("\nReceived termination signal. Exiting gracefully...")
    try:
        database.db.export_to_json(OUTPUT_PATH)
    except:
        pass
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


"""
Some helper functions to make your life easier.
"""

def is_server_running(host='127.0.0.1', port=5000):
    """Check if the Flask server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

def setup_webdriver():
    """Set up the Selenium WebDriver with Edge options."""
    edge_options = Options()
    edge_options.add_argument("--window-size=1920,1080")
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver

def retrieve_traces_from_backend(driver):
    """Retrieve traces from the backend API."""
    traces = driver.execute_script("""
        return fetch('/api/get_results')
            .then(response => response.ok ? response.json() : {traces: []})
            .then(data => data.traces || [])
            .catch(() => []);
    """)
    
    count = len(traces) if traces else 0
    print(f"  - Retrieved {count} traces from backend API" if count else "  - No traces found in backend storage")
    return traces or []

def clear_trace_results(driver, wait):
    """Clear all results from the backend by pressing the button."""
    try:
        clear_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Clear All Results')]")
        ))
        clear_button.click()

        # Wait for the clear confirmation message
        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@role='alert']"), "Results cleared successfully!"
        ))
    except Exception as e:
        print(f"Error clearing results: {str(e)}")
        traceback.print_exc()

def is_collection_complete():
    """Check if target number of traces have been collected."""
    current_counts = database.db.get_traces_collected()
    remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
                      for website, count in current_counts.items()}
    return sum(remaining_counts.values()) == 0

"""
Your implementation starts here.
"""

def collect_single_trace(driver, wait, website_url):
    """ Implement the trace collection logic here. 
    1. Open the fingerprinting website
    2. Click the button to collect trace
    3. Open the target website in a new tab
    4. Interact with the target website (scroll, click, etc.)
    5. Return to the fingerprinting tab and close the target website tab
    6. Wait for the trace to be collected
    7. Return success or failure status
    """
    try:
        # Ensure we're on the fingerprinting website
        driver.get(FINGERPRINTING_URL)
        time.sleep(2)  # Wait for page to load completely
        
        # Click the Collect Trace Data button when clickable
        collect_trace_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Collect Trace Data')]")
        ))
        collect_trace_button.click()
        time.sleep(1)  # Wait for button click to register

        # Open the target website in a new tab
        driver.execute_script("window.open('')")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get(website_url)
        time.sleep(3)  # Wait for website to load

        # Scroll down and up with longer delays
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0)")
        time.sleep(2)

        # Close the target website tab and return to the fingerprinting tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Wait for the trace to be collected with a longer timeout
        wait = WebDriverWait(driver, 20)  # Increased timeout to 20 seconds
        wait.until(EC.text_to_be_present_in_element(
            (By.XPATH, "//div[@role='alert']"), "Heatmap generated successfully!"
        ))
        
        # Additional wait to ensure worker has finished
        time.sleep(2)
        
        return True
    
    except Exception as e:
        print(f"Error collecting trace for {website_url}: {str(e)}")
        traceback.print_exc()  # Print full stack trace for debugging
        # If we're on the wrong tab, try to get back to the main tab
        try:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except:
            pass
        return False

def collect_fingerprints(driver, target_counts=None):
    """ Implement the main logic to collect fingerprints.
    1. Calculate the number of traces remaining for each website
    2. Open the fingerprinting website
    3. Collect traces for each website until the target number is reached
    4. Save the traces to the database
    5. Return the total number of new traces collected
    """
    try:
        # 1. Calculate the number of traces remaining for each website
        current_counts = database.db.get_traces_collected()
        remaining_counts = {website: max(0, TRACES_PER_SITE - count) 
                          for website, count in current_counts.items()}
        
        # If target_counts is provided, use that instead
        if target_counts:
            remaining_counts = target_counts
            
        total_new_traces = 0
        wait = WebDriverWait(driver, 10)  # 10 second timeout for wait operations
        
        # 2. Open the fingerprinting website
        driver.get(FINGERPRINTING_URL)
        
        # 3. Collect traces for each website until the target number is reached
        for website in WEBSITES:
            site_idx = WEBSITES.index(website)
            remaining = remaining_counts.get(website, 0)
            print(f"\nCollecting traces for {website}")
            print(f"Remaining traces to collect: {remaining}")
            
            while remaining > 0:
                # Collect a single trace
                success = collect_single_trace(driver, wait, website)
                print(remaining)
                
                if success:
                    # Retrieve and save the trace
                    traces = retrieve_traces_from_backend(driver)
                    if traces:
                        # Save the latest trace to the database
                        database.db.save_trace(website, site_idx, traces[-1])
                        total_new_traces += 1
                        remaining -= 1
                        print(f"Successfully collected trace {TRACES_PER_SITE - remaining}/{TRACES_PER_SITE}")
                    else:
                        print("No trace data found in backend")
                else:
                    print("Failed to collect trace, retrying...")
                
                # Clear the results after each successful collection
                if success:
                    clear_trace_results(driver, wait)
                
                # Add a small delay between collections
                time.sleep(1)
        
        # 4. Save the traces to the database (this is done incrementally above)
        print(f"\nCollection complete. Total new traces collected: {total_new_traces}")
        
        # 5. Return the total number of new traces collected
        return total_new_traces
        
    except Exception as e:
        print(f"Error in collect_fingerprints: {str(e)}")
        traceback.print_exc()
        return 0

def main():
    """Implement the main function to start the collection process."""
    driver = None
    try:
        # 1. Check if the Flask server is running
        if not is_server_running():
            print("Error: Flask server is not running. Please start the server first.")
            return

        # 2. Initialize the database
        print("Initializing database...")
        database.db.init_database()  # Add this line to initialize the database
        print("Database initialized successfully.")

        # 3. Set up the WebDriver
        print("Setting up WebDriver...")
        driver = setup_webdriver()
        print("WebDriver setup complete.")

        # 4. Start the collection process
        while not is_collection_complete():
            print("\nStarting new collection cycle...")
            new_traces = collect_fingerprints(driver)
            
            if new_traces == 0:
                print("No new traces collected in this cycle. Retrying...")
                time.sleep(5)  # Wait before retrying
            else:
                print(f"Collected {new_traces} new traces in this cycle.")

        # 5. Handle any exceptions and ensure the WebDriver is closed at the end
        print("\nCollection process completed successfully!")

    except Exception as e:
        print(f"Error in main process: {str(e)}")
        traceback.print_exc()
    
    finally:
        # 6. Export the collected data to a JSON file
        try:
            print("\nExporting collected data to JSON...")
            database.db.export_to_json(OUTPUT_PATH)
            print(f"Data exported successfully to {OUTPUT_PATH}")
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
        
        # Clean up WebDriver
        if driver:
            try:
                driver.quit()
                print("WebDriver closed successfully.")
            except:
                print("Error closing WebDriver.")

if __name__ == "__main__":
    main()
