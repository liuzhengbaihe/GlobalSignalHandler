from threading import Thread

from django.dispatch import Signal
from django.db.models import signals

from tcms.core.models import SIG_BULK_UPDATE
from tcms.apps.testplans.models import TestPlan
from tcms.apps.testcases.models import TestCase, TestCasePlan
from tcms.apps.testruns.models import TestRun, TestCaseRun

class SignalConfig(object):
    SIG_SAVE = signals.post_save
    SIG_DELETE = signals.pre_delete
    SIG_BULK_UPDATE = SIG_BULK_UPDATE
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
    pass

class BaseHandler(object):
    __metaclass__ = SignalHandlerType
    async = True

    @classmethod
    def get_handler(cls, signal):
        """
        get relative handler based on signal type.
        """
        handlers = {
                SignalConfig.SIG_SAVE: cls._save_handler,
                SignalConfig.SIG_BULK_UPDATE: cls._bulk_update_handler,
                SignalConfig.SIG_DELETE: cls._delete_handler,
                }
        return handlers.get(signal, None)

    @classmethod
    def _save_handler(cls, **kwargs):
        """
        Devide handlers into three types:'create', 'update', 'delete'.
        Put operation type into kwargs.
        """
        if kwargs['created']:
            kwargs['operation'] = SignalConfig.OPERATION_CREATE
            handler = cls.create_handler
        else:
            kwargs['operation'] = SignalConfig.OPERATION_UPDATE
            handler = cls.update_handler
        if cls.async:
            task = SignalHandlerTask(target=handler, kwargs=kwargs)
            task.start()
        else:
            handler(**kwargs)
        pass

    @classmethod
    def _delete_handler(cls, **kwargs):
        kwargs['operation'] = SignalConfig.OPERATION_DELETE
        if cls.async:
            task = SignalHandlerTask(target=cls.delete_handler, kwargs=kwargs)
            task.start()
        else:
            cls.delete_handler(**kwargs)
        pass

    @classmethod
    def _bulk_update_handler(cls, **kwargs):
        kwargs['operation'] = SignalConfig.OPERATION_UPDATE
        if cls.async:
            task = SignalHandlerTask(target=cls.update_handler, kwargs=kwargs)
            task.start()
        else:
            cls.update_handler(**kwargs)
        pass

    @classmethod
    def _generic_handler(cls, **kwargs):
        if cls.async:
            task = SignalHandlerTask(target=cls.generic_handler, kwargs=kwargs)
            task.start()
        else:
            cls.generic_handler(**kwargs)

class EmailHandler(BaseHandler):
    handling = {
        TestPlan: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestCase: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestCasePlan: (SignalConfig.SIG_SAVE,SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestRun: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
        TestCaseRun: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE),
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

    @classmethod
    def generic_handler(cls, **kwargs):
        """
        generic handler for all operaiton
        """
        pass

class ChangeLogHandler(BaseHandler):
    handling = {
        SignalConfig.MODEL_ALL: (SignalConfig.SIG_SAVE, SignalConfig.SIG_BULK_UPDATE, SignalConfig.SIG_DELETE)
    }

    @classmethod
    def create_handler(cls, **kwargs):
        """
        changelog triggered by create operation.
        """
        pass

    @classmethod
    def update_handler(cls, **kwargs):
        """
        changelog triggered by update operation.
        """
        pass

    @classmethod
    def delete_handler(cls, **kwargs):
        """
        changelog triggered by delete operation.
        """
        pass

    @classmethod
    def generic_handler(cls, **kwargs):
        """
        create snapshot of operated model
        """
        pass

