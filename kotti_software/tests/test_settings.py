# -*- coding: utf-8 -*-


def test_settings(db_session):

    settings = {
        'kotti.includes': '',
        'kotti.available_types': '',
        'pyramid.includes': '',
    }

    from kotti import main

    settings = {'kotti.configurators': 'kotti_software.kotti_configure'}
    main({}, **settings)

    # make sure all the types are available
    assert settings['kotti.available_types'].find('kotti_software.resources.SoftwareCollection') > 0
    assert settings['kotti.available_types'].find('kotti_software.resources.SoftwareProject') > 0

    # make sure all inccludes are available
    assert settings['pyramid.includes'].find('kotti_software.views') > 0
