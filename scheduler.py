import time
import schedule

from graph import graph
from logger import logger
from metrics import save_metrics


def run_job():
    try:
        logger.info("Scheduler triggered blog generation")

        initial_state = {
            "start_time": time.time()
        }

        result = graph.invoke(initial_state)

        logger.info(f"Generated Topic: {result.get('topic')}")
        logger.info(f"HTML length: {len(result.get('html', ''))}")

        logger.info("Blog generation completed successfully")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)

        save_metrics(status="failure")




# ⏰ Schedule job
schedule.every(6).hours.do(run_job)


# ▶️ Run once at startup
run_job()

logger.info("Scheduler started (runs every 6 hours)")


# 🔁 Main loop (robust)
while True:
    try:
        schedule.run_pending()
        time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Scheduler stopped manually")
        break

    except Exception as e:
        logger.error(f"Scheduler loop error: {str(e)}", exc_info=True)