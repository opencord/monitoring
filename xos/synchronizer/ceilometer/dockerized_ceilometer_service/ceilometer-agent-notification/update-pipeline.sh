#!/bin/sh

#Insert specified kafka url AFTER the match text
if [ ! -z "$KAFKA_PUBLISHER_URL" ]; then
   sed -i "/publishers:/a \ \ \ \ \ \ \ \ \ \ - $KAFKA_PUBLISHER_URL" /etc/ceilometer/pipeline.yaml
fi
