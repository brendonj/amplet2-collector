from . import processor

class _Fastping(processor.Processor):
    """Process AMP fastping test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            points.append({
                # XXX this has a different set of fields to latency, but is very
                # similar to udpstream... put them in the same table?
                "measurement": "fastping",
                "tags": {
                    "test": "fastping",
                    "source": source,
                    "destination": data["destination"],
                    "packet_rate": data["packet_rate"],
                    "packet_size": data["packet_size"],
                    "packet_count": data["packet_count"],
                    "dscp": data["dscp"],
                    "family": self._get_family(data.get("address", None)),
                },
                "time": timestamp,
                "fields": {
                    "response_time": datum["time_till_first_response"],
                    "connect_time": datum["time_till_connected"],
                    "duration": datum["runtime"],
                    "rtt": datum["rtt"]["mean"],
                    "jitter": datum["jitter"]["mean"],
                }
            })
        return points

process = _Fastping().process
