secure
======

Python program that keeps an eye on `/var/log/secure.log` and reports "Failed password" attempts.

Features:
--------
* Checks the file `/var/log/secure.log` every minute for new occurrence of **Failed password** message(s).
* If new attempt is found, it stores details in the SQLite database.
* After adding details to the database, it raises a desktop notification informing the user about the break-in attempt.

Requirements:
------------
To obtain expected results using `secure`, you need to configure `rsyslog` to log dates compatible with RFC 3146. This is because by default `rsyslog` doesn't log year in the messages. To enable RFC 3146 compatibility, comment out below line from `/etc/rsyslog.conf`:
~~~
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
~~~
and add below two lines:
~~~
$template RFC3164fmt,"<%PRI%>%TIMESTAMP% %HOSTNAME% %syslogtag%%msg%"
*.* /var/log/all-messages.log;ExampleFormat"
~~~

Usage:
------
~~~
$python secure.py
~~~
