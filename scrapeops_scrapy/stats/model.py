
class BaseStatsModel(object):

    def __init__(self):
        pass

    def get_value(self, stats, key, default=None):
        return stats.get(key, default)

    def set_value(self, stats, key, value):
        stats[key] = value

    def set_stats(self, stats, new_stats):
        stats = new_stats

    def inc_value(self, stats, key, count=1, start=0, spider=None):
        d = stats
        d[key] = d.setdefault(key, start) + count

    def max_value(self, stats, key, value, spider=None):
        stats[key] = max(stats.setdefault(key, value), value)


    def min_value(self, stats, key, value, spider=None):
        stats[key] = min(stats.setdefault(key, value), value)
    


class PeriodicStatsModel(BaseStatsModel):

    """
        STATS_ATTRIBUTES:
        --> job_name
        --> number_requests
        --> breakdown of response codes
        --> number of items
        --> average concurrency
        --> proxy_performance (success_rate, success_latency)
        --> job_start_time
        --> job_finish_time
        --> job_completion_time
        --> finish_reason
    """
    
    def __init__(self):
        self._periodic_stats = {}
        self._periodic_errors = 0
        self._periodic_warnings = 0
        self._periodic_criticals = 0

    def get_periodic_stats(self):
        return self._periodic_stats

    def reset_periodic_stats(self):
        self._periodic_stats = {}

    def display_periodic_stats(self):
        stats = self.get_periodic_stats()
        print('#### SCRAPEOPS PERIODIC STATS ####')
        print('{')
        for key, value in stats.items():
            if key[0] != '_':
                print(f"    '{key}': {value},")
        print('}')



class OverallStatsModel(BaseStatsModel):
    
    def __init__(self):
        self._overall_stats = {}
        self._overall_errors = 0
        self._overall_warnings = 0
        self._overall_criticals = 0

    def get_overall_stats(self):
        return self._overall_stats

    def display_overall_stats(self):
        stats = self.get_overall_stats()
        print('#### SCRAPEOPS OVERALL STATS ####')
        print('{')
        for key, value in stats.items():
            if key[0] != '_':
                print(f"    '{key}': {value},")
        print('}')

