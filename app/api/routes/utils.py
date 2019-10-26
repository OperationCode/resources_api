from prometheus_client import Counter, Summary

from app import utils as utils

failures_counter = Counter('my_failures', 'Number of exceptions raised')
latency_summary = Summary('request_latency_seconds', 'Length of request')
logger = utils.setup_logger('routes_logger')
