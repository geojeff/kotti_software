# -*- coding: utf-8 -*-

from pyramid.threadlocal import get_current_registry

from kotti.resources import get_root

from kotti.testing import DummyRequest
from kotti.testing import UnitTestBase
from kotti.testing import FunctionalTestBase
from kotti.testing import testing_db_url

from kotti_software import collection_settings
from kotti_software.resources import SoftwareCollection
from kotti_software.resources import SoftwareProject


class UnitTests(UnitTestBase):

    def test_software_collection(self):
        root = get_root()
        software_collection = SoftwareCollection()
        assert software_collection.type_info.addable(root, DummyRequest()) is True
        root['software_collection'] = software_collection

        software_project = SoftwareProject()

        assert len(software_collection.values()) == 0

        # there are no children of type SoftwareProject yet, the UI should present the add link
        assert software_project.type_info.addable(software_collection, DummyRequest()) is True

        software_collection['software_project'] = software_project

        assert len(software_collection.values()) == 1

    def test_software_project(self):
        root = get_root()
        software_collection = SoftwareCollection()
        root['software_collection'] = software_collection

        software_project = SoftwareProject(
                json_url="https://raw.github.com/geojeff/kotti_software/develop/json")

        software_collection['software_project'] = software_project

        assert len(software_collection.values()) == 1

    def test_software_project_json_overwriting_github(self):
        root = get_root()
        software_collection = SoftwareCollection()
        root['software_collection'] = software_collection

        software_project = SoftwareProject(
                json_url="https://raw.github.com/geojeff/kotti_software/develop/json",
                overwrite_home_page_url=True,
                overwrite_docs_url=True,
                overwrite_package_url=True,
                overwrite_bugtrack_url=True,
                desc_handling_choice='use_json_summary')

        software_collection['software_project'] = software_project

        assert len(software_collection.values()) == 1

        # desc_handling_choice is an either/or,
        # so also check for description overwriting
        software_project = SoftwareProject(
                json_url="https://raw.github.com/geojeff/kotti_software/develop/json",
                desc_handling_choice='use_json_description')

    def test_software_project_json_overwriting_pypi(self):
        root = get_root()
        software_collection = SoftwareCollection()
        root['software_collection'] = software_collection

        software_project = SoftwareProject(
                json_url="http://pypi.python.org/pypi/Kotti/json",
                overwrite_home_page_url=True,
                overwrite_docs_url=True,
                overwrite_package_url=True,
                overwrite_bugtrack_url=True,
                desc_handling_choice='use_json_summary')

        software_collection['software_project'] = software_project

        assert len(software_collection.values()) == 1

        # desc_handling_choice is an either/or,
        # so also check for description overwriting
        software_project = SoftwareProject(
                json_url="http://pypi.python.org/pypi/Kotti/json",
                desc_handling_choice='use_json_description')


class FunctionalTests(FunctionalTestBase):

    def setUp(self, **kwargs):
        self.settings = {'kotti.configurators': 'kotti_software.kotti_configure',
                         'sqlalchemy.url': testing_db_url(),
                         'kotti.secret': 'dude',
                         'kotti_software.collection_settings.pagesize': '5'}
        super(FunctionalTests, self).setUp(**self.settings)

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
