import urllib2
import json
import datetime
from dateutil.tz import tzutc
from plone.batching import Batch
from pyramid.renderers import get_renderer
import colander
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
    date = colander.SchemaNode(
        colander.DateTime(),
        title=_(u'Date'),
        description=_(u'Choose date of the software project. '\
                      u'If you leave this empty the creation date is used.'),
        validator=colander.Range(
            min=datetime.datetime(2012, 1, 1, 0, 0, tzinfo=colander.iso8601.Utc()),
            min_err=_('${val} is earlier than earliest datetime ${min}')),
        widget=DateTimeInputWidget(),
        missing=deferred_date_missing,
    )
    json_url = colander.SchemaNode(colander.String())


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
    context.refresh_date()

#    if context.json_url:
#        json_raw = urllib2.urlopen(context.json_url).read()
#        json_obj = json.loads(json_raw)
#
#    if json_obj:
#        upload_time = datetime.datetime.strptime(json_obj['urls'][0]['upload_time'],
#                                                 "%Y-%m-%dT%H:%M:%S")
#        context.formatted_date = format_date(upload_time)

    return {}


def view_softwarecollection(context, request):
    settings = collection_settings()
    macros = get_renderer('templates/macros.pt').implementation()
    session = DBSession()
    query = session.query(SoftwareProject).filter(\
                SoftwareProject.parent_id == context.id).order_by(SoftwareProject.date.desc())
    # [TODO] Expensive: ?
    items = query.all()
    [item.refresh_date() for item in items]
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
