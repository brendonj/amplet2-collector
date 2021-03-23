from . import processor

class _Sip(processor.Processor):
    """Process AMP sip test data for storing in influxdb."""
    def process(self, timestamp, source, data):
        points = []
        for datum in data["results"]:
            points.append({
                "measurement": "sip",
                "tags": {
                    "test": "sip",
                    "source": source,
                    "destination": data["hostname"],
                    "uri": data["uri"],
                    "dscp": data["dscp"],
                    "family": self._get_family(data.get("address", None)),
                },
                "time": timestamp,
                "fields": {
                    "response_time": datum["time_till_first_response"],
                    "connect_time": datum["time_till_connected"],
                    "duration": datum["duration"],
                    "rtt": datum["rtt"]["mean"],
                    "tx_mos": datum["tx"]["itu_mos"],
                    "tx_jitter": datum["tx"]["jitter"]["mean"],
                    "tx_loss_percent": 100.0 * datum["tx"]["lost"] / (datum["tx"]["packets"] + datum["tx"]["lost"]),
                    "rx_mos": datum["rx"]["itu_mos"],
                    "rx_jitter": datum["rx"]["jitter"]["mean"],
                    "rx_loss_percent": 100.0 * datum["rx"]["lost"] / (datum["rx"]["packets"] + datum["rx"]["lost"])
                }
            })
        return points

process = _Sip().process
