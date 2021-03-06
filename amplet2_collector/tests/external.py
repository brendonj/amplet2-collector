from . import processor

class _External(processor.Processor):
    """Process AMP external test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            points.append({
                "measurement": "external",
                "tags": {
                    "test": "external",
                    "source": source,
                    "destination": datum.get("destination") or source,
                    "command": data["command"],
                },
                "time": timestamp,
                "fields": {
                    "value": datum["value"],
                    "count": 1,
                }
            })
        return points

process = _External().process
