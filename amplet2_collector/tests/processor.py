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

    def _is_valid(self, field):
        if field is not None and field > 0:
            return True
        return False

    def _get_nested_value(self, d, *args):
        for key in args:
            try:
                d = d[key]
            except (KeyError, TypeError):
                return None
        return d
