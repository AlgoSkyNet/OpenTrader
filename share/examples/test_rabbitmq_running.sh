#!/bin/sh
#  Test our communications with the RabbitMQ server.
#  These tests will only work if you have pyrabbit installed:
#  http://pypi.python.org/pypi/pyrabbit
#  and have the 'rabbitmq_management' plugin to rabbitmq enabled.
#  See the OS command 'rabbitmq-plugins list' and make sure
#  the 'rabbitmq_management' and 'rabbitmq_web_dispatch' plugins are enabled.
#  
#  You dont need to have a listener thread running.

# The calling of OTCmd2 may need to be customized for your setup:
if [ -z "$OTPYTHON_EXE" ] ; then
    export OTPYTHON_EXE="sh /c/bin/tpython.sh"
fi

if [ -z "$OTCMD2" ] ; then
    export OTCMD2="$OTPYTHON_EXE OpenTrader/OTCmd2.py"
fi
# You must have the Python package rabbit installed.
$OTPYTHON_EXE -c 'import pyrabbit' || exit 9

# We run these tests in this directory of the source distribution
if [ ! -f setup.py -o -f test.sh ] ; then
    cd ../..
fi
# we put the output in tmp/logs
if [ -z "$OTLOG_DIR" ] ; then
    export OTLOG_DIR="tmp/logs"
  fi
[ -d "$OTLOG_DIR" ] || mkdir "$OTLOG_DIR" || exit 4

${OTCMD2} < share/examples/OTCmd2-rabbit.txt \
	  2>&1|tee "$OTLOG_DIR"/OTCmd2-rabbit.log
