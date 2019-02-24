from datetime import datetime, timedelta
import os.path
from typing import List, Any

from .common import History, Entry, Visit, Filter

TIME_FORMAT = "%d %b %Y %H:%M"

# TODO hmm, only use implicit datetime for rendering? And use set of tags that allow implicit?
def render(history: History, fallback_timezone = None):
    def fallback(v: Visit):
        dt = v.dt
        if dt.tzinfo is not None:
            return v
        else:
            return v._replace(dt=dt.replace(tzinfo=fallback_timezone))

    # sort visits by datetime, sort all items by URL
    entries = [
        entry._replace(visits=sorted([fallback(v) for v in entry.visits])) for _, entry in sorted(history.items())
    ]
    # # TODO filter by length?? or by query length (after ?)

    RVisits = List[Any]
    RContext = List[str]
    # TODO ugh. any?

    def format_entry(e: Entry):
        visits = e.visits

        delta = timedelta(minutes=20)
        groups: List[List[Visit]] = []
        group: List[Visit] = []
        def dump_group():
            nonlocal group
            if len(group) > 0:
                groups.append(group)
                group = []
        for v in visits:
            last = v if len(group) == 0 else group[-1]
            if v.dt - last.dt > delta:
                dump_group()
            group.append(v)
        dump_group()

        contexts = [v.context for v in visits if v.context is not None]

        res = []
        for group in groups:
            tags = list(sorted({e.tag for e in group if e.tag is not None}))

            start_time_s = group[0].dt.strftime(TIME_FORMAT)
            end_time_s = group[-1].dt.strftime(TIME_FORMAT)
            if start_time_s == end_time_s:
                res.append([start_time_s, tags])
            else:
                res.append(["{}--{}".format(start_time_s, group[-1].dt.strftime("%H:%M")), tags])
        # we presumably want descending date!
        return [list(reversed(res)), contexts]


    json_dict = {
        e.url: format_entry(e)
        for e in entries
    }
    return json_dict
