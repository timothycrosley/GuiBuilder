#!/usr/bin/env python

from distutils.core import setup

setup(name='GuiBuilder',
      version='0.5.2',
      description='A drag and drop interface to create WebElement UI templates quickly and easily.',
      author='Timothy Crosley',
      author_email='timothy.crosley@gmail.com',
      url='http://www.guibuilder.net/',
      download_url='https://github.com/timothycrosley/GuiBuilder/blob/master/dist/GuiBuilder-0.5.2.tar.gz?raw=true',
      license = "GNU GPLv2",
      scripts=['scripts/guiBuilder', 'scripts/webElementDocs'],
      requires=['webelements'], # Technically requires pyside but native install of this is preferred
      install_requires=['webelements>=1.0.0-alpha.6'],
      package_data={'GuiBuilder': ['icons/*.png', '*.css', 'icons/elements/*.png',
                                   'icons/sections/*.png', 'static/images/*.png',
                                   'static/images/popupcal/*.gif',
                                   'static/js/*.js', 'static/stylesheets/*.css']},
      include_package_data=True,
      packages=['GuiBuilder',],)
