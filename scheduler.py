import time
import schedule

from graph import graph
from logger import logger
from metrics import save_metrics


def run_job():
    try:
        logger.info("Blog generation triggered")

        initial_state = {
            "start_time": time.time()
        }

        result = graph.invoke(initial_state)
        
        if not result.get("html"):
            raise Exception("HTML missing")

        logger.info(f"Generated Topic: {result.get('topic')}")
        logger.info(f"HTML length: {len(result.get('html', ''))}")
        logger.info("Blog generation completed successfully")

        return True

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        save_metrics(status="failure")




if __name__ == "__main__":
    run_job()