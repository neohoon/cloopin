#!/bin/bash

cd ..
python manage.py build_solr_schema > schema.xml
mv schema.xml solr/solr-4.10.2/example/solr/collection1/conf

