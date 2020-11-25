from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc


executors = {
    'default': ThreadPoolExecutor(5),
}
job_defaults = {
    'coalesce': False,
    'max_instances': 1
}
odds_scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults, timezone=utc)
