#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Name:
        WebElementDocs

    Description:
        Provides a visual UI from which to browse the accessible webelements and their documentation.
"""

import inspect
import copy
import os
import sys
import types
from subprocess import Popen

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

import GuiBuilderConfig
from WebElementDocsView import Ui_MainWindow

class WebElementDocs(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('WebElement Documentation Browser')
        self.setWindowIcon(QIcon(os.path.dirname(__file__) + '/icons/documentation.png'))

        self.genericElementIcon = QIcon(os.path.dirname(__file__) + '/icons/elements/generic.png')
        self.populateElements()
        self.ui.cancelFilter.hide()

        self.connect(self.ui.filter, SIGNAL('textChanged(const QString &)'), self.filterItemBrowser)
        self.connect(self.ui.cancelFilter, SIGNAL("clicked()"), self.clearFilter)
        self.connect(self.ui.searchResults, SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
                     self.updateDocumentation)

    def updateDocumentation(self, item, ignored):
        if not item or not item.text():
            return

        item = unicode(item.text())
        product = GuiBuilderConfig.Factory.build(item.lower(), "", "")
        if not product:
            self.ui.info.setText("")
            return

        text = "<h2>" + item + "</h2>"
        text += "<p>" + (product.__doc__ or "") + "</p>"

        text += "<p><b>signals:</b><br />" + "<br />".join(product.signals) + "</p>"

        for attributeName in dir(product):
            if attributeName.startswith("_"):
                continue

            attribute = getattr(product, attributeName, None)
            formattedName = attributeName
            try:
                argSpec = inspect.getargspec(attribute)
                parmeters = []
                for parameter in argSpec.args:
                    parmeters.append(str(parameter))
                for index, default in enumerate(reversed(argSpec.defaults or [])):
                    parmeters[-(index + 1)] += "=" + str(default)
                formattedName += "(" + ", ".join(parmeters) + ")"
            except:
                pass
            if type(attribute) in [types.FunctionType, types.MethodType] and attribute.__doc__:
                text += "<p><b>" + formattedName + "</b>" + \
                        attribute.__doc__.replace("\n", "<br />") + "</p>"

        self.ui.info.setText(text)

    def clearFilter(self):
        self.ui.filter.setText('')

    def filterItemBrowser(self, text):
        if not text:
            self.ui.cancelFilter.hide()
            return self.ui.browserView.setCurrentIndex(0)

        self.ui.browserView.setCurrentIndex(1)
        self.ui.searchResults.clear()
        for productName, product in GuiBuilderConfig.Factory.products.iteritems():
            if str(text).lower() in str(productName).lower():
                newElement = QListWidgetItem(self.elementIcon(productName.split('.')[-1]), productName)
                newElement.setToolTip(product.__doc__ or "")
                newElement.properties = {}
                self.ui.searchResults.addItem(newElement)
        self.ui.cancelFilter.show()

    def elementIcon(self, elementName):
        iconName = os.path.dirname(__file__) + "/icons/elements/" + elementName.split('.')[-1].lower() + ".png"
        if os.path.isfile(iconName):
            return QIcon(iconName)
        else:
            return self.genericElementIcon

    def populateElements(self):
        self.ui.elementsFrame.layout().removeWidget(self.ui.elements)
        self.ui.elements = QToolBox()
        self.ui.elementsFrame.layout().addWidget(self.ui.elements)

        usedProducts = []
        for data in GuiBuilderConfig.sections:
            section = data['Name']
            icon = QIcon(data['Icon'])
            factory = data['Factory']

            elementSelector = QListWidget()
            self.connect(elementSelector, SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
                     self.updateDocumentation)
            elementSelector.setIconSize(QSize(32, 32))
            elementSelector.setDragDropMode(elementSelector.DragOnly)
            for productName, product in factory.products.iteritems():
                if productName in usedProducts:
                    continue
                else:
                    usedProducts.append(productName)

                newElement = QListWidgetItem(self.elementIcon(productName), productName)
                newElement.setToolTip(product.__doc__ or "")
                newElement.properties = {}
                elementSelector.addItem(newElement)

            self.ui.elements.addItem(elementSelector, icon, section)


def run():
    app = QApplication(sys.argv)

    window = WebElementDocs()
    window.resize(900, 700)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
