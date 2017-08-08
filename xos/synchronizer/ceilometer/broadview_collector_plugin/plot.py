
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


import plotly.plotly as py
import plotly.graph_objs as go
import time
import requests
#import ceilometerapi
import ast

PLOTLY_USERNAME = 'myusername'
PLOTLY_API_KEY = 'myapikey'
XOS_IP = '1.2.3.4'
XOS_PORT = '9999'

class LAGPlot():
	def __init__(self):
		# use my personal account, need an API key
		py.sign_in(PLOTLY_USERNAME, PLOTLY_API_KEY)
		self.data = {} # all the metrics we read
                self.ceilometer_url = 'http://%s:%s/api/tenant/monitoring/dashboard/metersamples/' % (XOS_IP, XOS_PORT)

	def getDataFromCeilometer(self):
		''' 
		keep track of how many times a lag member resolves
		read new metrics from ceilometer (use timestamps to read
                                                  a range so we get new
                                                  data since last read)
                '''
                url = "%s?%s" % (self.ceilometer_url,"no_hyperlinks=1&meter=broadview.pt.packet-trace-lag-resolution")
                try:
                    response = requests.get(url, auth=('padmin@vicci.org','letmein'))
                except requests.exceptions.RequestException as e:
                    raise e
                samples = response.json()
                #print samples
		for lagresolution in samples:
		    for lagmember in ast.literal_eval(lagresolution['metadata']['lag-members']):
			# here we add any new lagmembers to the hash
			if not lagmember in self.data:
			    self.data[lagmember] = 0
		    lagresolve = lagresolution['metadata']['dst-lag-member']
		    self.data[lagresolve] = self.data[lagresolve] + 1
		
		# now that we have added any new ceilometer data update the
                # pie chart and write it out
                print self.data
	
		data = []
		tmp = {}
		tmp["labels"] = []
		tmp["values"] = []
		tmp["type"] = "pie"
		for  key, val in self.data.iteritems():
                	tmp["labels"].append(key) # the lag member ID
			tmp["values"].append(val) # count
		data.append(tmp)
		fig = {}
		fig["data"] = data
    		fig["layout"] = {}
		# put whatever metadata that makes sense, if any
		fig["layout"]["title"] = 'BroadView LAG Resolution'
                print fig
		return fig
		
	def plotPieToFile(self, data, filename="pie.png"):
		# takes data in the following format and writes it to file
		if not data:
			data = {
    				'data': [{'labels': ['LAG001', 'LAG002', 'LAG003'],
              		         	'values': [19, 26, 55],
              		         	'type': 'pie'}],
    				'layout': {'title': 'BroadView LAG Resolution metadata...'}
     			}

		py.image.save_as(data, filename=filename)

if __name__ == "__main__":
	x = LAGPlot()
	while True:
           print "Plotting data"
	   data = x.getDataFromCeilometer()
	   x.plotPieToFile(data)
	   time.sleep(30)	
