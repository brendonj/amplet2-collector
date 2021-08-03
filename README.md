# amplet2-collector

The [AMP active measurement system](http://amp.wand.net.nz) is a set
of software that is designed to perform continuous, distributed,
black-box active network measurement.

amplet2-collector is a server-side component of the AMP system, and is
responsible for reading the data (from a RabbitMQ queue) and storing
the data in a database (InfluxDB). It will replace
[nntsc](https://github.com/wanduow/nntsc) as we move to use InfluxDB
and Grafana more directly.

Prebuilt Debian/Ubuntu packages are hosted by
[Cloudsmith](https://cloudsmith.io/~wand/repos/amp/packages/).

See also:
- [amplet2](https://github.com/wanduow/amplet2) - Client that performs tests and reports measurements.
- [ampweb](https://github.com/wanduow/amp-web) - Front-end web interface.
- [ampy](https://github.com/wanduow/ampy) - Interface between the display front- and the data storage back-end.
- [nntsc](https://github.com/wanduow/nntsc) - Data storage back-end.

For more information please email contact@wand.net.nz.

----

This code has been developed by the
[University of Waikato](http://www.waikato.ac.nz)
[WAND network research group](http://www.wand.net.nz).
It is licensed under the GNU General Public License (GPL) version 2. Please
see the included file COPYING for details of this license.

Copyright (c) 2020-2021 The University of Waikato, Hamilton, New Zealand.
All rights reserved.
