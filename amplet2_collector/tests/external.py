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
                    "command": data["command"],
                },
                "time": timestamp,
                "fields": {
                    "value": datum["value"]
                }
            })
        return points

process = _External().process
