import time

def safe_generate(func, retries=3, delay=2):
    for attempt in range(retries):
        try:
            return func()
        except Exception as e:
            print(f"Retry {attempt+1}/{retries} failed:", str(e))
            time.sleep(delay)

    raise Exception("All retries failed")