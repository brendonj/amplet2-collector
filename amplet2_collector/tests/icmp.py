from . import processor

class _Icmp(processor.Processor):
    """Process AMP icmp test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data:
            points.append({
                "measurement": "latency",
                "tags": {
                    "test": "icmp",
                    "source": source,
                    "destination": datum["target"],
                    "packet_size": datum["packet_size"],
                    "random": datum["random"],
                    "dscp": datum["dscp"],
                    "family": self._get_family(datum.get("address", None)),
                },
                "time": timestamp,
                "fields": {
                    "rtt": datum["rtt"],
                    "loss": datum["loss"],
                    # TODO record address as well?
                    "error_type": datum["error_type"],
                    "error_code": datum["error_code"],
                    "count": 1 if self._is_valid(datum["rtt"]) else 0,
                }
            })
        return points

process = _Icmp().process
