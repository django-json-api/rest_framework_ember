import copy
import inflection

from django.conf import settings

from rest_framework import renderers
from rest_framework_ember.utils import get_resource_name

from .utils import format_keys


class JSONRenderer(renderers.JSONRenderer):
    """
    Render a JSON response the way Ember Data wants it. Such as:
    {
        "company": {
            "id": 1,
            "name": "nGen Works",
            "slug": "ngen-works",
            "date_created": "2014-03-13 16:33:37"
        }
    }
    """
    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context.get('view')
        resource_name = get_resource_name(view)

        if resource_name == False:
            return super(JSONRenderer, self).render(
                data, accepted_media_type, renderer_context)

        data = format_keys(data, 'camelize') 

        if isinstance(data, list) and getattr(settings,
                                              'REST_EMBER_PLURALIZE_KEYS', False):
            if len(data) > 1:
                resource_name = inflection.pluralize(resource_name)

        try:
            data_copy = copy.copy(data)
            content = data_copy.pop('results')
            data = {resource_name : content, "meta" : data_copy}
        except (TypeError, KeyError, AttributeError) as e:
            
            # Default behavior
            if not resource_name == 'data':
                format_keys(data, 'camelize')

            data = {resource_name : data}
        return super(JSONRenderer, self).render(
            data, accepted_media_type, renderer_context)

