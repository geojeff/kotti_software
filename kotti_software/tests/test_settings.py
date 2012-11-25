# -*- coding: utf-8 -*-

from kotti.testing import UnitTestBase


class SettingsTest(UnitTestBase):

    def test(self):

        settings = {
            'kotti.includes': '',
            'kotti.available_types': '',
            'pyramid.includes': '',
        }

        import kotti_software

        kotti_software.kotti_configure(settings)

        # make sure all the types are available
        assert settings['kotti.available_types'].find('kotti_software.resources.SoftwareCollection') > 0
        assert settings['kotti.available_types'].find('kotti_software.resources.SoftwareProject') > 0

        # make sure all inccludes are available
        assert settings['pyramid.includes'].find('kotti_software.views') > 0
