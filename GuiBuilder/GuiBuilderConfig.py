# -*- coding: utf-8 -*-
'''
    GuiBuilderConfig.py

    Defines the configuration parameters used by GuiBuilder

    Copyright (C) 2013  Timothy Edmund Crosley

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import os
import glob

import WebElements.All as WebElements

sharedFilesRoot = os.environ.get("GUI_BUILDER_SHARED_FILES_ROOT",
                                 (os.path.dirname(__file__) or ".") + "/static/")
onSave = os.environ.get("GUI_BUILDER_ON_SAVE", None)
indent = " "

WebElements.Fields.Factory.products.pop('field', None)
sections = ({'Name':'Layout',
             'Factory':WebElements.Layout.Factory,
             'Icon':'icons/sections/layout.png'},
            {'Name':'Document',
             'Factory':WebElements.Document.Factory,
             'Icon':'icons/sections/document.png'},
            {'Name':'Display',
             'Factory':WebElements.Display.Factory,
             'Icon':'icons/sections/display.png'},
            {'Name':'Buttons',
             'Factory':WebElements.Buttons.Factory,
             'Icon':'icons/sections/buttons.png'},
            {'Name':'Fields',
             'Factory':WebElements.Fields.Factory,
             'Icon':'icons/sections/fields.png'},
            {'Name':'Inputs',
             'Factory':WebElements.Inputs.Factory,
             'Icon':'icons/sections/inputs.png'},
            {'Name':'HiddenInputs',
             'Factory':WebElements.HiddenInputs.Factory,
             'Icon':'icons/sections/hiddeninputs.png'},
            {'Name':'Navigation',
             'Factory':WebElements.Navigation.Factory,
             'Icon':'icons/sections/navigation.png'},
            {'Name':'Resources',
             'Factory':WebElements.Resources.Factory,
             'Icon':'icons/sections/resources.png'},
            {'Name':'Containers',
             'Factory':WebElements.Containers.Factory,
             'Icon':'icons/sections/containers.png'},
            {'Name':'DataViews',
             'Factory':WebElements.DataViews.Factory,
             'Icon':'icons/sections/dataviews.png'},
            {'Name':'Charts',
             'Factory':WebElements.Charts.Factory,
             'Icon':'icons/sections/charts.png'},
            {'Name':'Printing',
             'Factory':WebElements.Printing.Factory,
             'Icon':'icons/sections/printing.png'},
            {'Name':'CodeDocumentation',
             'Factory':WebElements.CodeDocumentation.Factory,
             'Icon':'icons/sections/documentation.png'},
            {'Name':'DOM',
             'Factory':WebElements.DOM.Factory,
             'Icon':'icons/sections/dom.png'},
           )

factories = [WebElements.Factory]

javascriptFiles = glob.glob(sharedFilesRoot + "**/*.js")
cssFiles = glob.glob(sharedFilesRoot + "**/*.css")

Factory = WebElements.FactoryClasses.Composite(factories)
WebElements.Display.Factory.addProduct(WebElements.Base.Invalid)

