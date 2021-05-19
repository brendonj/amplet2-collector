from . import processor

class _Dns(processor.Processor):
    """Process AMP dns test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            points.append({
                "measurement": "latency",
                "tags": {
                    "test": "dns",
                    "source": source,
                    "destination": datum["destination"],
                    "dscp": data["dscp"],
                    "query": data["query"],
                    "family": self._get_family(datum.get("address", None)),
                },
                "time": timestamp,
                "fields": {
                    "rtt": datum["rtt"],
                    "loss": None if not self._is_valid(datum["query_len"]) else 0 if self._is_valid(datum["response_size"]) else 1,
                    "count": 1 if self._is_valid(datum["rtt"]) else 0,
                    # TODO record address family properly
                    #"family": datum["family"],
                    #"family": "ipv4" if "." in datum["address"] else "ipv6",
                }
            })
        return points

process = _Dns().process
