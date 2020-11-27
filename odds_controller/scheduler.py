from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc


EXECUTORS = {
    'default': ThreadPoolExecutor(5)  # ideal for debugging purposes
    #  TODO switch to ProcessPoolExecutor (blockers):
    #       - resolve exception (KeyboardInterrupt, SystemExit) handling in each fork process
}
JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 1
}


class OddsScheduler(BackgroundScheduler):
    def __init__(self):
        super().__init__(executors=EXECUTORS, job_defaults=JOB_DEFAULTS, timezone=utc)
