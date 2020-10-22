Figure out package names and contents:

    amplet2-client
        - as is

    amplet2-server -> amplet2-server-modules?
        - contains test module parsers

    amplet2-collector -> amplet2-server
        - contains process to unpack and then store test results

Should they all be in the same repository? Need different versioning?
    - Lots of changes only affect the client, don't need new server packages


Deps:
    - pika
    - configparser
    - logging
