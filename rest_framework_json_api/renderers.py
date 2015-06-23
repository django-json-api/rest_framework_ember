"""
Renderers
"""
from rest_framework import renderers
from rest_framework_ember.utils import get_resource_name

from .utils import format_keys, format_resource_name


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
        # Get the resource name.
        resource_name = get_resource_name(view)

        # If no `resource_name` is found, render the default response.
        if not resource_name:
            return super(JSONRenderer, self).render(
                data, accepted_media_type, renderer_context
            )

        # If this is an error response, skip the rest.
        if 'errors' in resource_name or resource_name == 'data':
            return super(JSONRenderer, self).render(
                {resource_name: data}, accepted_media_type, renderer_context
            )

        # Camelize the keynames.
        formatted_data = format_keys(data, 'camelize')

        # Check if it's paginated data and contains a `results` key.
        if isinstance(formatted_data, dict):
            results = formatted_data.get('results')
        else:
            results = None

        # Pluralize the resource_name.
        resource_name = format_resource_name(
            results or formatted_data, resource_name
        )

        if results:
            rendered_data = {
                resource_name: results,
                'meta': formatted_data
            }
        else:
            rendered_data = {
                resource_name: formatted_data
            }

        return super(JSONRenderer, self).render(
            rendered_data, accepted_media_type, renderer_context
        )
