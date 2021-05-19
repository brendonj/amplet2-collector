from . import processor

class _Tcpping(processor.Processor):
    """Process AMP tcpping test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data:
            points.append({
                "measurement": "latency",
                "tags": {
                    "test": "tcpping",
                    "source": source,
                    "destination": datum["target"],
                    "packet_size": datum["packet_size"],
                    "random": datum["random"],
                    "dscp": datum["dscp"],
                    "port": datum["port"],
                    "family": self._get_family(datum.get("address", None)),
                },
                "time": timestamp,
                "fields": {
                    "rtt": datum["rtt"],
                    "loss": datum["loss"],
                    # TODO record address family properly
                    #"family": datum["family"],
                    #"family": "ipv4" if "." in datum["address"] else "ipv6",
                    "icmptype": datum["icmptype"],
                    "icmpcode": datum["icmpcode"],
                    "count": 1 if self._is_valid(datum["rtt"]) else 0,
                }
            })
        return points

process = _Tcpping().process
