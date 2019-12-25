from prometheus_client import Summary, Counter

latency_summary = Summary('request_latency_seconds', 'Length of request')
failures_counter = Counter('my_failures', 'Number of exceptions raised')
