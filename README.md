A simple modelfield, formfield and widget combination to allow a user pick a single location via google maps
in the django admin (without needing to install GeoDjango etc!).

In this fork, I have removed address geocoding (you manually pick a location on the map) and I 
also incorperated a default formfield so you don't have to mess with ModelAdmins - just add the 
modelfield to your model. 

![Screenshot](http://github.com/pastylegs/django-gmap-admin/blob/master/screenshot.png)

USAGE:
------
- include the `gmap_admin` app in your `settings.py`
- create a model that has a GeoLocationField field
  <pre><code>
    from django.db import models
    from gmap_admin.fields import GeoLocationField
    
    class Rental(models.Model):
        geolocation = GeoLocationField(max_length=100)    
  </code></pre>
  
That should be all you need to get started. If you're not using Django 1.3
make sure that the static media is in a location that will be found and
properly served. The assumed location is `settings.STATIC_URL + 'django_google_maps/js/google-maps-admin.js',`