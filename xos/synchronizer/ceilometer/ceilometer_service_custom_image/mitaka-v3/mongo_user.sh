mongo --host localhost --eval '
  db = db.getSiblingDB("ceilometer");
  db.addUser({user: "ceilometer",
  pwd: "password",
  roles: [ "readWrite", "dbAdmin" ]})'

