import logging
import time

import ampsave
from ampsave.exceptions import UnknownTestError
from google.protobuf.message import DecodeError
from influxdb import InfluxDBClient

# TODO move to another file
# TODO deal with queries that couldn't be sent vs queries with no responsee
#   - loss probably needs to be treated differently at a minimum
#   - family might not be set either
def get_family(address):
    if address is None:
        return None
    if "." in address:
        return "ipv4"
    if ":" in address:
        return "ipv6"
    return None

def get_hop_address(family, address):
    if address:
        return address
    if family == "ipv4":
        return "0.0.0.0"
    return "::"

def icmp(timestamp, source, data):
    points = []
    for datum in data:
        points.append({
            "measurement": "latency",
            "tags": {
                "test": "icmp",
                "source": source,
                "destination": datum["target"],
                "packet_size": datum["packet_size"],
                "random": datum["random"],
                "dscp": datum["dscp"],
                "family": get_family(datum.get("address", None)),
            },
            "time": timestamp,
            "fields": {
                "rtt": datum["rtt"],
                "loss": datum["loss"],
                # TODO record address family properly
                # TODO record address as well?
                #"family": datum["family"],
                #"family": "ipv4" if "." in datum["address"] else "ipv6",
                "error_type": datum["error_type"],
                "error_code": datum["error_code"],
            }
        })
    return points

def tcpping(timestamp, source, data):
    points = []
    for datum in data:
        points.append({
            "measurement": "latency",
            "tags": {
                "test": "tcpping",
                "source": source,
                "destination": datum["target"],
                "packet_size": datum["packet_size"],
                "random": datum["random"],
                "dscp": datum["dscp"],
                "port": datum["port"],
                "family": get_family(datum.get("address", None)),
            },
            "time": timestamp,
            "fields": {
                "rtt": datum["rtt"],
                "loss": datum["loss"],
                # TODO record address family properly
                #"family": datum["family"],
                #"family": "ipv4" if "." in datum["address"] else "ipv6",
                "icmptype": datum["icmptype"],
                "icmpcode": datum["icmpcode"],
            }
        })
    return points

def dns(timestamp, source, data):
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
                "family": get_family(datum.get("address", None)),
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

def http(timestamp, source, datum):
    points = []
    points.append({
        "measurement": "http",
        "tags": {
            "test": "http",
            "source": source,
            "destination": datum["url"],
            "caching": datum["caching"],
        },
        "time": timestamp,
        "fields": {
            "server_count": datum["server_count"],
            "object_count": datum["object_count"],
            "duration": datum["duration"],
            "bytes": datum["bytes"],
        }
    })
    return points

def traceroute(timestamp, source, data):
    points = []
    for datum in data:
        family = get_family(datum.get("address", None))
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
                    "address": get_hop_address(family,hop.get("address", None)),
                    "asn": hop.get("asn", None),
                }
            })
            hopid += 1
    return points

def throughput(timestamp, source, data):
    points = []
    for datum in data["results"]:
        points.append({
            "measurement": "throughput",
            "tags": {
                "test": "throughput",
                "source": source,
                "destination": data["target"],
                "write_size": data["write_size"],
                "dscp": data["dscp"],
                "protocol": data["protocol"],
                "direction": datum["direction"],
                "family": get_family(data.get("address", None)),
            },
            "time": timestamp,
            "fields": {
                # XXX duration vs runtime
                "duration": datum["duration"],
                "runtime": datum["runtime"],
                "bytes": datum["bytes"],
            }
        })
    return points

def udpstream(timestamp, source, data):
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
                "family": get_family(data.get("address", None)),
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

def external(timestamp, source, data):
    points = []
    for datum in data["results"]:
        points.append({
            "measurement": "external",
            "tags": {
                "test": "external",
                "source": source,
                "command": data["command"],
            },
            "time": timestamp,
            "fields": {
                "value": datum["value"]
            }
        })
    return points

def fastping(timestamp, source, data):
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
                "family": get_family(data.get("address", None)),
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

def sip(timestamp, source, data):
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
                "family": get_family(data.get("address", None)),
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

def youtube(timestamp, source, data):
    points = []
    points.append({
        "measurement": "video",
        "tags": {
            "test": "youtube",
            "source": source,
            "destination": data["video"],
            "requested_quality": data["requested_quality"],
        },
        "time": timestamp,
        "fields": {
            "actual_quality": data["actual_quality"],
            "pre_time": data["pre_time"],
            "initial_buffering": data["initial_buffering"],
            "playing_time": data["playing_time"],
            "stall_time": data["stall_time"],
            "stall_count": data["stall_count"],
        }
    })
    return points

class Processor(object):
    def __init__(self, dbhost="localhost", dbport=8086, dbuser=None,
            dbpass=None, dbname="amp"):
        self._logger = logging.getLogger(__name__)
        self._dbhost = dbhost
        self._dbport = dbport
        self._dbuser = dbuser
        self._dbpass = dbpass
        self._dbname = dbname
        self._db = None
        self._maximum_backoff = 64
        self._connect()

    def __del__(self):
        if self._db:
            self._db.close()

    # XXX this doesn't actually connect until a request is made?
    # XXX do some testing once I have requests to send
    def _connect(self):
        delay = 1
        while self._db is None:
            try:
                self._logger.debug("Connecting to influxdb %s:%d",
                            self._dbhost, self._dbport)
                self._db = InfluxDBClient(self._dbhost, self._dbport,
                        self._dbuser, self._dbpass, self._dbname)
            except ConnectionError as err:
                # XXX which exceptions?
                self._logger.warning("Failed to connect to influxdb %s:%d: %s",
                            self._dbhost, self._dbport, err)
                self._db = None
                time.sleep(delay)
                if delay < self._maximum_backoff:
                    delay = delay * 2
        self._logger.debug("Connected to influxdb %s:%d",
                    self._dbhost, self._dbport)

    def _write(self, points):
        if not points:
            return

        # XXX does this actually throw an exception? or will just return false?
        while True:
            try:
                if self._db.write_points(points, time_precision="s"):
                    break
                self._logger.warning("Failed to write to influxdb")
                self._db = None
                self._connect()
            except ConnectionError as err:
                # XXX which exceptions?
                self._logger.warning("Lost connection to influxdb %s:%d: %s",
                            self._dbhost, self._dbport, err)
                self._db = None
                self._connect()

    def process_data(self, channel, method, properties, body):
        # ignore any messages that don't have user_id set
        if not hasattr(properties, "user_id"):
            return

        # ignore any messages that don't have timestamp set
        if not hasattr(properties, "timestamp"):
            return

        # ignore any messages that don't have a test type
        if "x-amp-test-type" not in properties.headers:
            return

        # get the test type being reported
        test = properties.headers["x-amp-test-type"]

        try:
            # Extract the test specific results from the message. This may
            # include multiple results if the test has multiple targets.
            data = ampsave.get_data(test, body)
        except UnknownTestError:
            # ignore any messages for tests we don't have a module for
            self._logger.warning("Unknown test: '%s'", test)
            data = None
        except DecodeError as err:
            # Protocol buffer decoding failed for some reason
            self._logger.warning("Failed to decode %s result from %s: %s",
                        test, properties.user_id, err)
            data = None

        # write any data to influxdb, for now one message at a time
        if data:
            print(properties.timestamp, properties.user_id, test)
            #print(data)
            if test == "icmp":
                processed = icmp(properties.timestamp, properties.user_id, data)
            elif test == "tcpping":
                processed = tcpping(properties.timestamp, properties.user_id, data)
            elif test == "dns":
                processed = dns(properties.timestamp, properties.user_id, data)
            elif test == "http":
                processed = http(properties.timestamp, properties.user_id, data)
            elif test == "traceroute":
                processed = traceroute(properties.timestamp, properties.user_id, data)
            elif test == "throughput":
                processed = throughput(properties.timestamp, properties.user_id, data)
            elif test == "udpstream":
                processed = udpstream(properties.timestamp, properties.user_id, data)
            elif test == "external":
                processed = external(properties.timestamp, properties.user_id, data)
            elif test == "fastping":
                processed = fastping(properties.timestamp, properties.user_id, data)
            elif test == "sip":
                processed = sip(properties.timestamp, properties.user_id, data)
            elif test == "youtube":
                processed = youtube(properties.timestamp, properties.user_id, data)
            else:
                processed = []
            #XXX test specific modules to massage the data?
            #XXX merge all latency tests into one table with a tag for test type
            #self._write(properties.timestamp, properties.user_id, test, data)
            self._write(processed)

        # acknowledge message
        channel.basic_ack(method.delivery_tag)
