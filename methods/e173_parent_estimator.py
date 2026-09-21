"""E173 official-mini parent entrypoint.

The local subclass is required by WhestBench 0.16.1 loader discovery.
"""

from methods.e173_starter_ago import ParentEstimator


class Estimator(ParentEstimator):
    pass
