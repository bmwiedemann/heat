#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from heat.engine import attributes
from heat.engine import resource
from heat.engine import signal_responder
from heat.engine import stack_user
from heat.openstack.common.gettextutils import _
from heat.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class GenericResource(resource.Resource):
    '''
    Dummy resource for use in tests
    '''
    properties_schema = {}
    attributes_schema = {'foo': attributes.Schema('A generic attribute'),
                         'Foo': attributes.Schema('Another generic attribute')}

    def handle_create(self):
        LOG.warning(_('Creating generic resource (Type "%s")') %
                    self.type())

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        LOG.warning(_('Updating generic resource (Type "%s")') %
                    self.type())

    def handle_delete(self):
        LOG.warning(_('Deleting generic resource (Type "%s")') %
                    self.type())

    def _resolve_attribute(self, name):
        return self.name

    def handle_suspend(self):
        LOG.warning(_('Suspending generic resource (Type "%s")') %
                    self.type())

    def handle_resume(self):
        LOG.warning(_('Resuming generic resource (Type "%s")') %
                    self.type())


class ResWithComplexPropsAndAttrs(GenericResource):

    properties_schema = {'a_string': {'Type': 'String'},
                         'a_list': {'Type': 'List'},
                         'a_map': {'Type': 'Map'}}

    attributes_schema = {'list': attributes.Schema('A list'),
                         'map': attributes.Schema('A map'),
                         'string': attributes.Schema('A string')}

    def _resolve_attribute(self, name):
        try:
            return self.properties["a_%s" % name]
        except KeyError:
            return None


class ResourceWithProps(GenericResource):
    properties_schema = {'Foo': {'Type': 'String'}}


class ResourceWithResourceID(GenericResource):
    properties_schema = {'ID': {'Type': 'String'}}

    def handle_create(self):
        super(ResourceWithResourceID, self).handle_create()
        self.resource_id_set(self.properties.get('ID'))

    def handle_delete(self):
        self.mox_resource_id(self.resource_id)

    def mox_resource_id(self, resource_id):
        pass


class ResourceWithComplexAttributes(GenericResource):
    attributes_schema = {
        'list': attributes.Schema('A list'),
        'flat_dict': attributes.Schema('A flat dictionary'),
        'nested_dict': attributes.Schema('A nested dictionary'),
        'none': attributes.Schema('A None')
    }

    list = ['foo', 'bar']
    flat_dict = {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
    nested_dict = {'list': [1, 2, 3],
                   'string': 'abc',
                   'dict': {'a': 1, 'b': 2, 'c': 3}}

    def _resolve_attribute(self, name):
        if name == 'list':
            return self.list
        if name == 'flat_dict':
            return self.flat_dict
        if name == 'nested_dict':
            return self.nested_dict
        if name == 'none':
            return None


class ResourceWithRequiredProps(GenericResource):
    properties_schema = {'Foo': {'Type': 'String',
                                 'Required': True}}


class SignalResource(signal_responder.SignalResponder):
    properties_schema = {}
    attributes_schema = {'AlarmUrl': attributes.Schema('Get a signed webhook')}

    def handle_create(self):
        super(SignalResource, self).handle_create()
        self.resource_id_set(self._get_user_id())

    def handle_signal(self, details=None):
        if self.action in (self.SUSPEND, self.DELETE):
            msg = _('Cannot signal resource during %s') % self.action
            raise Exception(msg)

        LOG.warning(_('Signaled resource (Type "%(type)s") %(details)s')
                    % {'type': self.type(), 'details': details})

    def _resolve_attribute(self, name):
        if name == 'AlarmUrl' and self.resource_id is not None:
            return unicode(self._get_signed_url())


class StackUserResource(stack_user.StackUser):
    properties_schema = {}
    attributes_schema = {}

    def handle_create(self):
        super(StackUserResource, self).handle_create()
        self.resource_id_set(self._get_user_id())
