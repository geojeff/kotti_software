# -*- coding: utf-8 -*-

import logging

from kotti.security import has_permission
from kotti.resources import Document
from kotti_software.resources import SoftwareCollection
from kotti_software.resources import SoftwareProject
from kotti_software.static import kotti_software_js
from kotti.views.util import template_api

from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.renderers import get_renderer

from plone.batching import Batch

from kotti_software import collection_settings

_ = TranslationStringFactory('kotti_software')
log = logging.getLogger(__name__)


@view_defaults(permission='view')
class BaseView(object):

    def __init__(self, context, request):

        self.context = context
        self.request = request

        if has_permission("edit", self.context, self.request):
            kotti_software_js.need()


@view_defaults(context=SoftwareProject,
               permission='view')
class SoftwareProjectView(BaseView):

    @view_config(name='view',
                 renderer='kotti_software:templates/softwareproject-view.pt')
    def view(self):

        self.context.refresh_json()  # [TODO] Expensive: ?

        return {}


@view_defaults(context=SoftwareCollection,
               permission='view')
class SoftwareCollectionView(BaseView):

    @view_config(name="view",
                 renderer="kotti_software:templates/softwarecollection-view.pt")
    def view(self):

        softwareprojects = \
                [c for c in self.context.children
                 if (c.type in ("SoftwareProject", ))
                 and has_permission("view", self.context, self.request)]

        print 'TTTTTTTTJKAJSFDALKSDJFLAKDSFLAKDSLFKADKL', len(softwareprojects), self.context.children

        # [TODO] Expensive: ?
        [project.refresh_json() for project in softwareprojects]

        projects = sorted(softwareprojects, key=lambda x: x.date)

        page = self.request.params.get('page', 1)

        settings = collection_settings()

        if settings['use_batching']:
            projects = Batch.fromPagenumber(projects,
                                            pagesize=settings['pagesize'],
                                            pagenumber=int(page))

        return {
            'api': template_api(self.context, self.request),
            'macros': get_renderer('../templates/macros.pt').implementation(),
            'items': projects,
            'settings': settings,
            }


def includeme(config):

    import forms

    forms.includeme(config)
    config.scan("kotti_software")
