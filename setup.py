from setuptools import setup, find_packages
import os

version = '0.1.4'

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''
try:
    TODO = open(os.path.join(here, 'TODO.txt')).read()
except IOError:
    TODO = ''
try:
    AUTHORS = open(os.path.join(here, 'AUTHORS.txt')).read()
except IOError:
    AUTHORS = ''
try:
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    CHANGES = ''

development_requires = [
    'minify',
]

long_description = README + '\n\n' + TODO + '\n\n' + AUTHORS + '\n\n' + CHANGES

setup(name='kotti_software',
      version=version,
      description="Adds a software project listing to your Kotti site",
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Framework :: Pylons',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'License :: Repoze Public License',
      ],
      keywords='kotti software',
      author='Jeff Pittman',
      author_email='geojeff@me.com',
      url='http://github.com/geojeff/kotti_software',
      bugtrack_url='https://github.com/geojeff/kotti_software/issues',
      license=' BSD-derived (http://www.repoze.org/LICENSE.txt)',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Kotti>=0.8a1',
          'plone.batching',
          'AccessControl',  # this is actually a dependency of plone.batching
          'js.jquery_infinite_ajax_scroll',
          'js.jquery_form',
          'python-dateutil',
      ],
      project_points="""
      [fanstatic.libraries]
      kotti_software = kotti_software.fanstatic:library
      """,
      extras_require={},
      message_extractors={'kotti_software': [
            ('**.py', 'lingua_python', None),
            ('**.zcml', 'lingua_xml', None),
            ('**.pt', 'lingua_xml', None),
            ]},
      )
