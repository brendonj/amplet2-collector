#!/usr/bin/env python3
# TODO make batch size configurable

import argparse
import logging
import logging.handlers
import os
import sys

import daemon
import daemon.pidfile
import pika

from .processor import Processor
from .config import parse_config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
            help="Config file location",
            default="/etc/amplet2/collector.conf")
    parser.add_argument("-d", "--daemonise",
            help="Run as a daemon in the background",
            action="store_true")
    parser.add_argument("-l", "--logfile",
            help="Log file location (if running backgrounded)",
            default="/var/log/amplet2/collector.log")
    parser.add_argument("-p", "--pidfile",
            help="PID file location (if running backgrounded)",
            default="/var/run/amplet2/collector.pid")
    parser.add_argument("-v", "--verbose",
            help="Verbose log output",
            action="store_const",
            dest="loglevel",
            default=logging.INFO,
            const=logging.DEBUG)
    args = parser.parse_args()

    if args.daemonise:
        context = daemon.DaemonContext(
                detach_process=True,
                pidfile=daemon.pidfile.TimeoutPIDLockFile(args.pidfile),
                stderr=sys.stderr,
                stdout=sys.stdout
        )
        with context:
            run(args)
    else:
        run(args)


def run(args):
    # create our own logger, otherwise adjusting log levels causes all the
    # other loggers (e.g. pika) to adjust as well
    logger = logging.getLogger("amplet2_collector")
    logger.propagate = False
    logger.setLevel(args.loglevel)

    if args.daemonise:
        handler = logging.handlers.WatchedFileHandler(filename=args.logfile)
    else:
        handler = logging.StreamHandler()

    formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Starting amplet2 collector")

    config = parse_config(args.config)
    if config is None:
        sys.exit(os.EX_CONFIG)

    # connect to the database
    dbhost = config.get("influxdb", "host", fallback="localhost")
    dbport = config.getint("influxdb", "port", fallback=8086)
    dbuser = config.get("influxdb", "username", fallback="guest")
    dbpass = config.get("influxdb", "password", fallback="guest")
    dbname = config.get("influxdb", "database", fallback="amp")

    processor = Processor(dbhost, dbport, dbuser, dbpass, dbname)

    # connect to the message queue
    amqp_user = config.get("rabbitmq", "username", fallback="guest")
    amqp_pass = config.get("rabbitmq", "password", fallback="guest")
    amqp_host = config.get("rabbitmq", "host", fallback="localhost")
    amqp_port = config.getint("rabbitmq", "port", fallback=5672)
    amqp_queue = config.get("rabbitmq", "queue", fallback="ampqueue")

    logger.info("Connecting to rabbitmq server %s:%d", amqp_host, amqp_port)

    # XXX what happens if rabbitmq goes away while we are connected?
    amqp_credentials = pika.PlainCredentials(amqp_user, amqp_pass)
    amqp_connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=amqp_host, port=amqp_port, credentials=amqp_credentials))

    logger.info("Connected to rabbitmq server %s:%d", amqp_host, amqp_port)

    # the function signature was changed around version 1.0.0, but
    # Debian/Ubuntu don't appear to have caught up yet. Try the old one first.
    amqp_channel = amqp_connection.channel()
    try:
        amqp_channel.basic_consume(
                consumer_callback=processor.process_data,
                queue=amqp_queue)
    except TypeError:
        amqp_channel.basic_consume(
                queue=amqp_queue,
                on_message_callback=processor.process_data)

    logger.info("Consuming from rabbitmq queue '%s'", amqp_queue)
    amqp_channel.start_consuming()


if __name__ == "__main__":
    main()
