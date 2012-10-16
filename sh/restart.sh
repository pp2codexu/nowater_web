#!/bin/bash
command="cd /home/piglei/webapps/nowater/nowater_web &&\
svn up &&\
cp _settings.py settings.py &&\
/home/piglei/webapps/nowater/nowater_web/runctl restart
"
ssh zhikanlz.com -l piglei "${command}"
