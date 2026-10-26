import sys
import logging
import uvicorn

logging.basicConfig(
    filename="backend_run.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

if __name__ == "__main__":
    try:
        logging.info("Starting uvicorn server on 127.0.0.1:8001...")
        uvicorn.run("apps.api.src.main:app", host="127.0.0.1", port=8001, log_level="info")
    except Exception as e:
        logging.exception("Uvicorn crashed with exception: %s", e)
        raise
