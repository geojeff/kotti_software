# -*- coding: utf-8 -*-

from fanstatic import Library
from fanstatic import Resource
from js.jquery_form import jquery_form

library = Library('kotti_software', 'static')
kotti_software_js = Resource(
    library,
    'kotti_software.js',
    minified='kotti_software.min.js',
    depends=[jquery_form, ]
)
