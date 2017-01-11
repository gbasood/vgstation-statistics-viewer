from __future__ import unicode_literals

class QUERY_TIMESPAN:   # May need to move this to its own file for later use in other queries.
    ALL = 0
    QUARTERLY = 1
    MONTHLY = 2
    WEEKLY = 3
    DAILY = 4

def format_query_timespan(timespan):
    """Can't trust user input in this case, so we'll format it"""
    timespan = unicode(timespan).strip()
    print timespan, type(timespan.lower()), type(timespan), type("monthly")
    if "quarterly" in timespan.lower():
        return QUERY_TIMESPAN.QUARTERLY
	if "monthly" in timespan.lower():
        print "honk"
		return QUERY_TIMESPAN.MONTHLY
	if "weekly" in timespan.lower():
		return QUERY_TIMESPAN.WEEKLY
	if "daily" in timespan.lower():
		return QUERY_TIMESPAN.DAILY
