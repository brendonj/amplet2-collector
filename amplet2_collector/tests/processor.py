class Processor(object):
    def __init__(self):
        pass

    def process(self, timestamp, source, data):
        pass

    def _get_family(self, address):
        if address is None:
            return None
        if "." in address:
            return "ipv4"
        if ":" in address:
            return "ipv6"
        return None
