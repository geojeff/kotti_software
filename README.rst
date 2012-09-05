==============
kotti_software
==============

This is an extension to the Kotti CMS that adds a system for presenting
software projects on your site.

kotti_software started as a copy of kotti_blog.

`Find out more about Kotti`_

Setting up kotti_software
=========================

This Addon adds two new Content Types to your Kotti site.
To set up the content types add ``kotti_software.kotti_configure``
to the ``kotti.configurators`` setting in your ini file::

    kotti.configurators = kotti_software.kotti_configure

Now you can create a software collection and add software projects.

There are different settings to adjust the behavior of the
software.

You can select if the software projects in the collection overview
should be batched. If you set 
``kotti_software.collection_settings.use_batching`` to ``true``
(the default value) the software projects will be shown on separate
pages. If you set it to ``false`` all software projects are shown
all together on one page::

    kotti_software.collection_settings.use_batching = false

If you use batching you can choose how many software projects are
shown on one page. The default value for 
``kotti_software.collection_settings.pagesize`` is 5::

    kotti_software.collection_settings.pagesize = 10

You can use auto batching where the next page of the software projects
is automatically loaded when scrolling down the overview page instead
of showing links to switch the pages. The default for
``kotti_software.collection_settings.use_auto_batching`` is ``true``::

    kotti_software.collection_settings.use_auto_batching = false

With ``kotti_software.collection_settings.link_headline_overview`` you
can control whether the headline of a software project in the
collection overview is linked to the software project or not. This
setting defaults to ``true``::

    kotti_software.collection_settings.link_headline_overview = false

Parts of kotti_software can be overridden with the setting
``kotti_software.asset_overrides``. Have a look to the 
`Kotti documentation about the asset_overrides setting`_, which is the
same as in ``kotti_software``.

Be warned: This addon is in alpha state. Use it at your own risk.

.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
.. _Kotti documentation about the asset_overrides setting: http://kotti.readthedocs.org/en/latest/configuration.html?highlight=asset#adjust-the-look-feel-kotti-asset-overrides

