from . import processor

class _Dns(processor.Processor):
    """Process AMP dns test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            if datum["query_len"] is not None and datum["query_len"] > 0:
            #if datum.get("query_len", 0) > 0:
                #response = datum.get("response_size")
                #if response != None and response > 0:
                requests = 1
                if datum["response_size"] is not None and datum["response_size"] > 0:
                    loss = 0
                else:
                    loss = 1
            else:
                requests = 0
                loss = None
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
                    "loss": loss,
                    "requests": requests,
                    # TODO record address family properly
                    #"family": datum["family"],
                    #"family": "ipv4" if "." in datum["address"] else "ipv6",
                }
            })
        return points

process = _Dns().process
