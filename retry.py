from logger import logger
import time


def retry(func, retries=3, delay=2, name="operation", validate=None):
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            result = func()

            if validate:
                validate(result)

            return result

        except Exception as e:
            last_error = str(e)

            logger.warning(
                f"{name} failed (attempt {attempt}/{retries}) | Error: {last_error}"
            )

            if attempt == retries:
                logger.error(
                    f"{name} failed after {retries} attempts",
                    exc_info=True
                )
                raise

            time.sleep(delay)