from setuptools import setup, find_packages
import os

version = '0.1.2'

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
tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-xdist',
    'WebTest',
    'wsgi_intercept',
    'zope.testbrowser',
]

long_description = README + '\n\n' + TODO + '\n\n' + AUTHORS + '\n\n' + CHANGES

setup(name='kotti_software',
      version=version,
      description="Kotti software -- adds a software project listing to your site",
      long_description=long_description,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Pyramid',
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
          'Kotti>=0.7',
          'plone.batching',
          'AccessControl',  # this is actually a dependency of plone.batching
          'js.jquery_infinite_ajax_scroll',
          'js.jquery_form',
          'python-dateutil',
      ],
      project_points="""
      [fanstatic.libraries]
      kotti_software = kotti_software:library
      """,
      tests_require=tests_require,
      extras_require={
          'testing': tests_require,
          'development': development_requires,
          },
      message_extractors={'kotti_software': [
            ('**.py', 'lingua_python', None),
            ('**.zcml', 'lingua_xml', None),
            ('**.pt', 'lingua_xml', None),
            ]},
      )
