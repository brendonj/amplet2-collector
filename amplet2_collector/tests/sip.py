from . import processor

class _Sip(processor.Processor):
    """Process AMP sip test data for storing in influxdb."""
    def _get_loss_percent(self, datum):
        if datum is None:
            return None

        lost = datum.get("lost")
        packets = datum.get("packets")

        if self._is_valid(lost) and self._is_valid(packets):
            return 100.0 * lost / (lost + packets)

        return None


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
                    "rtt": self._get_nested_value(datum, "rtt", "mean"),
                    "tx_mos": self._get_nested_value(datum, "tx", "itu_mos"),
                    "tx_jitter": self._get_nested_value(datum, "tx", "jitter", "mean"),
                    "tx_loss_percent": self._get_loss_percent(datum.get("tx")),
                    "rx_mos": self._get_nested_value(datum, "rx", "itu_mos"),
                    "rx_jitter": self._get_nested_value(datum, "rx", "jitter", "mean"),
                    "rx_loss_percent": self._get_loss_percent(datum.get("rx")),
                    "count": 1 if self._is_valid(datum["time_till_first_response"]) else 0,
                }
            })
        return points

process = _Sip().process
