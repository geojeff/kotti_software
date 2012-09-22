import urllib2
import json
import datetime
from dateutil.tz import tzutc
from plone.batching import Batch
from pyramid.renderers import get_renderer
import colander
from deform.widget import SelectWidget
from deform.widget import CheckboxWidget
from deform.widget import DateTimeInputWidget

from kotti import DBSession
from kotti.views.edit import (
    DocumentSchema,
    generic_edit,
    generic_add,
)
from kotti.views.util import (
    ensure_view_selector,
    template_api,
    format_date,
)

from kotti_software.resources import (
    SoftwareCollection,
    SoftwareProject,
)
from kotti_software import (
    collection_settings,
    _,
)


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
    description_handling_choice = colander.SchemaNode(
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

    date = colander.SchemaNode(
        colander.DateTime(),
        title=_(u'Date'),
        description=_(u'Enter for a manual entry. Leave blank to use the creation date or the JSON-fetched date.'),
        validator=colander.Range(
            min=datetime.datetime(2012, 1, 1, 0, 0, tzinfo=colander.iso8601.Utc()),
            min_err=_('${val} is earlier than earliest datetime ${min}')),
        widget=DateTimeInputWidget(),
        missing=deferred_date_missing,)
    choices = (
        ('', '- Select -'),
        ('use_entered', 'Used entered date'),
        ('use_json_date', 'Use date in JSON data'),
        ('use_now', 'Use the current date'))
    date_handling_choice = colander.SchemaNode(
        colander.String(),
        default='use_json_date',
        title=_(u'Date Handling'),
        widget=SelectWidget(values=choices))

    home_page_url = colander.SchemaNode(
        colander.String(),
        title=_(u'Home Page URL'),
        description=_(u'Leave blank usually, and the URL will be fetched. Enter if doing a manual entry.'),
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
        description=_(u'Leave blank usually, and the URL will be fetched. Enter if doing a manual entry.'),
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
        description=_(u'Leave blank usually, and the URL will be fetched. Enter if doing a manual entry.'),
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
        description=_(u'Leave blank usually, and the URL will be fetched. Enter if doing a manual entry.'),
        missing=_(''),)
    overwrite_bugtrack_url = colander.SchemaNode(
        colander.Boolean(),
        description='Overwrite bugtracker URL from JSON',
        default=True,
        missing=True,
        widget=CheckboxWidget(),
        title='')


@ensure_view_selector
def edit_softwarecollection(context, request):
    return generic_edit(context, request, SoftwareCollectionSchema())


def add_softwarecollection(context, request):
    return generic_add(context, request, SoftwareCollectionSchema(), SoftwareCollection, u'softwarecollection')


@ensure_view_selector
def edit_softwareproject(context, request):
    return generic_edit(context, request, SoftwareProjectSchema())


def add_softwareproject(context, request):
    return generic_add(context, request, SoftwareProjectSchema(), SoftwareProject, u'softwareproject')


def view_softwareproject(context, request):
    json_obj = None

    # [TODO] Expensive: ? 
    context.refresh_json()

    context.formatted_date = format_date(context.date)

    return {}


def view_softwarecollection(context, request):
    settings = collection_settings()
    macros = get_renderer('templates/macros.pt').implementation()
    session = DBSession()
    query = session.query(SoftwareProject).filter(\
                SoftwareProject.parent_id == context.id).order_by(SoftwareProject.date.desc())
    items = query.all()
    # [TODO] Expensive: ?
    [item.refresh_json() for item in items]
    query.order_by(SoftwareProject.date.desc())
    items = query.all()
    page = request.params.get('page', 1)
    if settings['use_batching']:
        items = Batch.fromPagenumber(items,
                      pagesize=settings['pagesize'],
                      pagenumber=int(page))

    for item in items:
        item.formatted_date = format_date(item.date)

    return {
        'api': template_api(context, request),
        'macros': macros,
        'items': items,
        'settings': settings,
        }


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
        edit_softwareproject,
        context=SoftwareProject,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        add_softwareproject,
        name=SoftwareProject.type_info.add_view,
        permission='add',
        renderer='kotti:templates/edit/node.pt',
        )


def includeme_view(config):
    config.add_view(
        view_softwarecollection,
        context=SoftwareCollection,
        name='view',
        permission='view',
        renderer='templates/softwarecollection-view.pt',
        )

    config.add_view(
        view_softwareproject,
        context=SoftwareProject,
        name='view',
        permission='view',
        renderer='templates/softwareproject-view.pt',
        )

    config.add_static_view('static-kotti_software', 'kotti_software:static')


def includeme(config):
    settings = config.get_settings()
    if 'kotti_software.asset_overrides' in settings:
        for override in [a.strip()
                         for a in settings['kotti_software.asset_overrides'].split()
                         if a.strip()]:
            config.override_asset(to_override='kotti_software', override_with=override)
    includeme_edit(config)
    includeme_view(config)
