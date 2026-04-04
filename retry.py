from logger import logger
import time


def retry(func, attempts=3, delay=2, name="task", validate=None):
    import time

    for i in range(attempts):
        try:
            result = func()

            if validate:
                validate(result)

            return result

        except Exception as e:
            print(f"[Retry:{name}] Attempt {i+1} failed → {e}")
            time.sleep(delay)

    print(f"[Retry:{name}] All attempts failed → returning fallback")

    return {}  # 🔥 ALWAYS dict (safe for your pipeline)