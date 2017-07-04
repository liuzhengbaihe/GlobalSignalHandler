# -*- coding: utf-8 -*-
# 
# Nitrate is copyright 2010 Red Hat, Inc.
# 
# Nitrate is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version. This program is distributed in
# the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranties of TITLE, NON-INFRINGEMENT,
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
# The GPL text is available in the file COPYING that accompanies this
# distribution and at <http://www.gnu.org/licenses>.
# 
# Authors:
#    Zheng Liu <zheliu@redhat.com>

from django.dispatch import Signal
from django.db import models, signals

class GlobalSignal(object):
    """
    define the global signals incluing both built-in and custom ones
    """
    SIG_SAVE = signals.post_save
    SIG_DELETE = signals.pre_delete
    SIG_BULK_UPDATE = Signal(providing_args=["instance", "kwargs"])

class GlobalSignalQuerySet(models.query.QuerySet):
    """
    Use for listening the bulk update operation.
    Since bulk_create does not return created obj ids, globalSignalHandler does not support this case for now.
    For detailed info, please refer to django source code.
    """
    def update(self, **kwargs):
        instances = super(self.__class__, self).update(**kwargs)
        GlobalSignal.SIG_BULK_UPDATE.send(sender=self.model, instance=self, **kwargs)
        return instances

class GlobalSignalManager(models.Manager):
    """
    Custom manager which expect global signal listener should inherit from this class.
    """
    def get_query_set(self):
        return GlobalSignalQuerySet(self.model, using=self._db)

class GlobalSignalModel(models.Model):
    """
    Used as a base class for listening the bulk update operation.
    Models which expect global signal listener should inherit from this class.
    """
    objects = GlobalSignalManager()

    class Meta:
        abstract = True
