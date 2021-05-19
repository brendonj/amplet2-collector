from . import processor

# XXX why not split out scheme, host, path into separate fields, makes
# matching destinations with other tests easier?
class _Http(processor.Processor):
    """Process AMP http test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        points.append({
            "measurement": "http",
            "tags": {
                "test": "http",
                "source": source,
                "destination": data["url"],
                "caching": data["caching"],
            },
            "time": timestamp,
            "fields": {
                "server_count": data["server_count"],
                "object_count": data["object_count"],
                "duration": data["duration"],
                "bytes": data["bytes"],
                "count": 1,
            }
        })
        return points

process = _Http().process
