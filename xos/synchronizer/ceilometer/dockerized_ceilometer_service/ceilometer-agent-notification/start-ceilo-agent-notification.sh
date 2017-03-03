#!/bin/sh

if [ ! -z "$RABBIT_TRANSPORT_URL" ]; then
   sed -r -i "s,[#]*(transport_url) = (.*),\1 = $RABBIT_TRANSPORT_URL,g" /etc/ceilometer/ceilometer.conf
fi
if [ ! -z "$RABBIT_HOST" ]; then
   sed -r -i "s/[#]*(rabbit_host) = (.*)/\1 = $RABBIT_HOST/g" /etc/ceilometer/ceilometer.conf
fi
if [ ! -z "$RABBIT_USER" ]; then
   sed -r -i "s/[#]*(rabbit_userid) = (.*)/\1 = $RABBIT_USER/g" /etc/ceilometer/ceilometer.conf
fi
if [ ! -z "$RABBIT_PASS" ]; then
   sed -r -i "s/[#]*(rabbit_password) = (.*)/\1 = $RABBIT_PASS/g" /etc/ceilometer/ceilometer.conf
fi

#Run ceilometer-agent-notification
/usr/local/bin/ceilometer-agent-notification
