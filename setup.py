#!/usr/bin/env python

from distutils.core import setup

setup(name='GuiBuilder',
      version='0.1',
      description='Python Distribution Utilities',
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='http://www.webelements.in/',
      download_url='https://github.com/timothycrosley/GuiBuilder/blob/master/dist/GuiBuilder-0.1.tar.gz?raw=true',
      license = "GNU GPLv2",
      scripts=['scripts/guiBuilder', 'scripts/webElementDocs'],
      requires = ['webelements', 'pyqt',],
      package_data={'GuiBuilder': ['icons/*.png', '*.css', 'icons/elements/*.png',
                                   'icons/sections/*.png', 'static/images/*.png',
                                   'static/images/popupcal/*.gif',
                                   'static/js/*.js', 'static/stylesheets/*.css']},
      include_package_data=True,
      packages=['GuiBuilder',],)
