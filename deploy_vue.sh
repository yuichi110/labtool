#!/bin/bash

# Set app root
cd `dirname $0`
approot=`pwd`

# Build Vue
cd $approot
cd vue
npm run build

# Clean up django old static files
cd $approot
rm -rf django/common/templates/*
rm -rf django/common/static/*
rm -rf django/staticfiles/*

# Move vue files to django
cd $approot
mv vue/dist/index.html django/common/templates/
mv vue/dist/* django/common/static

# Collect static
cd $approot
cd django
python3 manage.py collectstatic --no-input
