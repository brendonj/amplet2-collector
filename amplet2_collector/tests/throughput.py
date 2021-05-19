from . import processor

class _Throughput(processor.Processor):
    """Process AMP throughput test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            points.append({
                "measurement": "throughput",
                "tags": {
                    "test": "throughput",
                    "source": source,
                    "destination": data["target"],
                    "write_size": data["write_size"],
                    "dscp": data["dscp"],
                    "protocol": data["protocol"],
                    "direction": datum["direction"],
                    "family": self._get_family(data.get("address", None)),
                },
                "time": timestamp,
                "fields": {
                    # XXX duration vs runtime
                    "duration": datum["duration"],
                    "runtime": datum["runtime"],
                    "bytes": datum["bytes"],
                    "count": 1 if self._is_valid(datum["bytes"]) else 0,
                }
            })
        return points

process = _Throughput().process
