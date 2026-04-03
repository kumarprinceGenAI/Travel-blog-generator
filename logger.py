import logging
import sys

# 🔥 Force UTF-8 for stdout (fix ₹ issue)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# 🔹 Basic config (clean)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

# 🔹 Global logger
logger = logging.getLogger("app")