from pytrends.request import TrendReq
import logging

logger = logging.getLogger(__name__)

# 🔹 Initialize Google Trends
pytrends = TrendReq(hl='en-IN', tz=330)


# 🔹 REAL TREND SIGNAL
def get_trend_signal_real():
    keywords = [
        "budget travel india",
        "visa free countries for indians",
        "cheap international trips from india",
        "digital nomad visa",
        "monsoon travel india"
    ]

    try:
        pytrends.build_payload(keywords, timeframe='today 3-m')
        data = pytrends.interest_over_time()

        if data.empty:
            logger.warning("[Signals] Trends empty → using fallback")
            return keywords

        trending = sorted(
            keywords,
            key=lambda k: data[k].iloc[-1] if k in data else 0,
            reverse=True
        )

        logger.info(f"[Signals] Trends: {trending[:5]}")
        return trending[:5]

    except Exception as e:
        logger.error(f"[Signals] Trends error: {str(e)}")
        return keywords


# 🔹 PAIN POINT SIGNAL (SAFE STATIC VERSION)
def get_pain_points_real():
    pain_points = [
        "hidden travel costs",
        "tourist scams",
        "transport confusion in new cities",
        "overcrowded tourist places",
        "budget planning mistakes",
        "visa issues for indians",
        "language barriers while traveling"
    ]

    logger.info(f"[Signals] Pain Points: {pain_points}")
    return pain_points


# 🔹 NORMALIZATION (VERY IMPORTANT)
def normalize_signals(signals):
    normalized = list(set([s.strip().lower() for s in signals if s]))
    logger.info(f"[Signals] Normalized: {normalized}")
    return normalized