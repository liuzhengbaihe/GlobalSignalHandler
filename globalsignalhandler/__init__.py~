from threading import Thread

from django.dispatch import Signal
from django.db.models import signals

from tcms.core.models import GlobalSignal
from tcms.apps.testplans.models import TestPlan
from tcms.apps.testcases.models import TestCase, TestCasePlan
from tcms.apps.testruns.models import TestRun, TestCaseRun

class SignalConfig(object):
    MODEL_ALL = 'ALL'
    OPERATION_CREATE = 'create'
    OPERATION_UPDATE = 'update'
    OPERATION_DELETE = 'delete'

class SignalHandlerType(type):
    def __init__(cls, name, bases, attr):
        """
        connect signals to handlers. Signal object can not bring the signal type info,
        so handle them respectively.
        """
        handling = getattr(cls, 'handling', None)
        if handling:
            cls.connect(handling)

    def connect(cls, handling):
        for model_kls, signals in handling.iteritems():
            for signal in signals:
                if model_kls == SignalConfig.MODEL_ALL:
                    signal.connect(cls.get_handler(signal))
                else:
                    signal.connect(cls.get_handler(signal), sender=model_kls)

class SignalHandlerTask(Thread):
    def __init__(self, handler, **kwargs):
        super(self.__class__, self).__init__(target=handler, kwargs=kwargs)


class BaseHandler(object):
    """
    async is a flag to decide if using thread mechanism to run handler.
    """
    __metaclass__ = SignalHandlerType
    async = True

    @classmethod
    def get_handler(cls, signal):
        """
        get relative handler based on signal type.
        """
        handlers = {
                GlobalSignal.SIG_SAVE: cls._save_handler,
                GlobalSignal.SIG_BULK_UPDATE: cls._bulk_update_handler,
                GlobalSignal.SIG_DELETE: cls._delete_handler,
                }
        return handlers.get(signal, None)

    @classmethod
    def execute(cls, handler, **kwargs):
        """
        start running handler tasks based on async.
        """
        if cls.async:
            task = SignalHandlerTask(handler, **kwargs)
            task.start()
        else:
            handler(**kwargs)

    @classmethod
    def _save_handler(cls, **kwargs):
        """
        Devide handlers into three types:'create', 'update', 'delete'.
        Put operation type into kwargs.
        """
        if kwargs['created']:
            kwargs['operation'] = SignalConfig.OPERATION_CREATE
            handler = getattr(cls, 'create_handler', cls.default_handler)
        else:
            kwargs['operation'] = SignalConfig.OPERATION_UPDATE
            handler = getattr(cls, 'update_handler', cls.default_handler)
        cls.execute(handler=handler, **kwargs)

    @classmethod
    def _delete_handler(cls, **kwargs):
        kwargs['operation'] = SignalConfig.OPERATION_DELETE
        handler = getattr(cls, 'delete_handler', cls.default_handler)
        cls.execute(handler=handler, **kwargs)

    @classmethod
    def _bulk_update_handler(cls, **kwargs):
        kwargs['operation'] = SignalConfig.OPERATION_UPDATE
        handler = getattr(cls, 'update_handler', cls.default_handler)
        cls.execute(handler=handler, **kwargs)

    @classmethod
    def default_handler(cls, **kwargs):
        """
        This method is called if create_handler/update_handler/delete_handler of subclass is not defined.
        """
        pass

class EmailHandler(BaseHandler):
    handling = {
        TestPlan: (GlobalSignal.SIG_SAVE, GlobalSignal.SIG_BULK_UPDATE, GlobalSignal.SIG_DELETE),
        TestCase: (GlobalSignal.SIG_SAVE, GlobalSignal.SIG_BULK_UPDATE, GlobalSignal.SIG_DELETE),
        TestCasePlan: (GlobalSignal.SIG_SAVE,GlobalSignal.SIG_BULK_UPDATE, GlobalSignal.SIG_DELETE),
        TestRun: (GlobalSignal.SIG_SAVE, GlobalSignal.SIG_BULK_UPDATE, GlobalSignal.SIG_DELETE),
        TestCaseRun: (GlobalSignal.SIG_SAVE, GlobalSignal.SIG_BULK_UPDATE, GlobalSignal.SIG_DELETE),
    }

    @classmethod
    def create_handler(cls, **kwargs):
        """
        notification triggered by create operation.
        """
        pass

    @classmethod
    def update_handler(cls, **kwargs):
        """
        notification triggered by update operation.
        """
        pass

    @classmethod
    def delete_handler(cls, **kwargs):
        """
        notification triggered by delete operation.
        """
        pass

class ChangeLogHandler(BaseHandler):
    handling = {
        SignalConfig.MODEL_ALL: (GlobalSignal.SIG_SAVE, GlobalSignal.SIG_BULK_UPDATE, GlobalSignal.SIG_DELETE)
    }

    @classmethod
    def default_handler(cls, **kwargs):
        """
        create snapshot of operated model
        """
        pass

