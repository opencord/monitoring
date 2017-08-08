
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#!/bin/sh

#Insert specified kafka url AFTER the match text
if [ ! -z "$KAFKA_PUBLISHER_URL" ]; then
   sed -i "/publishers:/a \ \ \ \ \ \ \ \ \ \ - $KAFKA_PUBLISHER_URL" /etc/ceilometer/pipeline.yaml
fi
