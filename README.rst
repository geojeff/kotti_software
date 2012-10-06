==============
kotti_software
==============

This is an extension to the Kotti CMS that adds a system for presenting
a list of software projects on your site.

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

Using kotti_software
====================

Add a software collection to your site, then to that add software projects.
For software projects, you can provide a date, which you will need to
manually keep up to date. Or, you can provide a json_url instead of a date
and the last-updated date for the project, along with main urls, will be
gathered from a JSON source. Here are ways to enter software projects:

    1) Enter the JSON url only (for fetching from a JSON data source)

    2) Enter the date and any of: home_page, docs_url,
       package_url, bugtrack_url (manual entry)

    3) Enter the date only (bare-bones entry, with just date and
       title, and whatever is in body -- useful for defunct
       projects)

There is a date-handling select property that should be set according to the
action for 1), 2), or 3) above: 'Use entered date', 'Use date in JSON data',
or 'Use the current date'.

There is a similar select property for how to handle the description. Choices
for that are: 'Used entered description (can be blank)', 'Use summary in JSON data',
or 'Use description in JSON data'.

For the JSON data, if your project is a Python project and it has been posted
to pypi.python.org, you can enter the JSON url for that, as described below.
Otherwise, make your own JSON file, using the following format, and post it
somewhere, then enter that URL. See instructions below about 'raw' data links.

::

    {
        "info": {
            "home_page": "http://kotti.pylonsproject.org",
            "docs_url": "http://packages.python.org/Kotti", 
            "package_url": "http://pypi.python.org/pypi/Kotti", 
            "bugtrack_url": "", 
            "description": "Kotti is a high-level, 'Pythonic' framework..."
            "summary": "Kotti is a high-level, 'Pythonic' framework..."
        }, 
        "urls": [ { "upload_time": "2012-08-30T11:59:58", } ]
    }

The home_page, docs_url, package_url, and bugtrack_url urls are key/value pairs
within "info", not within "urls" as you might expect. Within the "urls" data
structure is upload_time, an arrangement that might appear unnecessarily
complicated. It is this way because we follow the pypi JSON structure. kotti_software
is written for use on the Kotti website, which mostly presents Python projects that
are posted on pypi. Also, kotti_software is used by Kotti developers on their
personal websites, which also tend to have Python projects. However, any type of
project can be posted, for javascript, Ruby, etc. Just follow the data structure
format above for creating a custom JSON data structure for each project.


**Instructions for common JSON sources:**

pypi
----

Enter the url of the form "http://pypi.python.org/pypi/{project name}/json",
where {project name} is the case-sensitive name of the project on pypi. For
example, for Kotti the url is "http://pypi.python.org/pypi/Kotti/json".

See http://pypi.python.org/pypi/Kotti/json to see the JSON that is parsed.

Hosting Elsewhere
-----------------

As an alternative to pypi, if your project is not posted there, you may put
a JSON file somewhere in your github, bitbucket, or other repo, and access
it with an appropriate url. For instance, for a file in a github repo, the
RAW url should be used, e.g.:

json_url = "https://raw.github.com/geojeff/kotti_fruits_example/master/json"

As described above, you will need to follow the format of the pypi JSON data
in such a file.

Work in progress
================

``kotti_software`` is considered alpha software, not yet suitable for use in
production environments.  The current state of the project is in no way feature
complete nor API stable.  If you really want to use it in your project(s), make
sure to pin the exact version in your requirements.  Not doing so will likely
break your project when future releases become available.

Development
===========

Contributions to ``kotti_software`` are very welcome.
Just clone its `Github repository`_ and submit your contributions as pull requests.

Note that all development is done on the ``develop`` branch. ``master`` is reserved
for "production-ready state".  Therefore, make sure to always base development work
on the current state of the ``develop`` branch.

This follows the highly recommended `A successful Git branching model`_ pattern,
which is implemented by the excellent `gitflow`_ git extension.

Testing
-------

|build status|_

``kotti_software`` has 100% test coverage.
Please make sure that you add tests for new features and that all tests pass before
submitting pull requests.  Running the test suite is as easy as running ``py.test``
from the source directory (you might need to run ``python setup.py dev`` to have all
the test requirements installed in your virtualenv).


.. _Find out more about Kotti: http://pypi.python.org/pypi/Kotti
.. _Kotti documentation about the asset_overrides setting: http://kotti.readthedocs.org/en/latest/configuration.html?highlight=asset#adjust-the-look-feel-kotti-asset-overrides
.. _Github repository: https://github.com/geojeff/kotti_software
.. _gitflow: https://github.com/nvie/gitflow
.. _A successful Git branching model: http://nvie.com/posts/a-successful-git-branching-model/
.. |build status| image:: https://secure.travis-ci.org/geojeff/kotti_software.png?branch=master
.. _build status: http://travis-ci.org/geojeff/kotti_software
