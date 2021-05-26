from . import processor

class _Udpstream(processor.Processor):
    """Process AMP udpstream test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            points.append({
                "measurement": "udpstream",
                "tags": {
                    "test": "udpstream",
                    "source": source,
                    "destination": data["target"],
                    "packet_size": data["packet_size"],
                    "packet_spacing": data["packet_spacing"],
                    "packet_count": data["packet_count"],
                    "dscp": data["dscp"],
                    "direction": datum["direction"],
                    "family": self._get_family(data.get("address", None)),
                },
                "time": timestamp,
                "fields": {
                    "rtt": self._get_nested_value(datum, "rtt", "mean"),
                    "jitter": self._get_nested_value(datum, "jitter", "mean"),
                    "loss": datum["loss_percent"],
                    "mos": self._get_nested_value(datum, "voip", "itu_mos"),
                    "count": 1 if datum["rtt"] is not None else 0,
                }
            })
        return points

process = _Udpstream().process
