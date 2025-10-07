import time
import requests

def html_request_with_retry(url, method="GET", max_attempts=3, delay=1.0, **kwargs):
    """
    Make an HTTP request with automatic retry on failure.

    Args:
        url (str): The URL to request
        method (str): HTTP method - either 'GET' or 'POST' (default: 'GET')
        max_attempts (int): How many times to try the request (default: 3)
        delay (float): Initial delay in seconds between retries (default: 1.0)
        **kwargs: Any additional arguments to pass to requests.get() or requests.post()

    Returns:
        requests.Response: The response object from successful request

    Raises:
        requests.RequestException: If all retry attempts fail

    """
    # Store the last exception we encounter so we can re-raise it if all attempts fail
    most_recent_exception = None

    # Try up to max_attempts times
    for attempt in range(max_attempts):
        try:
            # Make the actual HTTP request based on the method
            if method == "GET":
                # Pass url and any additional keyword arguments
                response = requests.get(url, **kwargs)
                response.raise_for_status()
                return response
            elif method == "POST":
                # Pass url and any additional keyword arguments
                response = requests.post(url, **kwargs)
                response.raise_for_status()
                return response

        except requests.RequestException as e:
            # Catch any requests-related exception (timeout, connection error, etc.)
            most_recent_exception = e

            # Check if we should retry (i.e., we haven't used all attempts yet)
            if attempt < max_attempts - 1:
                # Calculate wait time with exponential backoff
                # Attempt 0: delay * (2^0) = delay * 1 = original delay
                # Attempt 1: delay * (2^1) = delay * 2 = double the delay
                # Attempt 2: delay * (2^2) = delay * 4 = quadruple the delay
                wait_time = delay * (2**attempt)

                # Inform user we're retrying (helpful for debugging)
                print(f"Request failed, retrying in {wait_time}s...")

                # Wait before trying again
                time.sleep(wait_time)

                # Loop continues to next attempt

            # If we get here on the last attempt, we don't sleep or print
            # Just let the loop end

    # If we exit the loop, all attempts failed
    # Raise the last exception we caught so we know what went wrong
    raise most_recent_exception