import datetime
import json
import urllib2
from dateutil.tz import tzutc

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import types

from zope.interface import implements

from kotti.resources import IDocument
from kotti.resources import IDefaultWorkflow
from kotti.resources import Document

from kotti_software import _


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime

    def process_bind_param(self, value, engine):
        if value is not None:
            return value.astimezone(tzutc())

    def process_result_value(self, value, engine):
        if value is not None:
            return datetime.datetime(value.year, value.month, value.day,
                    value.hour, value.minute, value.second, value.microsecond,
                    tzinfo=tzutc())


class SoftwareCollection(Document):
    implements(IDocument, IDefaultWorkflow)

    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)

    sort_order_is_ascending = Column('sort_order_is_ascending', Boolean())

    type_info = Document.type_info.copy(
        name=u'SoftwareCollection',
        title=_(u'SoftwareCollection'),
        add_view=u'add_softwarecollection',
        addable_to=[u'Document'],
        )

    def __init__(self,
                 sort_order_is_ascending=False,
                 **kwargs):
        super(SoftwareCollection, self).__init__(**kwargs)

        self.sort_order_is_ascending = sort_order_is_ascending


class SoftwareProject(Document):
    implements(IDocument, IDefaultWorkflow)

    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)

    desc_handling_choice = 'use_entered'
    #  other choices: ('use_json_summary',
    #                  'use_json_description',
    #                  'use_github_description'
    #                  'use_bitbucket_description')

    # String(1000) usage is for mysql compatibility.
    pypi_url = Column('pypi_url', String(1000))

    date = Column('date', UTCDateTime())
    date_handling_choice = 'use_pypi_date'
    #  other choices: ('use_github_date',
    #                  'use_bitbucket_date',
    #                  'use_entered',
    #                  'use_now')

    home_page_url = Column('home_page_url', String(1000))
    docs_url = Column('docs_url', String(1000))
    package_url = Column('package_url', String(1000))
    bugtrack_url = Column('bugtrack_url', String(1000))

    overwrite_home_page_url = Column('overwrite_home_page_url', Boolean())
    overwrite_docs_url = Column('overwrite_docs_url', Boolean())
    overwrite_package_url = Column('overwrite_package_url', Boolean())
    overwrite_bugtrack_url = Column('overwrite_bugtrack_url', Boolean())

    github_owner = Column('github_owner', String(1000))
    github_repo = Column('github_repo', String(1000))
    github_date = Column('github_date', UTCDateTime())

    bitbucket_owner = Column('bitbucket_owner', String(1000))
    bitbucket_repo = Column('bitbucket_repo', String(1000))
    bitbucket_date = Column('bitbucket_date', UTCDateTime())

    type_info = Document.type_info.copy(
        name=u'SoftwareProject',
        title=_(u'SoftwareProject'),
        add_view=u'add_softwareproject',
        addable_to=[u'SoftwareCollection'],
        )

    def __init__(self,
                 desc_handling_choice='use_entered',
                 pypi_url='',
                 date=None,
                 date_handling_choice='use_pypi_date',
                 home_page_url='',
                 docs_url='',
                 package_url='',
                 bugtrack_url='',
                 overwrite_home_page_url=True,
                 overwrite_docs_url=True,
                 overwrite_package_url=True,
                 overwrite_bugtrack_url=True,
                 github_owner='',
                 github_repo='',
                 bitbucket_owner='',
                 bitbucket_repo='',
                 **kwargs):
        super(SoftwareProject, self).__init__(**kwargs)

        self.desc_handling_choice = desc_handling_choice

        self.pypi_url = pypi_url

        self.date_handling_choice = date_handling_choice

        self.home_page_url = home_page_url
        self.docs_url = docs_url
        self.package_url = package_url
        self.bugtrack_url = bugtrack_url
        self.overwrite_home_page_url = overwrite_home_page_url
        self.overwrite_docs_url = overwrite_docs_url
        self.overwrite_package_url = overwrite_package_url
        self.overwrite_bugtrack_url = overwrite_bugtrack_url

        self.github_owner = github_owner
        self.github_repo = github_repo

        self.bitbucket_owner = bitbucket_owner
        self.bitbucket_repo = bitbucket_repo

        github_refreshed = False
        bitbucket_refreshed = False

        if self.date_handling_choice.startswith('use_pypi'):
            if self.pypi_url:
                self.refresh_pypi()
        elif self.date_handling_choice.startswith('use_github'):
            if self.github_owner and self.github_repo:
                self.refresh_github()
                github_refreshed = True
        elif self.date_handling_choice.startswith('use_bitbucket'):
            if self.bitbucket_owner and self.bitbucket_repo:
                self.refresh_bitbucket()
                bitbucket_refreshed = True
        else:
            self.date = date

        if not github_refreshed:
            if self.github_owner and self.github_repo:
                self.refresh_github()

        if not bitbucket_refreshed:
            if self.bitbucket_owner and self.bitbucket_repo:
                self.refresh_bitbucket()

    def tz_dt(self, dt):
        return datetime.datetime(dt.year, dt.month, dt.day,
                                 dt.hour, dt.minute, dt.second,
                                 tzinfo=tzutc())

    def parse_pypi_dt(self, s):
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")

    def parse_github_dt(self, s):
        return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

    def parse_bitbucket_dt(self, s):
        return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

    def parse_dt(self, source, json_obj, key):
        if key in json_obj and json_obj[key]:
            dt_string = json_obj[key]
            if dt_string:
                if source == 'pypi':
                    dt = self.parse_pypi_dt(dt_string)
                elif source == 'github':
                    dt = self.parse_github_dt(dt_string)
                elif source == 'bitbucket':
                    dt = self.parse_bitbucket_dt(dt_string)
                if dt:
                    return dt

    def refresh_pypi(self):
        if self.pypi_url:
            json_raw = urllib2.urlopen(self.pypi_url).read()
            json_obj = json.loads(json_raw)

            if json_obj:
                if self.date_handling_choice == 'use_pypi_date':
                    if len(json_obj['urls']) > 0 and \
                            'upload_time' in json_obj['urls'][0]:
                        dt = self.parse_dt('pypi', json_obj['urls'][0], 'upload_time')
                        self.date = self.tz_dt(dt)

                if 'info' in json_obj:
                    if self.overwrite_home_page_url:
                        if 'home_page' in json_obj['info']:
                            home_page_url = json_obj['info']['home_page']
                            if home_page_url:
                                self.home_page_url = home_page_url

                    if self.overwrite_docs_url:
                        if 'docs_url' in json_obj['info']:
                            docs_url = json_obj['info']['docs_url']
                            if docs_url:
                                self.docs_url = docs_url

                    if self.overwrite_package_url:
                        if 'package_url' in json_obj['info']:
                            package_url = json_obj['info']['package_url']
                            if package_url:
                                self.package_url = package_url

                    if self.overwrite_bugtrack_url:
                        if 'bugtrack_url' in json_obj['info']:
                            bugtrack_url = json_obj['info']['bugtrack_url']
                            if bugtrack_url:
                                self.bugtrack_url = bugtrack_url

                    if self.desc_handling_choice == 'use_pypi_summary':
                        if 'summary' in json_obj['info']:
                            summary = json_obj['info']['summary']
                            if summary:
                                self.description = summary
                    elif self.desc_handling_choice == 'use_pypi_description':
                        if 'description' in json_obj['info']:
                            description = json_obj['info']['description']
                            if description:
                                self.description = description

    def refresh_github(self):
        if self.github_owner and self.github_repo:
            github_base_api_url = "https://api.github.com/repos"
            github_url = "{0}/{1}/{2}".format(github_base_api_url,
                                              self.github_owner,
                                              self.github_repo)
            json_raw = urllib2.urlopen(github_url).read()
            json_obj = json.loads(json_raw)

            dt = None

            if json_obj:
                dt = self.parse_dt('github', json_obj, 'pushed_at')
                if self.date_handling_choice == 'use_github_date':
                    if dt:
                        self.date = self.tz_dt(dt)
                if dt:
                    self.github_date = self.tz_dt(dt)

                if self.desc_handling_choice == 'use_github_description':
                    if 'description' in json_obj:
                        description = json_obj['description']
                        if description:
                            self.description = description

    def refresh_bitbucket(self):
        if self.bitbucket_owner and self.bitbucket_repo:
            bitbucket_base_api_url = "https://api.bitbucket.org/1.0/repositories"
            bitbucket_url = "{0}/{1}/{2}".format(bitbucket_base_api_url,
                                                 self.bitbucket_owner,
                                                 self.bitbucket_repo)
            json_raw = urllib2.urlopen(bitbucket_url).read()
            json_obj = json.loads(json_raw)

            dt = None

            if json_obj:
                dt = self.parse_dt('bitbucket', json_obj, 'last_updated')
                if self.date_handling_choice == 'use_bitbucket_date':
                    if dt:
                        self.date = self.tz_dt(dt)
                if dt:
                    self.bitbucket_date = self.tz_dt(dt)

                if self.desc_handling_choice == 'use_bitbucket_description':
                    if 'description' in json_obj:
                        description = json_obj['description']
                        if description:
                            self.description = description
