import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
#from services.exampleservice.models import *
from services.monitoring.models import *
django.setup()

for o in CeilometerService.get_service_objects().all():
   print "Delete", o
   o.delete()

print "wait for perma-deletion"

while MonitoringChannel.deleted_objects.all().exists() or CeilometerService.deleted_objects.all().exists():
    pass
