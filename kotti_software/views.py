import datetime
from dateutil.tz import tzutc

import colander
from colander import Invalid

import logging

from deform.widget import CheckboxWidget
from deform.widget import DateTimeInputWidget
from deform.widget import SelectWidget

from kotti.views.form import AddFormView
from kotti.views.form import EditFormView

from kotti.views.edit import DocumentSchema
from kotti.views.edit import generic_edit
from kotti.views.edit import generic_add

from kotti.views.util import ensure_view_selector

from kotti_software import collection_settings
from kotti_software.resources import SoftwareCollection
from kotti_software.resources import SoftwareProject
from kotti_software.static import kotti_software_js
from kotti_software import _

from kotti.security import has_permission
from kotti.views.util import template_api

from kotti import DBSession

from plone.batching import Batch

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.renderers import get_renderer

log = logging.getLogger(__name__)


class SoftwareCollectionSchema(DocumentSchema):
    pass


@colander.deferred
def deferred_date_missing(node, kw):
    value = datetime.datetime.now()
    return datetime.datetime(value.year, value.month, value.day, value.hour,
        value.minute, value.second, value.microsecond, tzinfo=tzutc())


class SoftwareProjectSchema(DocumentSchema):

    choices = (
        ('', '- Select -'),
        ('use_entered', 'Used entered description (can be blank)'),
        ('use_json_summary', 'Use summary in JSON data'),
        ('use_json_description', 'Use description in JSON data'))
    desc_handling_choice = colander.SchemaNode(
        colander.String(),
        default='use_entered',
        missing='use_entered',
        title=_(u'Description Handling'),
        widget=SelectWidget(values=choices))

    json_url = colander.SchemaNode(
        colander.String(),
        title=_(u'JSON URL'),
        description=_(u'Enter unless doing a manual entry.'),
        missing=_(''),)

    choices = (
        ('', '- Select -'),
        ('use_entered', 'Use entered date'),
        ('use_json_date', 'Use date in JSON data'),
        ('use_now', 'Use the current date'))
    date_handling_choice = colander.SchemaNode(
        colander.String(),
        default='use_json_date',
        title=_(u'Date Handling'),
        widget=SelectWidget(values=choices))
    date = colander.SchemaNode(
        colander.DateTime(),
        title=_(u'Date'),
        description=_(u'Enter date only if date handling = use_entered.'),
        validator=colander.Range(
            min=datetime.datetime(2012, 1, 1, 0, 0,
                                  tzinfo=colander.iso8601.Utc()),
            min_err=_('${val} is too early; min date now is ${min}')),
        widget=DateTimeInputWidget(),
        missing=deferred_date_missing,)

    home_page_url = colander.SchemaNode(
        colander.String(),
        title=_(u'Home Page URL'),
        description=_(u'Leave blank usually, and the URL will be fetched.'),
        missing=_(''),)
    overwrite_home_page_url = colander.SchemaNode(
        colander.Boolean(),
        description='Overwrite home page from JSON',
        default=True,
        missing=True,
        widget=CheckboxWidget(),
        title='')

    docs_url = colander.SchemaNode(
        colander.String(),
        title=_(u'Docs URL'),
        description=_(u'Leave blank usually, and the URL will be fetched.'),
        missing=_(''),)
    overwrite_docs_url = colander.SchemaNode(
        colander.Boolean(),
        description='Overwrite docs URL from JSON',
        default=True,
        missing=True,
        widget=CheckboxWidget(),
        title='')

    package_url = colander.SchemaNode(
        colander.String(),
        title=_(u'Download URL'),
        description=_(u'Leave blank usually, and the URL will be fetched.'),
        missing=_(''),)
    overwrite_package_url = colander.SchemaNode(
        colander.Boolean(),
        description='Overwrite package URL from JSON',
        default=True,
        missing=True,
        widget=CheckboxWidget(),
        title='')

    bugtrack_url = colander.SchemaNode(
        colander.String(),
        title=_(u'Bugtracker URL'),
        description=_(u'Leave blank usually, and the URL will be fetched.'),
        missing=_(''),)
    overwrite_bugtrack_url = colander.SchemaNode(
        colander.Boolean(),
        description='Overwrite bugtracker URL from JSON',
        default=True,
        missing=True,
        widget=CheckboxWidget(),
        title='')


class AddSoftwareProjectFormView(AddFormView):
    item_type = _(u"SoftwareProject")
    item_class = SoftwareProject

    def schema_factory(self):

        def validator(form, value):

            if (value['date_handling_choice'] == 'use_json_date'
                    and not value['json_url']):
                exc = Invalid(
                    form,
                    _(u'Date handling = use_json_date; json_url required')
                )
                exc['json_url'] = _(u'Provide json url for fetching data')
                raise exc

        return SoftwareProjectSchema(validator=validator)

    def add(self, **appstruct):

        return self.item_class(
            title=appstruct['title'],
            description=appstruct['description'],
            body=appstruct['body'],
            tags=appstruct['tags'],
            home_page_url=appstruct['home_page_url'],
            docs_url=appstruct['docs_url'],
            package_url=appstruct['package_url'],
            bugtrack_url=appstruct['bugtrack_url'],
            desc_handling_choice=appstruct['desc_handling_choice'],
            date_handling_choice=appstruct['date_handling_choice'],
            overwrite_home_page_url=appstruct['overwrite_home_page_url'],
            overwrite_docs_url=appstruct['overwrite_docs_url'],
            overwrite_package_url=appstruct['overwrite_package_url'],
            overwrite_bugtrack_url=appstruct['overwrite_bugtrack_url'],
            json_url=appstruct['json_url'],
            date=appstruct['date'],
            )


class EditSoftwareProjectFormView(EditFormView):

    def schema_factory(self):

        def validator(form, value):

            if (value['date_handling_choice'] == 'use_json_date'
                    and not value['json_url']):
                exc = Invalid(
                    form,
                    _(u'Date handling = use_json_date; json_url required')
                )
                exc['json_url'] = _(u'Provide json url for fetching data')
                raise exc

        return SoftwareProjectSchema(validator=validator)

    def edit(self, **appstruct):

        if appstruct['title']:
            self.context.title = appstruct['title']

        if appstruct['description']:
            self.context.description = appstruct['description']

        if appstruct['body']:
            self.context.body = appstruct['body']

        if appstruct['tags']:
            self.context.tags = appstruct['tags']

        self.context.desc_handling_choice = \
                appstruct['desc_handling_choice']
        self.context.date_handling_choice = \
                appstruct['date_handling_choice']
        self.context.overwrite_home_page_url = \
                appstruct['overwrite_home_page_url']
        self.context.overwrite_docs_url = \
                appstruct['overwrite_docs_url']
        self.context.overwrite_package_url = \
                appstruct['overwrite_package_url']
        self.context.overwrite_bugtrack_url = \
                appstruct['overwrite_bugtrack_url']

        if appstruct['home_page_url']:
            self.context.home_page_url = appstruct['home_page_url']

        if appstruct['docs_url']:
            self.context.docs_url = appstruct['docs_url']

        if appstruct['package_url']:
            self.context.package_url = appstruct['package_url']

        if appstruct['bugtrack_url']:
            self.context.bugtrack_url = appstruct['bugtrack_url']

        if self.context.date_handling_choice == 'use_json_date':
            if appstruct['json_url']:
                self.context.json_url = appstruct['json_url']
                self.context.refresh_json()
        else:
            self.context.date = appstruct['date']


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

        settings = collection_settings()
        session = DBSession()
        query = \
            session.query(SoftwareProject).filter(
                    SoftwareProject.parent_id == self.context.id).order_by(
                            SoftwareProject.date.desc())
        items = query.all()
        # [TODO] Expensive: ?
        [item.refresh_json() for item in items]
        query.order_by(SoftwareProject.date.desc())
        items = query.all()
        page = self.request.params.get('page', 1)
        if settings['use_batching']:
            items = Batch.fromPagenumber(items,
                          pagesize=settings['pagesize'],
                          pagenumber=int(page))

        return {
            'api': template_api(self.context, self.request),
            'macros': get_renderer('templates/macros.pt').implementation(),
            'items': items,
            'settings': settings,
            }


@ensure_view_selector
def edit_softwarecollection(context, request):
    return generic_edit(context,
                        request,
                        SoftwareCollectionSchema())


def add_softwarecollection(context, request):
    return generic_add(context,
                       request,
                       SoftwareCollectionSchema(),
                       SoftwareCollection,
                       u'softwarecollection')


#def view_softwareproject(context, request):
#    # [TODO] Expensive: ?
#    context.refresh_json()
#
#    return {}
#
#
#def view_softwarecollection(context, request):
#    settings = collection_settings()
#    macros = get_renderer('templates/macros.pt').implementation()
#    session = DBSession()
#    query = session.query(SoftwareProject).filter(
#        SoftwareProject.parent_id == \
#        context.id).order_by(SoftwareProject.date.desc())
#    items = query.all()
#    # [TODO] Expensive: ?
#    [item.refresh_json() for item in items]
#    query.order_by(SoftwareProject.date.desc())
#    items = query.all()
#    page = request.params.get('page', 1)
#    if settings['use_batching']:
#        items = Batch.fromPagenumber(items,
#                      pagesize=settings['pagesize'],
#                      pagenumber=int(page))
#
#    return {
#        'api': template_api(context, request),
#        'macros': macros,
#        'items': items,
#        'settings': settings,
#        }


def includeme_edit(config):

    config.add_view(
        edit_softwarecollection,
        context=SoftwareCollection,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        add_softwarecollection,
        name=SoftwareCollection.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        EditSoftwareProjectFormView,
        context=SoftwareProject,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        AddSoftwareProjectFormView,
        name=SoftwareProject.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
        )


def includeme_view(config):

#    config.add_view(
#        view_softwarecollection,
#        context=SoftwareCollection,
#        name='view',
#        permission='view',
#        renderer='templates/softwarecollection-view.pt',
#        )
#
#    config.add_view(
#        view_softwareproject,
#        context=SoftwareProject,
#        name='view',
#        permission='view',
#        renderer='templates/softwareproject-view.pt',
#        )

    config.add_static_view('static-kotti_software', 'kotti_software:static')


def includeme(config):
    settings = config.get_settings()
    if 'kotti_software.asset_overrides' in settings:
        asset_overrides = \
                [a.strip()
                 for a in settings['kotti_software.asset_overrides'].split()
                 if a.strip()]
        for override in asset_overrides:
            config.override_asset(to_override='kotti_software',
                                  override_with=override)

    config.scan("kotti_software")

    includeme_edit(config)
    includeme_view(config)
