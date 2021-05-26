from . import processor

class _Fastping(processor.Processor):
    """Process AMP fastping test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            samples = self._get_nested_value(datum, "rtt", "samples")
            if samples is None:
                loss_percent = None
            else:
                loss_percent = 100.0 * (1 - (samples / data["packet_count"]))
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
                    "rtt": self._get_nested_value(datum, "rtt", "mean"),
                    "jitter": self._get_nested_value(datum, "jitter", "mean"),
                    "loss_percent": loss_percent,
                    "count": 1 if datum["rtt"] is not None else 0,
                }
            })
        return points

process = _Fastping().process
