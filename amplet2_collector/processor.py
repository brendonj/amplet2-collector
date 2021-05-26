import logging
import time

import ampsave
from ampsave.exceptions import UnknownTestError
from google.protobuf.message import DecodeError
from influxdb import InfluxDBClient

from . import tests

# TODO deal with queries that couldn't be sent vs queries with no responsee
#   - loss probably needs to be treated differently at a minimum
#   - family might not be set either

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
        self._batch_size = 100
        self._pending = []
        self._count = 0
        self._connect()

    def __del__(self):
        if self._db:
            try:
                self._db.close()
            except AttributeError:
                pass

    def _connect(self):
        delay = 1
        while self._db is None:
            try:
                self._logger.debug("Connecting to influxdb %s:%d",
                                   self._dbhost, self._dbport)
                self._db = InfluxDBClient(self._dbhost, self._dbport,
                        self._dbuser, self._dbpass, self._dbname)
            except ConnectionError as err:
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

        while True:
            try:
                # XXX try using line protocol (is json default?)
                if self._db.write_points(points, batch_size=10000,
                                         time_precision="s"):
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
            self._logger.warning("Can't decode unknown test: '%s'", test)
            data = None
        except DecodeError as err:
            # protocol buffer decoding failed for some reason
            self._logger.warning("Failed to decode %s result from %s: %s",
                        test, properties.user_id, err)
            data = None

        # if the incoming messages are really bad then I guess this could
        # affect how often results get written, but why is the data that bad?
        if data is None:
            return

        try:
            # process the message using test specific code into a list of
            # datapoints appropriate to insert into influxdb
            self._pending += getattr(tests, test).process(
                    properties.timestamp, properties.user_id, data)
        except AttributeError:
            self._logger.warning("Can't process unknown test: '%s'", test)

        # count messages rather than using the number of pending results
        # (some tests can report one result, others hundreds and this gives
        # a bit more consistency to the processing delay)
        self._count += 1

        if self._count < self._batch_size:
            return

        # write all pending data to influxdb and reset the accumulator
        self._write(self._pending)
        self._pending = []
        self._count = 0

        # don't ack anything until we write the whole block of pending results,
        # as sending individual acks can be slow
        channel.basic_ack(method.delivery_tag, True)
