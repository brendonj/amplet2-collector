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
                    "rtt": datum["rtt"]["mean"],
                    "jitter": datum["jitter"]["mean"],
                    "loss": datum["loss_percent"],
                    "mos": datum["voip"]["itu_mos"],
                }
            })
        return points

process = _Udpstream().process
