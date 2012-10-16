#coding: utf-8
from web.contrib.template import render_mako

from settings import PROJECT_PATH

render = render_mako(
    directories=[PROJECT_PATH + '/templates'],
    input_encoding='utf-8',
    output_encoding='utf-8',
    module_directory = '/tmp/nowater/mako_modules',
    encoding_errors = 'replace',
    format_exceptions = True,
    default_filters=['decode.utf_8'],
)
