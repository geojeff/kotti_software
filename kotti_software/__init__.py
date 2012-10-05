from fanstatic import (
    Library,
    Resource,
    Group,
    )
from pyramid.i18n import TranslationStringFactory
from kotti.static import view_needed
from kotti.util import extract_from_settings
from js.jquery_infinite_ajax_scroll import (
    jquery_infinite_ajax_scroll,
    jquery_infinite_ajax_scroll_css,
)

_ = TranslationStringFactory('kotti_software')

library = Library("kotti_software", "static")
kotti_software_css = Resource(library,
                              "style.css",
                              depends=[jquery_infinite_ajax_scroll_css, ],
                              bottom=True)
kotti_software_js = Resource(library,
                             "kotti_software.js",
                             depends=[jquery_infinite_ajax_scroll, ],
                             bottom=True)
view_needed.add(Group([kotti_software_css, kotti_software_js, ]))


def kotti_configure(settings):
    settings['pyramid.includes'] += ' kotti_software.views'
    settings['kotti.available_types'] += \
            ' kotti_software.resources.SoftwareCollection'
    settings['kotti.available_types'] += \
            ' kotti_software.resources.SoftwareProject'


def check_true(value):
    if value == u'true':
        return True
    return False


SOFTWARECOLLECTION_DEFAULTS = {
    'use_batching': 'true',
    'pagesize': '5',
    'use_auto_batching': 'true',
    'link_headline_overview': 'true',
    }


def collection_settings(name=''):
    prefix = 'kotti_software.collection_settings.'
    if name:
        prefix += name + '.'  # pragma: no cover
    settings = SOFTWARECOLLECTION_DEFAULTS.copy()
    settings.update(extract_from_settings(prefix))
    settings['use_batching'] = check_true(settings['use_batching'])
    try:
        settings['pagesize'] = int(settings['pagesize'])
    except ValueError:
        settings['pagesize'] = 5
    settings['use_auto_batching'] = check_true(settings['use_auto_batching'])
    settings['link_headline_overview'] = \
            check_true(settings['link_headline_overview'])
    return settings
