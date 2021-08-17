import copy


class StatsAggregator(object):

    def __init__(self):
        pass
    
    @staticmethod
    def aggregate_stats(crawler, periodic_stats, overall_stats):
        StatsAggregator.avg_latency(periodic_stats, overall_stats)
        StatsAggregator.log_levels(crawler)

    @staticmethod
    def avg_latency(periodic_stats, overall_stats):
        for stat_type in [periodic_stats, overall_stats]:
            stats_copy = copy.deepcopy(stat_type)
            for key, value in stats_copy.items():
                if 'responses' in key and 'total_latency' in key:
                    count_key = key.replace('total_latency', 'count')
                    avg_latency = value / stats_copy.get(count_key)
                    self.set_value(stat_type, key.replace('total_latency', 'avg_latency'), avg_latency)

    @staticmethod
    def log_levels(crawler):
        scrapy_stats = crawler.stats.get_stats()
        for log_level in ['WARNING', 'ERROR', 'CRITICAL']:
            log_key = 'log_count/' + log_level
            log_value = scrapy_stats.get(log_key, 0)
            previous_value = self._overall_stats.get(log_key, 0)
            self.set_value(self._periodic_stats, log_key, log_value - previous_value)
            self.set_value(self._overall_stats, log_key, log_value)


