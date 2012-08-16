#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Name:
        GuiBuilder

    Description:
        Provides a visual UI from which to build WebElement templates.

    Lost? For Extensive and up-to-date documentation on GuiBuilder point your browser to:
        http://wiki.arincdirect.net/bin/view/Adc/GuiBuilder
"""
import inspect
import copy
import os
import sys
import types
from subprocess import Popen

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import GuiBuilderConfig
from WebElements.DictUtils import OrderedDict
from GuiBuilderConfig import indent
from GuiBuilderView import Ui_MainWindow
from Session import Session
from WebElements import UITemplate

sharedFilesRoot = QUrl.fromLocalFile(GuiBuilderConfig.sharedFilesRoot)


class PropertyController(QObject):

        typeMap = {'int':QSpinBox,
                   'float':QDoubleSpinBox,
                   'bool':QCheckBox,
                   'string':QLineEdit}
        defaultType = QLineEdit

        def __init__(self, elementKey, propertyName, propertyType, builder):
            QObject.__init__(self)
            self.elementKey = elementKey
            self.propertyName = propertyName
            self.propertyType = propertyType
            self.builder = builder
            self.widget = self.createWidget()

        def createWidget(self):
            value = self.builder.propertyMap[self.elementKey].get(self.propertyName, None)

            widget = self.typeMap.get(self.propertyType, self.defaultType)()
            if self.propertyType in ["int", "float"]:
                widget.setMaximum(99999)
                widget.setValue(int(value or 0))
                self.connect(widget, SIGNAL("valueChanged(const QString &)"), self.setValue)
            elif self.propertyType == "bool":
                if value:
                    widget.toggle()
                self.connect(widget, SIGNAL("toggled(bool)"), self.setValue)
            else:
                widget.setText(unicode(value or ''))
                self.connect(widget, SIGNAL("textChanged(const QString &)"), self.setValue)

            return widget

        def setValue(self, value):
            self.builder.propertyMap[self.elementKey][self.propertyName] = unicode(value or "")
            self.builder.convertTreeToTemplate()


class GuiBuilder(QMainWindow):
    session = Session(os.path.expanduser('~') + "/.GuiBuilderSession")

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.preview.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
        self.ui.preview.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.ui.preview.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        self.ui.preview.settings().setAttribute(QWebSettings.AutoLoadImages, True)

        self.setWindowTitle('WebElement UITemplate Builder')
        self.setWindowIcon(QIcon('icons/icon.png'))
        self.setCurrentFile(None)
        self.genericElementIcon = QIcon('icons/elements/generic.png')
        self.oldTemplate = ""
        self.populateElements()
        self.propertyMap = {}
        self.currentElementKey = 0
        self.selectedKey = None
        self.propertyControls = {}

        self.connect(self.ui.newTemplate, SIGNAL('clicked()'), self.newTemplate)
        self.connect(self.ui.backToStartPage, SIGNAL('clicked()'), self.backToStartPage)
        self.connect(self.ui.wuiTemplate, SIGNAL("textChanged()"), self.updatePreview)
        self.connect(self.ui.open, SIGNAL("clicked()"), self.open)
        self.connect(self.ui.save, SIGNAL("clicked()"), self.save)
        self.connect(self.ui.saveAs, SIGNAL("clicked()"), self.saveAs)
        self.connect(self.ui.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
                     self.updateDocumentation)
        self.connect(self.ui.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
                     self.updateProperties)
        self.connect(self.ui.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
                     self.refreshPreviewKeepTree)
        self.connect(self.ui.rearrange, SIGNAL("toggled(bool)"), self.changeTreeDragDropMode)
        self.connect(self.ui.expand, SIGNAL("clicked()"), self.ui.tree.expandAll)
        self.connect(self.ui.collapse, SIGNAL("clicked()"), self.ui.tree.collapseAll)
        self.connect(self.ui.deleteFromTree, SIGNAL("clicked()"), self.deleteFromTree)
        self.connect(self.ui.newPage, SIGNAL("clicked()"), self.createPage)
        self.connect(self.ui.reload, SIGNAL("clicked()"), self.reloadEverything)
        self.connect(self.ui.filter, SIGNAL('textChanged(const QString &)'), self.filterItemBrowser)
        self.connect(self.ui.cancelFilter, SIGNAL("clicked()"), self.clearFilter)
        self.connect(self.ui.continueEditing, SIGNAL("clicked()"), self.gotoEditPage)
        self.connect(self.ui.baseLayout, SIGNAL("currentIndexChanged(const QString &)"), self.convertTreeToTemplate)
        self.connect(self.ui.recentlyOpened, SIGNAL("currentIndexChanged(const QString &)"), self.openRecent)
        self.connect(self.ui.preview, SIGNAL("titleChanged(const QString &)"), self.selectElement)
        self.connect(self.ui.documentation, SIGNAL("clicked()"), self.startDocBrowser)

        def treeDropEvent(event):
            to_return = QTreeWidget.dropEvent(self.ui.tree, event)
            self.convertTreeToTemplate()
            self.ui.filter.selectAll()
            self.ui.filter.setFocus()
            return to_return

        self.ui.tree.dropEvent = treeDropEvent
        self.ui.tree.setHeaderHidden(False)
        self.ui.continueEditing.hide()
        self.populateRecentlyOpened()

    def selectElement(self, selected):
        try:
            int(selected)
        except:
            return
        self.ui.tree.setCurrentItem(self.ui.tree.findItems(selected, Qt.MatchExactly | Qt.MatchRecursive, 4)[0])

    def createPage(self):
        Popen("instantlyGUI", shell=True)
        sys.exit(1)

    def startDocBrowser(self):
        Popen("webElementDocs", shell=True)

    def populateRecentlyOpened(self):
        recentlyOpened = self.session.get('recentlyOpenedFiles', [])
        if not recentlyOpened:
            self.ui.recentlyOpened.hide()
            return

        self.ui.recentlyOpened.clear()
        for fileName in ['Open Recent...'] + recentlyOpened:
            self.ui.recentlyOpened.addItem(fileName)

        self.ui.recentlyOpened.setCurrentIndex(0)

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

    def deleteFromTree(self):
        selectedItems = self.ui.tree.selectedItems()
        if not selectedItems:
            return

        answer = QMessageBox.question(self, 'Are you sure you want to delete elements?',
                                      "Are you susre you want to delete " + str(len(selectedItems)) +
                                      " element(s)?", QMessageBox.Yes | QMessageBox.No)
        if not answer == QMessageBox.Yes:
            return

        for item in selectedItems:
            parent = item.parent()
            if parent:
                parent.removeChild(item)
            else:
                for topLevelItemIndex in xrange(self.ui.tree.topLevelItemCount()):
                    topLevelItem = self.ui.tree.topLevelItem(topLevelItemIndex)
                    if topLevelItem == item:
                        self.ui.tree.takeTopLevelItem(topLevelItemIndex)

        self.unselectCurrentElement()
        self.convertTreeToTemplate()

    def unselectCurrentElement(self):
        self.selectedKey = None
        self.currentItem = None
        self.ui.properties.clear()
        self.ui.info.setText("")

    def convertTreeToTemplate(self):
        baseTag = str(self.ui.baseLayout.currentText()).lower()
        template = ['<' + baseTag + '>']
        for topLevelItemIndex in xrange(self.ui.tree.topLevelItemCount()):
            template.append(str(self.__templateFromTreeNode(self.ui.tree.topLevelItem(topLevelItemIndex))))

        template.append('</' + baseTag + '>')
        self.ui.wuiTemplate.setText(QString(''.join(template)))

    def __templateFromTreeNode(self, node, indentationLevel=0):
        indentation = (indent * indentationLevel) or ""
        xml = indentation + "<" + node.text(0)
        if node.text(0) == "label":
            node.properties = self.propertyMap.get(unicode(node.text(4)), {'text':'Label'})
        else:
            node.properties = self.propertyMap.get(unicode(node.text(4)), {})
        for propertyName, propertyValue in node.properties.iteritems():
            if not propertyValue:
                continue

            propertyValue = unicode(propertyValue).replace("&amp;", "&").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            xml += " " + unicode(propertyName) + '="' + propertyValue + '"'

        xml += ">\n"

        for childIndex in range(0, node.childCount()):
            childNode = node.child(childIndex)
            xml += self.__templateFromTreeNode(childNode, indentationLevel + 1)

        xml += indentation + "</" + node.text(0) + ">\n"
        return xml

    def changeTreeDragDropMode(self, internalOnly=False):
        if internalOnly:
            self.ui.tree.setDragDropMode(QAbstractItemView.InternalMove);
        else:
            self.ui.tree.setDragDropMode(QAbstractItemView.DropOnly);

    def gotoEditPage(self):
        self.ui.pages.setCurrentIndex(1)
        self.ui.cancelFilter.hide()
        self.ui.filter.setFocus()
        self.ui.continueEditing.show()

    def setCurrentFile(self, currentFile):
        self.currentFile = currentFile
        if currentFile:
            self.setWindowTitle('WebElement UITemplate Builder - ' + currentFile)
            self.ui.save.setEnabled(True)
            self.ui.continueEditing.setText("Continue Editing '%s'  >" % currentFile)
            self.updateRecent(currentFile)
        else:
            self.setWindowTitle('WebElement UITemplate Builder')
            self.ui.continueEditing.setText("Continue Editing Unsaved Template  >")
            self.ui.save.setEnabled(False)

    def newElementKey(self):
        returnValue = unicode(self.currentElementKey)
        self.currentElementKey += 1
        self.propertyMap[returnValue] = {}
        return returnValue

    def updateTree(self):
        self.propertyMap = {}
        self.currentElementKey = 0
        self.ui.tree.clear()

        self.disconnect(self.ui.baseLayout, SIGNAL("currentIndexChanged(const QString &)"), self.convertTreeToTemplate)
        baseLayout = self.structure.get('create', 'flow')
        for index in xrange(self.ui.baseLayout.count()):
            self.ui.baseLayout.setCurrentIndex(index)
            if self.ui.baseLayout.currentText() == baseLayout:
                break
        self.connect(self.ui.baseLayout, SIGNAL("currentIndexChanged(const QString &)"), self.convertTreeToTemplate)

        for childElement in self.structure.get('childElements', []):
            self.__convertDictToNode(childElement, self.ui.tree)
        self.ui.tree.expandAll()

    def __convertDictToNode(self, structure, node):
        create = structure.pop('create', None)
        if not create:
            return

        newNode = QTreeWidgetItem(node)
        newNode.setText(0, create)
        newNode.setIcon(0, self.elementIcon(create))
        newNode.setText(1, structure.get('id', ''))
        newNode.setText(2, structure.get('name', ''))
        newNode.setText(3, structure.get('accessor', ''))
        newNode.setText(4, self.newElementKey())
        if self.selectedKey != None:
            if newNode.text(4) == self.selectedKey:
                newNode.setSelected(True)
                self.ui.tree.setCurrentItem(newNode)
                self.ui.tree.scrollTo(self.ui.tree.currentIndex())

        childElements = structure.pop('childElements', [])
        self.propertyMap[unicode(newNode.text(4))] = structure

        for childElement in childElements:
            self.__convertDictToNode(childElement, newNode)

    def elementIcon(self, elementName):
        iconName = "icons/elements/" + elementName.split('.')[-1].lower() + ".png"
        if os.path.isfile(iconName):
            return QIcon(iconName)
        else:
            return self.genericElementIcon

    def newTemplate(self):
        self.setCurrentFile(None)
        self.ui.wuiTemplate.setText('<flow>\n</flow>')
        self.gotoEditPage()

    def backToStartPage(self):
        self.ui.pages.setCurrentIndex(0)

    def openRecent(self, fileName):
        fileName = str(fileName)
        if fileName and fileName != "Open Recent...":
            self.setFile(fileName)

    def getLastOpenedDirectory(self):
        openAt = QDir.homePath()
        lastOpenedDirectory = self.session.get('lastOpenedDirectory', openAt)
        if os.path.exists(lastOpenedDirectory):
            openAt = lastOpenedDirectory

        return openAt

    def open(self):
        fileName = QFileDialog.getOpenFileName(self, "Open WUI(WebElement User Interface) file",
                                               self.getLastOpenedDirectory(), "Files (*.wui);;All Files (*)");
        if fileName:
            self.setFile(fileName)

    def updateRecent(self, fileName):
        self.session['lastOpenedDirectory'] = os.path.dirname(str(fileName))
        recent = self.session.setdefault('recentlyOpenedFiles', [])
        if fileName in recent:
            recent.remove(fileName)

        recent.insert(0, fileName)
        while len(recent) > 20:
            recent.pop()

        self.populateRecentlyOpened()
        self.session.save()

    def setFile(self, fileName):
        templateFile = open(fileName, 'r')
        template = templateFile.read()
        templateFile.close()

        self.ui.wuiTemplate.setText(template)
        self.setCurrentFile(fileName)

        self.gotoEditPage()

    def save(self):
        if not self.currentFile:
            self.saveAs()

        with open(self.currentFile, 'w') as wuiFile:
            wuiFile.write(self.ui.wuiTemplate.toPlainText())
        Popen("webkit", shell=True)

    def saveAs(self):
        fileName = QFileDialog.getSaveFileName(self, "Save to WUI(WebElement User Interface) file",
                                            self.getLastOpenedDirectory(), "Files (*.wui);;All Files (*)")
        if not fileName:
            return

        if not ".wui" in fileName:
            fileName = fileName + ".wui"

        self.setCurrentFile(fileName)
        self.ui.save.setEnabled(True)
        self.save()

    def html(self, elementHtml):
        html = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">'
        html += "<html>"
        html += "<head>"
        for javascript in GuiBuilderConfig.javascriptFiles:
            html += '<script langauge="javascript" src="' + javascript + '"></script>'
        for css in GuiBuilderConfig.cssFiles:
            html += '<link rel="stylesheet" href="' + css + '" type="text/css" />'
        html += "</head>"
        html += "<body>"
        html += elementHtml
        html += "</body>"
        html += "</html>"

        return html

    def reloadEverything(self):
        self.refreshPreview()

    def refreshPreview(self):
        self.oldTemplate = None
        self.updatePreview()

    def refreshPreviewKeepTree(self):
        self.oldTemplate = None
        self.updatePreview(False)

    def highlightSelected(self, uiDict, index=0, inTab=None):
        for element in uiDict.get('childElements', []):
            elementType = element['create'].lower()
            element.setdefault('javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                     (index, element.get('onclick', '')))
            if 'field' in elementType:
                element.setdefault('userInput.javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                                   (index, element.get('onclick', '')))
                element.setdefault('label.javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                               (index, element.get('onclick', '')))
            elif 'tab' == elementType:
                inTab = element
                element.setdefault('tabLabel.javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                               (index, element.get('onclick', '')))
            if index == int(self.selectedKey or -1):
                if 'field' in elementType:
                    element['labelStyle'] = "border:2px blue dashed;" + element.get('labelStyle', '')

                if 'tab' == elementType:
                    element['select'] = True
                elif inTab:
                    inTab['select'] = True
                element['style'] = "border:2px blue dashed;" + element.get('style', '')
            index += 1
            index = self.highlightSelected(element, index, inTab)
            element

        return index

    def updatePreview(self, redrawTree=True):
        if not self.ui.wuiTemplate.toPlainText() or self.ui.wuiTemplate.toPlainText() == self.oldTemplate:
            return

        self.oldTemplate = self.ui.wuiTemplate.toPlainText()
        try:
            self.structure = UITemplate.fromXML(unicode(self.ui.wuiTemplate.toPlainText()))
            validTemplate = True
        except Exception, e:
            validTemplate = False
            print "There was an error converting the template to structure: " + unicode(e)

        if validTemplate:
	    print "Reloading"
            structureCopy = copy.deepcopy(self.structure)
            self.highlightSelected(structureCopy)
            element = GuiBuilderConfig.Factory.buildFromDictionary(structureCopy)
            scriptContainer = GuiBuilderConfig.Factory.build('ScriptContainer')
            element.setScriptContainer(scriptContainer)
            element.addChildElement(scriptContainer)
            print self.html(element.toHtml())
            self.ui.preview.setHtml(self.html(element.toHtml()), sharedFilesRoot)
            if redrawTree:
                self.updateTree()

    def updateProperties(self, item, ignored):
        if not item or item.text(4) == self.selectedKey:
            return
        if not item.text(4):
            item.setText(4, self.newElementKey())

        self.currentItem = item
        self.selectedKey = item.text(4)

        self.ui.properties.clear()
        self.ui.properties.setColumnCount(2)
        self.ui.properties.setHorizontalHeaderLabels(['Name', 'Value'])

        elementName = unicode(item.text(0)).lower()
        element = GuiBuilderConfig.Factory.products[elementName]

        properties = OrderedDict()
        properties['accessor'] = {}
        properties['id'] = {}
        properties['name'] = {}
        properties['create'] = {}
        properties.update(element.properties)

        self.ui.properties.setRowCount(len(properties))
        for propertyIndex, propertyName, propertyDict in properties.iteritemsWithIndex():
            propertyType = propertyDict.get('type', "string")

            label = QLabel()
            label.setText(propertyName[0].upper() + propertyName[1:] + ": ")
            self.ui.properties.setCellWidget(propertyIndex,  0, label)

            controller = PropertyController(unicode(item.text(4)), propertyName, propertyType, self)
            self.ui.properties.setCellWidget(propertyIndex, 1, controller.widget)
            self.propertyControls[propertyName] = controller

    def updateDocumentation(self, item, ignored):
        if not item or item.text(4) == self.selectedKey:
            return

        item = unicode(item.text(0))
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

            attribute = product.__getattribute__(attributeName)
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
    styleSheetFile = open("GuiBuilder.css", "r")
    styleSheet = styleSheetFile.read()
    styleSheetFile.close()

    app = QApplication(sys.argv)
    app.setStyleSheet(styleSheet)

    window = GuiBuilder()
    if len(sys.argv) > 1:
        window.setFile(sys.argv[1])
    window.resize(1024, 768)
    window.show()


    sys.exit(app.exec_())

            
if __name__ == "__main__":
    run()
