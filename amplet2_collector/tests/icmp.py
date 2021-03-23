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
                    # TODO record address family properly
                    # TODO record address as well?
                    #"family": datum["family"],
                    #"family": "ipv4" if "." in datum["address"] else "ipv6",
                    "error_type": datum["error_type"],
                    "error_code": datum["error_code"],
                }
            })
        return points

process = _Icmp().process
