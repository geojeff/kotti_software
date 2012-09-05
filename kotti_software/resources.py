import datetime
import urllib2
import json
from dateutil.tz import tzutc
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    types,
)
from kotti.resources import Document
from kotti_software import _
from kotti.views.util import format_date


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
    id = Column('id', Integer, ForeignKey('documents.id'), primary_key=True)

    type_info = Document.type_info.copy(
        name=u'SoftwareCollection',
        title=_(u'SoftwareCollection'),
        add_view=u'add_softwarecollection',
        addable_to=[u'Document'],
        )


class SoftwareProject(Document):
    id = Column(Integer, ForeignKey('documents.id'), primary_key=True)
    date = Column('date', UTCDateTime())
    json_url = Column('json_url', String())

    type_info = Document.type_info.copy(
        name=u'Software project',
        title=_(u'Software project'),
        add_view=u'add_softwareproject',
        addable_to=[u'SoftwareCollection'],
        )

    def __init__(self, date=None, json_url='', **kwargs):
        super(SoftwareProject, self).__init__(**kwargs)
        self.date = date
        self.json_url = json_url
        if self.date is None:
            self.refresh_date()

    def refresh_date(self):
        if self.json_url:
            json_raw = urllib2.urlopen(self.json_url).read()
            json_obj = json.loads(json_raw)

            if json_obj and len(json_obj['urls']) > 0 and \
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
