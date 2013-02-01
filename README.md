# GlobalSignalHandler
## 1. Description
GlobalSignalHandler is designed as an app to build a centrial signal listener over TCMS models.
For global signals, a centrial handler will route them to relative handlers. Every handler will create a task
and implement the specific feature like Email Notification and ChangeLog function.
## 2. Features
GlobalSignalHandler can provide centrial signal listener and centrial signal handler for a project.
It can be introduced as a generic signal solution for any django projects. Its features list as below:

 1. Provide a configurable way for developers to decide which models and what operations need listened.

 2. Global listener can listen all the data operations which run through ORM.(create, delete, update, bulk_update)

 3. Provide detailed operation info for handler.(model, instances, operation type and other specific info.)

 4. Build a base handler to restrict the definition of all subclasses, and provide the common actions. 

 5. Introduce async mechanism when handling massive signals to make sure signals are not blocking.
 
## 3. Design Structure
The design of this app is simple. To build a global listener, GlobalSignalHandler connect configured senders(models) to receivers(handlers) for configured signals when EmailHandler and ChangLogHandler are in initialization. Considering there may be many features working based on signals. BaseHandler has abstracted all the possible common actions and pre-processed origin signals to provide a neat interface for subclasses.

![Alt structure][1]
## 4. Implementation
This app defined six classes.

1. SignalConfig

    SignalConfig defines the signals and operation types which will be used for custom configuration.Custom configuration is defined base on function handlers.

    ![Alt signalconfig][2]

2. SignalHandlerType

    SignalHandlerType are defined as metaclass of handlers. This class is used for connecting configured models with handlers for configured signals when a specific Handler class is in initialization.

    ![Alt signalhandlertype][3] 

3. SignalHandlerTask
    
    SignalHandlerTask inherits from threading.Thread. It's used for creating and running task. 

4. BaseHandler

    BaseSignalHandler defined a base handler for all function handlers. It will classify signals and call the specific implementation of subclasses.

    ![Alt class_diagram][4]

5. EmailHandler and ChangeLogHandler
    
    EmailHandler and ChangeLogHandler are subclasses of BaseHandler. They are used for implementing the specific features.

The workflow shows as following image:

![Alt workflow][5]

For source code, please refer to this link:[https://code.engineering.redhat.com/gerrit/#/c/2834/][]
[https://code.engineering.redhat.com/gerrit/#/c/2834/]: https://code.engineering.redhat.com/gerrit/#/c/2834/

## 5. Notes
###5.1 Custom managers which expect global signal listener should inherit from GlobalSignalManager. 
GlobalSignalManager returns the custom QuerySet(GlobalSignalQuerySet) to listen the bulk update operation. To ensure that bulk update operation can emit signals, GlobalSignalQuerySet overrides update method of QuerySet.
Custom managers which are defined as default manager of models should inherit from GlobalSignalManager. GlobalSignalManager is implemented as blew:

    class GlobalSignalQuerySet(models.query.QuerySet):
        """
        Use for listening the bulk update operation.
        """
        def update(self, **kwargs):
            instances = super(self.__class__, self).update(**kwargs)
            SIG_BULK_UPDATE.send(sender=self.model, instance=self, **kwargs)
            return instances
    class GlobalSignalManager(models.Manager):
        """
        Custom manager which expect global signal listener should inherit from this class.
        """
        def get_query_set(self):
            return GlobalSignalQuerySet(self.model, using=self._db)

### 5.2 Models which expect global signal listener should inherit from class TCMSActionModel.
TCMSActionModel set GlobalSignalManager as its default manager. It will return GlobalSignalQuerySet to listen the bulk update operation.Source code show as below:

    class TCMSActionModel(models.Model, UrlMixin):
    """
    TCMS action models.
    Use for global log system.
    Models which expect global signal listener should inherit from this class.
    """
    objects = GlobalSignalManager()
    
    class Meta:
        abstract = True

### 5.3 Please do not use method of 'bulk_create' if expecting global signal listener. 
Since bulk_create does not return created object ids. GlobalSignalHandler does not support this case for now.
For detailed info, please refer to django source code.

[1]:/home/liuzheng/TCMS/globalsignalhandler/structure.jpg
[2]:/home/liuzheng/TCMS/globalsignalhandler/signalconfig.jpg
[3]:/home/liuzheng/TCMS/globalsignalhandler/signalhandlertype.jpg
[4]:/home/liuzheng/TCMS/globalsignalhandler/class_diagram.jpg
[5]:/home/liuzheng/TCMS/globalsignalhandler/workflow.jpg
