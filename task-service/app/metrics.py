from prometheus_client import Counter

tasks_created_total = Counter(
    "tasks_created_total",
    "Total number of tasks created"
)

cache_hits_total = Counter(
    "cache_hits_total",
    "Total number of cache hits"
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total number of cache misses"
)
