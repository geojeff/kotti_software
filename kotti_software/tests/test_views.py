# -*- coding: utf-8 -*-

import os
import kotti
from kotti.resources import get_root
from kotti.testing import DummyRequest
from kotti.testing import UnitTestBase
from kotti_software.resources import SoftwareCollection
from kotti_software.resources import SoftwareProject
from kotti_software.views import SoftwareProjectView
from kotti_software.views import SoftwareCollectionView

here = os.path.abspath(os.path.dirname(__file__))


class ViewsTests(UnitTestBase):

    def test_softwareproject_view(self):

        root = get_root()
        softwareproject = root['softwareproject'] = SoftwareProject()

        view = SoftwareProjectView(softwareproject, DummyRequest()).view()

        assert view is not None

    def test_softwarecollection_view(self):

        root = get_root()
        softwareproject = root['softwareproject'] = SoftwareProject()
        view = SoftwareCollectionView(root, DummyRequest()).view()

        assert softwareproject is not None

        assert view is not None

        assert ('items' in view) and (len(view['items']) == 1)

        assert ('api' in view) \
                and (type(view['api']) is kotti.views.util.TemplateAPI)

        assert ('settings' in view) \
                 and ('use_batching' in view['settings']) \
                 and (view['settings']['use_batching'] is True)
        assert ('settings' in view) \
                and ('pagesize' in view['settings']) \
                and (view['settings']['pagesize'] == 5)
        assert ('settings' in view) \
                and ('use_auto_batching' in view['settings']) \
                and (view['settings']['use_auto_batching'] is True)
        assert ('settings' in view) \
                and ('link_headline_overview' in view['settings']) \
                and (view['settings']['link_headline_overview'] is True)

        softwarecollection = root['softwarecollection'] = SoftwareCollection()
        view = SoftwareCollectionView(root['softwarecollection'],
                                      DummyRequest()).view()

        assert view is not None

        assert ('items' in view) and (len(view['items']) == 0)

        assert ('settings' in view) \
                 and ('use_batching' in view['settings']) \
                 and (view['settings']['use_batching'] is True)
        assert ('settings' in view) \
                and ('pagesize' in view['settings']) \
                and (view['settings']['pagesize'] == 5)
        assert ('settings' in view) \
                and ('use_auto_batching' in view['settings']) \
                and (view['settings']['use_auto_batching'] is True)
        assert ('settings' in view) \
                and ('link_headline_overview' in view['settings']) \
                and (view['settings']['link_headline_overview'] is True)
        assert (('settings' in view) \
                 and ('use_batching' in view['settings']) \
                 and (view['settings']['use_batching'] is True))
