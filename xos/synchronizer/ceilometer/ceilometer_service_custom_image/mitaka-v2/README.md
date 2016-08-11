# ceilometer-ansible-mitaka

1.Adding of ceilometer user in mongodb using mongodb ansible module is throwing error,Need to fix.
  Workaroung using scripter is added.
2.Mongodb connection in ceilometer.conf mitaka has error.
  
  [database]
...
connection = mongodb://ceilometer:CEILOMETER_DBPASS@controller:27017/ceilometer

 The above connection is not working.So replaced with below lines:
 metering_connection = mongodb://localhost:27017/ceilometer
 event_connection = mongodb://localhost:27017/ceilometer

3.# mongo --host controller --eval '
  db = db.getSiblingDB("ceilometer");
  db.createUser({user: "ceilometer",
  pwd: "CEILOMETER_DBPASS",
  roles: [ "readWrite", "dbAdmin" ]})'

  The above command creteUser has some issues,so it is replaced with addUser(point 1 using script).
