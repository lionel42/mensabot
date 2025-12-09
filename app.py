import schedule
import time
import subprocess
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def job():
    logger.info("Running daily job...")
    subprocess.run(["python", "-m", "mensabot"])

# Schedule for Monday to Friday at 14:00
for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
    getattr(schedule.every(), day).at("14:00").do(job)


logger.info("Scheduler started. Waiting for weekday jobs...")


while True:
    schedule.run_pending()
    logger.debug("Checked for pending jobs. Sleeping...")
    time.sleep(30)  # check every 30 seconds
