from . import processor

class _Traceroute(processor.Processor):
    """Process AMP traceroute test data for storing in influxdb."""
    def _get_hop_address(self, family, address):
        if address:
            return address
        if family == "ipv4":
            return "0.0.0.0"
        return "::"

    def process(self, timestamp, source, data):
        points = []
        for datum in data:
            family = self._get_family(datum.get("address", None))
            tags = {
                "test": "traceroute",
                "source": source,
                "destination": datum["target"],
                "packet_size": datum["packet_size"],
                "random": datum["random"],
                "dscp": datum["dscp"],
                "family": family,
            }

            points.append({
                "measurement": "pathlen",
                "tags": tags.copy(),
                "time": timestamp,
                "fields": {
                    "length": datum["length"],
                }
            })

            hopid = 1
            for hop in datum["hops"]:
                hoptags = tags.copy()
                hoptags["hop"] = "%02d" % hopid

                points.append({
                    "measurement": "traceroute",
                    "tags": hoptags,
                    "time": timestamp,
                    "fields": {
                        "rtt": hop.get("rtt", None),
                        "address": self._get_hop_address(family,
                                hop.get("address", None)),
                        "asn": hop.get("asn", None),
                    }
                })
                hopid += 1
        return points

process = _Traceroute().process
