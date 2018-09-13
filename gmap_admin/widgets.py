from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.utils.encoding import force_text

from gmap_admin import settings


class GoogleMapsWidget(widgets.HiddenInput):
    class Media:
        js = [
            'http://maps.google.com/maps/api/js?key={}&sensor=false'.format(settings.GOOGLE_MAPS_KEY),
            'gmap_admin/js/google-maps-admin.js',
            ]

    @property
    def is_hidden(self):
        return False

    def render(self, name, value, attrs=None):
        if value is None or value == ',':
            value = ""
            center_lng = settings.DEFAULT_LNG
            center_lat = settings.DEFAULT_LAT
        #     def build_attrs(self, base_attrs, extra_attrs=None):
        final_attrs = self.build_attrs(attrs, {'type': self.input_type, 'name': name, })
        # final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if len(value) > 1:
            final_attrs['value'] = force_text(self._format_value(value))
            center_lat,center_lng = final_attrs['value'].split(',')
        else:
            center_lat = settings.DEFAULT_LAT
            center_lng = settings.DEFAULT_LNG
        return mark_safe('''
                    <input{attrs} type="hidden" />
                    <div class="map_canvas_wrapper" style="display:inline-block;">
                        <div id="{map_id}" style="width:{width}px;height:{height}px"></div>
                        <script>
                            django.jQuery(function($) {{
                                $("#{field_id}").gmapAdmin({{
                                        'zoom': {zoom}
                                        ,'lat': '{center_lat}'
                                        ,'lng': '{center_lng}'
                                        ,'map_elem': '#{map_id}'
                                        ,'delete_elem': '#{delete_id}'
                                        ,'add_elem': '#{add_id}'
                                }});
                            }});
                        </script>
                    </div>
                    <p><a id="{delete_id}" href="javascript:void(0)">Remove Marker</a></p>
                    <p><a id="{add_id}" href="javascript:void(0)">Add Marker</a></p>
                    <p class="help">Double click to zoom in and center on a location. 
                        Right click to set the marker on a position. You can also drag and drop the marker.</p>
                '''.format(
            field_id=attrs['id'],
            delete_id='map_delete_{}'.format(attrs['id']),
            add_id='map_add_{}'.format(attrs['id']),
            map_id='map_{}'.format(attrs['id']),
            attrs=flatatt(final_attrs),
            height=settings.HEIGHT,
            width=settings.WIDTH,
            zoom=settings.ZOOM,
            center_lng=center_lng,
            center_lat=center_lat,
        ))
