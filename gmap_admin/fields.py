import logging

from django.db import models
from django.core import exceptions
from django import forms

from gmap_admin.widgets import GoogleMapsWidget


logger = logging.getLogger(__name__)


def typename(obj):
    """Returns the type of obj as a string. More descriptive and specific than
    type(obj), and safe for any object, unlike __class__."""
    if hasattr(obj, '__class__'):
        return getattr(obj, '__class__').__name__
    else:
        return type(obj).__name__


class GeoPt(object):
    """A geographical point."""

    lat = None
    lon = None

    def __init__(self, lat, lon=None):
        if lon is None:
            lat, lon = self._split_geo_point(lat)
        self.lat = self._validate_geo_range(lat, 90)
        self.lon = self._validate_geo_range(lon, 180)

    def __unicode__(self):
        return ','.join(self.lat, self.lon)

    def __len__(self):
        return len(self.__unicode__())

    @staticmethod
    def _split_geo_point(geo_point):
        """splits the geo point into lat and lon"""
        try:
            return geo_point.split(',')
        except (AttributeError, ValueError):
            raise exceptions.ValidationError(
                'Expected a "lat,long" formatted string; received {} (a {}).'.format(
                    geo_point, typename(geo_point)))

    @staticmethod
    def _validate_geo_range(geo_part, range_val):
        try:
            geo_part = float(geo_part)
            if abs(geo_part) > range_val:
                raise exceptions.ValidationError(
                    'Must be between - {} and {}; received {}'.format(range_val, range_val, geo_part)
                )
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                'Expected float, received {} (a {}).'.format(geo_part, typename(geo_part))
            )
        return geo_part


class GoogleMapsFormField(forms.CharField):
    pass


class GeoLocationField(models.CharField):
    """
    A geographical point, specified by floating-point latitude and longitude
    coordinates. Often used to integrate with mapping sites like Google Maps.
    May also be used as ICBM coordinates.

    This is the georss:point element. In XML output, the coordinates are
    provided as the lat and lon attributes. See: http://georss.org/

    Serializes to '<lat>,<lon>'. Raises BadValueError if it's passed an invalid
    serialized string, or if lat and lon are not valid floating points in the
    ranges [-90, 90] and [-180, 180], respectively.
    """
    description = 'A geographical point, specified by floating-point ' \
                  'latitude and longitude coordinates.'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 100
        super(GeoLocationField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, GeoPt):
            return value
        return GeoPt(value)

    def get_prep_value(self, value):
        if value == u'':
            return None
        try:
            return ','.join(value.lat, value.lon)
        except AttributeError:
            return ''

    def get_prep_lookup(self, lookup_type, value):
        # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def value_to_string(self, obj):
        logger.debug(obj)
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'widget': GoogleMapsWidget, }
        kwargs.update(defaults)
        return super(GeoLocationField, self).formfield(form_class=GoogleMapsFormField, **kwargs)


# legacy support for south
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^gmap_admin\.fields\.GeoLocationField"])
except ImportError:
    pass
