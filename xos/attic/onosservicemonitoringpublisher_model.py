def __init__(self, *args, **kwargs):
    super(ONOSServiceMonitoringPublisher, self).__init__(*args, **kwargs)

def can_update(self, user):
    #Don't allow creation of this model instances for non-admin users also
    return False

def save(self, *args, **kwargs):
    if not self.creator:
        if not getattr(self, "caller", None):
            # caller must be set when creating a monitoring channel since it creates a slice
            raise XOSProgrammingError("ONOSServiceMonitoringPublisher's self.caller was not set")
        self.creator = self.caller
        if not self.creator:
            raise XOSProgrammingError("ONOSServiceMonitoringPublisher's self.creator was not set")

    if self.pk is None:
        #Allow only one openstack monitoring publisher per admin user
        publisher_count = sum ( [1 for onospublisher in ONOSServiceMonitoringPublisher.get_tenant_objects().all() if (onospublisher.creator == self.creator)] )
        if publisher_count > 0:
            raise XOSValidationError("Already %s openstack publishers exist for user Can only create max 1 ONOSServiceMonitoringPublisher instance per user" % str(publisher_count))

    super(ONOSServiceMonitoringPublisher, self).save(*args, **kwargs)