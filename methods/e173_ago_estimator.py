"""E173 official-mini AGO entrypoint.

The local subclass is required by WhestBench 0.16.1 loader discovery.
"""

from methods.e173_starter_ago import AGOEstimator


class Estimator(AGOEstimator):
    pass
