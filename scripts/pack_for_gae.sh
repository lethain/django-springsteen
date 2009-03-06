#!/bin/bash
cp -r gae_example gae
cp -r springsteen gae/springsteen
curl http://media.djangoproject.com/releases/1.0/Django-1.0.tar.gz > django.tar.gz
tar -xzvf django.tar.gz
rm django.tar.gz
mv Django-1.0/django gae
rm -rf Django-1.0/
rm -rf gae/django/contrib/comments
rm -rf gae/django/contrib/admin
rm -rf gae/django/contrib/admindocs
rm -rf gae/django/contrib/gis
rm -rf gae/django/contrib/databrowse
rm -rf gae/django/contrib/auth
