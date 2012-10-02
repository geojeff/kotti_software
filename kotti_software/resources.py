import datetime
import json
import urllib2
from dateutil.tz import tzutc

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import types

from zope.interface import implements

from kotti.resources import IDocument
from kotti.resources import IDefaultWorkflow
from kotti.resources import Document

from kotti.views.util import format_date

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

    type_info = Document.type_info.copy(
        name=u'SoftwareCollection',
        title=_(u'SoftwareCollection'),
        add_view=u'add_softwarecollection',
        addable_to=[u'Document'],
        )


class SoftwareProject(Document):
    implements(IDocument, IDefaultWorkflow)

    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)

    description_handling_choice = 'use_entered'
    #  other choices: ('use_json_summary', 'use_json_description')

    json_url = Column('json_url', String())

    date = Column('date', UTCDateTime())
    date_handling_choice = 'use_json_date'
    #  other choices: ('use_entered', 'use_now')

    home_page_url = Column('home_page_url', String())
    docs_url = Column('docs_url', String())
    package_url = Column('package_url', String())
    bugtrack_url = Column('bugtrack_url', String())

    overwrite_home_page_url = Column('overwrite_home_page_url', Boolean())
    overwrite_docs_url = Column('overwrite_docs_url', Boolean())
    overwrite_package_url = Column('overwrite_package_url', Boolean())
    overwrite_bugtrack_url = Column('overwrite_bugtrack_url', Boolean())

    type_info = Document.type_info.copy(
        name=u'Software project',
        title=_(u'Software project'),
        add_view=u'add_softwareproject',
        addable_to=[u'SoftwareCollection'],
        )

    def __init__(self,
                 description_handling_choice='use_entered',
                 json_url='', 
                 date=None,
                 date_handling_choice='use_json_date',
                 home_page_url='',
                 docs_url='',
                 package_url='',
                 bugtrack_url='',
                 overwrite_home_page_url=True,
                 overwrite_docs_url=True,
                 overwrite_package_url=True,
                 overwrite_bugtrack_url=True,
                 **kwargs):
        super(SoftwareProject, self).__init__(**kwargs)

        self.description_handling_choice = description_handling_choice

        self.json_url = json_url

        # The choices for date_handling_choice are:
        #
        #   use_json_date
        #   use_entered
        #   use_now
        #
        # Logic:
        #
        #   if use_json_date, use it, regardless of incoming date value
        #   else set the date (the date view default system will make it NOW
        #     if date is None)
        #
        if self.json_url:
            self.refresh_json()
        else:
            self.date = date

        self.date_handling_choice = date_handling_choice

        self.home_page_url = home_page_url
        self.docs_url = docs_url
        self.package_url = package_url
        self.bugtrack_url = bugtrack_url
        self.overwrite_home_page_url = overwrite_home_page_url
        self.overwrite_docs_url = overwrite_docs_url
        self.overwrite_package_url = overwrite_package_url
        self.overwrite_bugtrack_url = overwrite_bugtrack_url

    def refresh_json(self):
        print 'refresh_json'
        if self.json_url:
            json_raw = urllib2.urlopen(self.json_url).read()
            json_obj = json.loads(json_raw)

            print 'refresh_json', 'json_url', self.json_url
            if json_obj:
                print 'refresh_json', 'json_obj', json_obj
                if self.date_handling_choice == 'use_json_date':
                    if len(json_obj['urls']) > 0 and \
                            'upload_time' in json_obj['urls'][0]:
                        upload_time_string = \
                                json_obj['urls'][0]['upload_time']
                        if upload_time_string:
                            upload_time = \
                                datetime.datetime.strptime(upload_time_string,
                                                           "%Y-%m-%dT%H:%M:%S")
                            self.date = \
                                datetime.datetime(upload_time.year,
                                                  upload_time.month,
                                                  upload_time.day,
                                                  upload_time.hour,
                                                  upload_time.minute,
                                                  upload_time.second,
                                                  upload_time.microsecond,
                                                  tzinfo=tzutc())
                            self.formatted_date = format_date(self.date)

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

                    if self.description_handling_choice == 'use_json_summary':
                        if 'summary' in json_obj['info']:
                            summary = json_obj['info']['summary']
                            if summary:
                                self.description = summary
                    elif self.description_handling_choice == 'use_json_description':
                        if 'description' in json_obj['info']:
                            description = json_obj['info']['description']
                            if description:
                                self.description = description
