import datetime
from dateutil.tz import tzutc

import colander
from colander import Invalid

import logging

from deform.widget import CheckboxWidget
from deform.widget import DateTimeInputWidget
from deform.widget import SelectWidget
from deform.widget import RadioChoiceWidget

from kotti.views.form import AddFormView
from kotti.views.form import EditFormView

from kotti.views.edit import DocumentSchema

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

    choices = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending'))
    sort_order_choice = colander.SchemaNode(colander.String(),
            title=_(u'Sort Order'),
            default='descending',
            widget=RadioChoiceWidget(values=choices),
            validator=colander.OneOf(('ascending', 'descending')))


@colander.deferred
def deferred_date_missing(node, kw):

    value = datetime.datetime.now()

    return datetime.datetime(value.year, value.month, value.day, value.hour,
        value.minute, value.second, value.microsecond, tzinfo=tzutc())


class SoftwareProjectSchema(DocumentSchema):

    choices = (
        ('', '- Select -'),
        ('use_entered', 'Used entered description (can be blank)'),
        ('use_pypi_summary', 'Use summary in PyPI data'),
        ('use_pypi_description', 'Use description in PyPI data'),
        ('use_github_description', 'Use description in GitHub data'),
        ('use_bitbucket_description', 'Use description in Bitbucket data'))
    desc_handling_choice = colander.SchemaNode(
        colander.String(),
        default='use_entered',
        missing='use_entered',
        title=_(u'Description Handling'),
        widget=SelectWidget(values=choices))

    pypi_url = colander.SchemaNode(
        colander.String(),
        title=_(u'PyPI URL'),
        description=_(u'Enter unless doing a manual entry.'),
        missing=_(''),)

    choices = (
        ('', '- Select -'),
        ('use_entered', 'Use entered date'),
        ('use_pypi_date', 'Use date in PyPI data'),
        ('use_github_date', 'Use date in GitHub data'),
        ('use_bitbucket_date', 'Use date in Bitbucket data'),
        ('use_now', 'Use current date and time'))
    date_handling_choice = colander.SchemaNode(
        colander.String(),
        default='use_pypi_date',
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
        description='Overwrite home page from PyPI',
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
        description='Overwrite docs URL from PyPI',
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
        description='Overwrite package URL from PyPI',
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
        description='Overwrite bugtracker URL from PyPI',
        default=True,
        missing=True,
        widget=CheckboxWidget(),
        title='')

    github_owner = colander.SchemaNode(
        colander.String(),
        title=_(u'GitHub Owner'),
        description=_(u'Name of the owner on GitHub for the project repo.'),
        missing=_(''),)

    github_repo = colander.SchemaNode(
        colander.String(),
        title=_(u'GitHub Repo'),
        description=_(u'Name of the repo on GitHub for the project.'),
        missing=_(''),)

    bitbucket_owner = colander.SchemaNode(
        colander.String(),
        title=_(u'Bitbucket Owner'),
        description=_(u'Name of the owner on Bitbucket for the project repo.'),
        missing=_(''),)

    bitbucket_repo = colander.SchemaNode(
        colander.String(),
        title=_(u'Bitbucket Repo'),
        description=_(u'Name of the repo on Bitbucket for the project.'),
        missing=_(''),)


def software_project_validator(form, value):

    if ((value['date_handling_choice'] == 'use_pypi_date' or
         value['desc_handling_choice'] == 'use_pypi_summary' or
         value['desc_handling_choice'] == 'use_pypi_description') and
        not value['pypi_url']):
        msg = u'For fetching date or description from PyPI, PyPI url required'
        exc = Invalid(form, _(msg))
        exc['pypi_url'] = _(u'Provide PyPI url for fetching data')
        raise exc

    if ((value['date_handling_choice'] == 'use_github_date' or
         value['desc_handling_choice'] == 'use_github_description') and
        (not value['github_owner'] or not value['github_repo'])):
        msg = u'For fetching date or description from GitHub, owner and repo required'
        exc = Invalid(form, _(msg))
        exc['github_owner'] = _(u'Provide GitHub owner for api call')
        exc['github_repo'] = _(u'Provide GitHub repo for api call')
        raise exc

    if value['github_owner'] and not value['github_repo']:
        msg = u'To specifiy a GitHub repo, both owner and repo required'
        exc = Invalid(form, _(msg))
        exc['github_repo'] = _(u'Provide GitHub repo for api call')
        raise exc

    if value['github_repo'] and not value['github_owner']:
        msg = u'To specifiy a GitHub repo, both owner and repo required'
        exc = Invalid(form, _(msg))
        exc['github_owner'] = _(u'Provide GitHub owner for api call')
        raise exc

    if ((value['date_handling_choice'] == 'use_bitbucket_date' or
         value['desc_handling_choice'] == 'use_bitbucket_description') and
        (not value['bitbucket_owner'] or not value['bitbucket_repo'])):
        msg = u'For fetching date or description from Bitbucket, owner and repo required'
        exc = Invalid(form, _(msg))
        exc['bitbucket_owner'] = _(u'Provide Bitbucket owner for api call')
        exc['bitbucket_repo'] = _(u'Provide Bitbucket repo for api call')
        raise exc

    if value['bitbucket_owner'] and not value['bitbucket_repo']:
        msg = u'To specifiy a Bitbucket repo, both owner and repo required'
        exc = Invalid(form, _(msg))
        exc['bitbucket_repo'] = _(u'Provide Bitbucket repo for api call')
        raise exc

    if value['bitbucket_repo'] and not value['bitbucket_owner']:
        msg = u'To specifiy a Bitbucket repo, both owner and repo required'
        exc = Invalid(form, _(msg))
        exc['bitbucket_owner'] = _(u'Provide Bitbucket owner for api call')
        raise exc


class AddSoftwareProjectFormView(AddFormView):
    item_type = _(u"SoftwareProject")
    item_class = SoftwareProject

    def schema_factory(self):

        return SoftwareProjectSchema(validator=software_project_validator)

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
            pypi_url=appstruct['pypi_url'],
            date=appstruct['date'],
            github_owner=appstruct['github_owner'],
            github_repo=appstruct['github_repo'],
            bitbucket_owner=appstruct['bitbucket_owner'],
            bitbucket_repo=appstruct['bitbucket_repo'],
            )


class EditSoftwareProjectFormView(EditFormView):

    def schema_factory(self):

        return SoftwareProjectSchema(validator=software_project_validator)

    def edit(self, **appstruct):

        pypi_info_changed = False
        github_info_changed = False
        bitbucket_info_changed = False

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

        if self.context.date_handling_choice == 'use_pypi_date':
            if appstruct['pypi_url']:
                self.context.pypi_url = appstruct['pypi_url']
                pypi_info_changed = True
        else:
            self.context.date = appstruct['date']

        if appstruct['github_owner']:
            self.context.github_owner = appstruct['github_owner']
            github_info_changed = True

        if appstruct['github_repo']:
            self.context.github_repo = appstruct['github_repo']
            github_info_changed = True

        if appstruct['bitbucket_owner']:
            self.context.bitbucket_owner = appstruct['bitbucket_owner']
            bitbucket_info_changed = True

        if appstruct['bitbucket_repo']:
            self.context.bitbucket_repo = appstruct['bitbucket_repo']
            bitbucket_info_changed = True

        if pypi_info_changed:
            self.context.refresh_pypi()

        if github_info_changed:
            self.context.refresh_github()

        if bitbucket_info_changed:
            self.context.refresh_bitbucket()


class AddSoftwareCollectionFormView(AddFormView):
    item_type = _(u"SoftwareCollection")
    item_class = SoftwareCollection

    def schema_factory(self):

        return SoftwareCollectionSchema()

    def add(self, **appstruct):
        sort_order_is_ascending = False

        if appstruct['sort_order_choice'] == 'ascending':
            sort_order_is_ascending = True

        return self.item_class(
            title=appstruct['title'],
            description=appstruct['description'],
            body=appstruct['body'],
            tags=appstruct['tags'],
            sort_order_is_ascending=sort_order_is_ascending,
            )


class EditSoftwareCollectionFormView(EditFormView):

    def schema_factory(self):

        return SoftwareCollectionSchema()

    def edit(self, **appstruct):

        if appstruct['title']:
            self.context.title = appstruct['title']

        if appstruct['description']:
            self.context.description = appstruct['description']

        if appstruct['body']:
            self.context.body = appstruct['body']

        if appstruct['tags']:
            self.context.tags = appstruct['tags']

        if appstruct['sort_order_choice'] == 'ascending':
            self.sort_order_is_ascending = True
        else:
            self.sort_order_is_ascending = False


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

    @view_config(renderer='kotti_software:templates/softwareproject-view.pt')
    def view(self):

        # [TODO] Are these calls too expensive?
        self.context.refresh_pypi()
        self.context.refresh_github()
        self.context.refresh_bitbucket()

        return {}


@view_defaults(context=SoftwareCollection,
               permission='view')
class SoftwareCollectionView(BaseView):

    @view_config(
             renderer="kotti_software:templates/softwarecollection-view.pt")
    def view(self):

        session = DBSession()

        query = session.query(SoftwareProject).filter(
                SoftwareProject.parent_id == self.context.id)

        items = query.all()

        # [TODO] Are these calls too expensive?
        [item.refresh_pypi() for item in items]
        [item.refresh_github() for item in items]
        [item.refresh_bitbucket() for item in items]

        if self.context.sort_order_is_ascending:
            items = sorted(items, key=lambda x: x.date)
        else:
            items = sorted(items, key=lambda x: x.date, reverse=True)

        page = self.request.params.get('page', 1)

        settings = collection_settings()

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


def includeme_edit(config):

    config.add_view(
        EditSoftwareCollectionFormView,
        context=SoftwareCollection,
        name='edit',
        permission='edit',
        renderer='kotti:templates/edit/node.pt',
        )

    config.add_view(
        AddSoftwareCollectionFormView,
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
