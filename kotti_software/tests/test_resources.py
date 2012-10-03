# -*- coding: utf-8 -*-

from kotti.resources import get_root
from kotti.testing import DummyRequest
from kotti.testing import UnitTestBase
from kotti_software.resources import SoftwareCollection
from kotti_software.resources import SoftwareProject


class ResourcesTests(UnitTestBase):

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
