from pyramid.threadlocal import get_current_registry

from kotti.testing import FunctionalTestBase
from kotti.testing import testing_db_url

from kotti_software import collection_settings


class TestSoftwareCollection(FunctionalTestBase):

    def setUp(self, **kwargs):
        self.settings = {'kotti.configurators': 'kotti_software.kotti_configure',
                         'sqlalchemy.url': testing_db_url(),
                         'kotti.secret': 'dude',
                         'kotti_software.collection_settings.pagesize': '5'}
        super(TestSoftwareCollection, self).setUp(**self.settings)

    def test_asset_overrides(self):
        from kotti import main
        self.settings['kotti_software.asset_overrides'] = 'kotti_software:hello_world/'
        main({}, **self.settings)

    def test_softwarecollection_default_settings(self):
        b_settings = collection_settings()
        assert b_settings['use_batching'] == True
        assert b_settings['pagesize'] == 5
        assert b_settings['use_auto_batching'] == True
        assert b_settings['link_headline_overview'] == True

    def test_softwarecollection_change_settings(self):
        settings = get_current_registry().settings
        settings['kotti_software.collection_settings.use_batching'] = u'false'
        settings['kotti_software.collection_settings.pagesize'] = u'2'
        settings['kotti_software.collection_settings.use_auto_batching'] = u'false'
        settings['kotti_software.collection_settings.link_headline_overview'] = u'false'

        b_settings = collection_settings()
        assert b_settings['use_batching'] == False
        assert b_settings['pagesize'] == 2
        assert b_settings['use_auto_batching'] == False
        assert b_settings['link_headline_overview'] == False

    def test_softwarecollection_wrong_settings(self):
        settings = get_current_registry().settings
        settings['kotti_software.collection_settings.use_batching'] = u'blibs'
        settings['kotti_software.collection_settings.pagesize'] = u'blabs'
        settings['kotti_software.collection_settings.use_auto_batching'] = u'blubs'
        settings['kotti_software.collection_settings.link_headline_overview'] = u'blobs'

        b_settings = collection_settings()
        assert b_settings['use_batching'] == False
        assert b_settings['pagesize'] == 5
        assert b_settings['use_auto_batching'] == False
        assert b_settings['link_headline_overview'] == False
