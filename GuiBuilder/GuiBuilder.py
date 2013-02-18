#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
    GuiBuilder.py

    Provides a visual UI from which to build WebElement templates.

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

import copy
import inspect
import os
import sys
import types
import WebElements.All as WebElements
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *
from subprocess import Popen
from WebElements import shpaml, UITemplate
from WebElements.DictUtils import OrderedDict
from WebElements.MultiplePythonSupport import *
from WebElements.Base import TextNode

import GuiBuilderConfig
from GuiBuilderConfig import indent
from GuiBuilderView import Ui_MainWindow
from itertools import chain
from Session import Session

sharedFilesRoot = QUrl.fromLocalFile(GuiBuilderConfig.sharedFilesRoot)


class TextEditDialog(QDialog):

    def __init__(self, parent=None, currentText=""):
        super(TextEditDialog, self).__init__(parent)

        self.oldText = currentText
        self.edit = QTextEdit(currentText)
        self.button = QPushButton("Save")
        self.button.setObjectName("saveProperty")

        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.button.clicked.connect(self.success)
        self.edit.setFocus()

    def success(self):
        return self.done(QDialog.Accepted)

    @classmethod
    def getText(cls, parentDisplay, currentText=""):
        dialog = cls(parentDisplay, currentText)
        if not dialog.exec_() == QDialog.Accepted:
            return dialog.oldText
        return dialog.edit.toPlainText().replace("\n", "<br/>")


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
            self.extendedEdit = self.createExtendedEdit()
            self.extendedEdit.setObjectName("extendedEdit")
            self.extendedEdit.setMaximumWidth(20)
            self.extendedEdit.setMinimumWidth(20)


        def createExtendedEdit(self):
            result = QLabel()
            if self.propertyType == "string":
                result = QPushButton("...")

                self.connect(result, SIGNAL("clicked()"), self.updateText)
            return result

        def updateText(self):
            self.widget.setText(TextEditDialog.getText(self.builder, self.widget.text()))

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
        self.lastSaved = ""

        self.connect(self.ui.newTemplate, SIGNAL('clicked()'), self.newTemplate)
        self.connect(self.ui.backToStartPage, SIGNAL('clicked()'), self.backToStartPage)
        self.connect(self.ui.wuiXML, SIGNAL("textChanged()"), self.updatePreview)
        self.connect(self.ui.wuiSHPAML, SIGNAL("textChanged()"), self.updateXML)
        self.connect(self.ui.open, SIGNAL("clicked()"), self.open)
        self.connect(self.ui.save, SIGNAL("clicked()"), self.save)
        self.connect(self.ui.saveAs, SIGNAL("clicked()"), self.saveAs)
        self.connect(self.ui.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
                     self.updateDocumentation)
        self.connect(self.ui.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
                     self.updateProperties)
        self.connect(self.ui.tree, SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),
                     self.refreshPreviewKeepTree)
        self.connect(self.ui.expand, SIGNAL("clicked()"), self.ui.tree.expandAll)
        self.connect(self.ui.collapse, SIGNAL("clicked()"), self.ui.tree.collapseAll)
        self.connect(self.ui.reload, SIGNAL("clicked()"), self.reloadEverything)
        self.connect(self.ui.filter, SIGNAL('textChanged(const QString &)'), self.filterItemBrowser)
        self.connect(self.ui.filterProperties, SIGNAL('textChanged(const QString &)'), self.filterProperties)
        self.connect(self.ui.filterTree, SIGNAL('textChanged(const QString &)'), self.filterTree)
        self.connect(self.ui.cancelFilter, SIGNAL("clicked()"), self.clearFilter)
        self.connect(self.ui.cancelPropertyFilter, SIGNAL("clicked()"), self.clearPropertyFilter)
        self.connect(self.ui.cancelTreeFilter, SIGNAL("clicked()"), self.clearTreeFilter)
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
            self.resizeTreeColumns()
            return to_return

        def treeDropMimeData(parent, index, data, action):
            success =  QTreeWidget.dropMimeData(self.ui.tree, parent, index, data, action)
            if success:
                if parent:
                    if index > 0:
                        self.selectedKey = int(parent.child(index-1).text(4)) + 1
                    else:
                        self.selectedKey = int(parent.text(4)) + 1
                else:
                    if index == 0:
                        self.selectedKey = 0
                    else:
                        self.selectedKey = int(self.ui.tree.topLevelItem(index-1).text(4)) + 1
            return success

        def keyPressOverride(evt):
            if evt.key() == Qt.Key_Delete:
                self.deleteFromTree()

            QTreeWidget.keyPressEvent(self.ui.tree, evt)

        self.ui.tree.dropEvent = treeDropEvent
        self.ui.tree.dropMimeData = treeDropMimeData
        self.ui.tree.keyPressEvent = keyPressOverride
        self.ui.tree.setHeaderHidden(False)
        self.ui.continueEditing.hide()
        self.populateRecentlyOpened()

        self.ui.cancelFilter.hide()
        self.ui.cancelPropertyFilter.hide()
        self.ui.cancelTreeFilter.hide()

    def resizeTreeColumns(self):
        for column in xrange(4):
            self.ui.tree.resizeColumnToContents(column)

    def selectElement(self, selected):
        try:
            int(selected)
        except:
            return
        self.ui.tree.setCurrentItem(self.ui.tree.findItems(selected, Qt.MatchExactly | Qt.MatchRecursive, 4)[0])

    def startDocBrowser(self):
        Popen("webElementDocs", cwd=os.path.expanduser('~'))

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

    def clearPropertyFilter(self):
        self.ui.filterProperties.setText('')
        self.ui.filterProperties.setFocus()

    def clearTreeFilter(self):
        self.ui.filterTree.setText('')
        self.ui.filterTree.setFocus()

    def filterItemBrowser(self, text):
        if not text:
            self.ui.cancelFilter.hide()
            return self.ui.browserView.setCurrentIndex(0)

        self.ui.browserView.setCurrentIndex(1)
        self.ui.searchResults.clear()
        for productName, product in iteritems(GuiBuilderConfig.Factory.products):
            if str(text).lower() in str(productName).lower():
                newElement = QListWidgetItem(self.elementIcon(productName), productName)
                newElement.setToolTip(product.__doc__ or "")
                newElement.properties = {}
                self.ui.searchResults.addItem(newElement)
        self.ui.cancelFilter.show()

    def filterProperties(self, text):
        if not text:
            self.ui.cancelPropertyFilter.hide()
            for row in xrange(self.ui.properties.rowCount()):
                self.ui.properties.setRowHidden(row, False)
        else:
            for row in xrange(self.ui.properties.rowCount()):
                self.ui.cancelPropertyFilter.show()
                self.ui.properties.setRowHidden(row, True)
                for col in xrange(self.ui.properties.columnCount()):
                    item = self.ui.properties.cellWidget(row, col)
                    if item:
                        if text.lower() in item.text().lower():
                            self.ui.properties.setRowHidden(row, False)

        self.resetPropertyLayout()

    def filterTree(self, text):
        if not text:
            self.ui.cancelTreeFilter.hide()
            iterator = QTreeWidgetItemIterator(self.ui.tree)
            while iterator.value():
                item = iterator.value()
                iterator += 1
                item.setHidden(False)
        else:
            iterator = QTreeWidgetItemIterator(self.ui.tree)
            while iterator.value():
                item = iterator.value()
                iterator += 1
                item.setHidden(True)
                for column in xrange(5):
                    if text.lower() in item.text(column).lower():
                        item.setHidden(False)
                        parent = item.parent()
                        while parent:
                            parent.setHidden(False)
                            parent = parent.parent()

    def deleteFromTree(self):
        selectedItems = self.ui.tree.selectedItems()
        if not selectedItems:
            return

        answer = QMessageBox.question(self, 'Are you sure you want to delete elements?',
                                      "Are you sure you want to delete " + str(len(selectedItems)) +
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
                    if topLevelItem:
                        if topLevelItem.text(4) == item.text(4):
                            self.ui.tree.takeTopLevelItem(topLevelItemIndex)

        self.unselectCurrentElement()
        self.convertTreeToTemplate()

    def unselectCurrentElement(self):
        self.selectedKey = None
        self.currentItem = None
        self.ui.properties.clear()
        self.ui.info.setText("")

    def updateXML(self):
        self.ui.wuiXML.setText(shpaml.convert_text(self.ui.wuiSHPAML.toPlainText()))
        self.updateSaveIndicator()

    def convertTreeToTemplate(self):
        baseTag = str(self.ui.baseLayout.currentText()).lower()
        childCount = self.ui.tree.topLevelItemCount()
        template = [(childCount == 0 and "> " or "") + baseTag + "\n"]
        for topLevelItemIndex in xrange(childCount):
            template.append(str(self.__templateFromTreeNode(self.ui.tree.topLevelItem(topLevelItemIndex))))

        template = ''.join(template)
        existing = self.ui.wuiSHPAML.toPlainText().strip()
        new = template.strip()
        if existing != new:
            position = self.ui.wuiSHPAML.textCursor().position()
            self.ui.wuiSHPAML.setText(template)
            cursor = self.ui.wuiSHPAML.textCursor()
            cursor.setPosition(position - (len(existing) - len(new)))
            self.ui.wuiSHPAML.setTextCursor(cursor)

    def __templateFromTreeNode(self, node, indentationLevel=1):
        indentation = (indent * indentationLevel) or ""
        childCount = node.childCount()
        if node.text(0) == "label":
            node.properties = self.propertyMap.get(unicode(node.text(4)), {'text':'Label'})
        else:
            node.properties = self.propertyMap.get(unicode(node.text(4)), {})

        if node.text(0) == "textnode":
            xml = indentation + node.properties.get('text', '')
            return xml

        xml = indentation + (childCount == 0 and "> " or "") + node.text(0)
        accessor = node.properties.get('accessor', None)
        if accessor:
            xml += "@" + accessor
        nodeID = node.properties.get('id', None)
        if nodeID:
            xml += "#" + nodeID
        classes = node.properties.get('class', None)
        if classes:
            for nodeClass in classes.split(' '):
                xml += "." + nodeClass
        for propertyName, propertyValue in iteritems(node.properties):
            if not propertyValue or propertyName in ('class', 'id', 'accessor'):
                continue

            propertyValue = unicode(propertyValue).replace("&amp;", "&").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if not " " in propertyValue and not '"' in propertyValue:
                xml += " " + unicode(propertyName) + '=' + propertyValue
            else:
                xml += " " + unicode(propertyName) + '="' + propertyValue + '"'

        xml += "\n"

        for childIndex in range(0, childCount):
            childNode = node.child(childIndex)
            xml += self.__templateFromTreeNode(childNode, indentationLevel + 1)

        return xml

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
        baseLayout = self.structure.create or 'flow'
        for index in xrange(self.ui.baseLayout.count()):
            self.ui.baseLayout.setCurrentIndex(index)
            if self.ui.baseLayout.currentText() == baseLayout:
                break
        self.connect(self.ui.baseLayout, SIGNAL("currentIndexChanged(const QString &)"), self.convertTreeToTemplate)

        for childElement in self.structure.childElements:
            self.__convertDictToNode(childElement, self.ui.tree)
        self.ui.tree.expandAll()
        self.resizeTreeColumns()
        if self.ui.tree.currentIndex():
            self.ui.tree.scrollTo(self.ui.tree.currentIndex())

        self.updateSaveIndicator()

    def updateSaveIndicator(self):
        if self.currentFile and self.lastSaved != self.ui.wuiSHPAML.toPlainText():
            self.ui.save.setEnabled(True)
        else:
            self.ui.save.setEnabled(False)

    def __convertDictToNode(self, structure, node):
        if type(structure) in (str, unicode):
            structure = UITemplate.Template('textnode', properties=(('text', structure),))

        create = structure.create
        if not create:
            return

        newNode = QTreeWidgetItem(node)
        newNode.setText(0, create)
        newNode.setIcon(0, self.elementIcon(create))
        newNode.setText(1, structure.id)
        newNode.setText(2, structure.name)
        newNode.setText(3, structure.accessor)
        newNode.setText(4, self.newElementKey())
        self.resizeTreeColumns()
        if self.selectedKey != None:
            if int(newNode.text(4)) == int(self.selectedKey):
                newNode.setSelected(True)
                self.ui.tree.setCurrentItem(newNode)
                self.ui.tree.scrollTo(self.ui.tree.currentIndex())

        childElements = structure.childElements or ()
        propertyDict = dict(structure.properties)
        propertyDict.update({'id':structure.id, 'name':structure.name, 'accessor':structure.accessor})
        self.propertyMap[unicode(newNode.text(4))] = propertyDict

        for childElement in childElements:
            self.__convertDictToNode(childElement, newNode)

    def elementIcon(self, elementName):
        iconName = "icons/elements/" + elementName.split('-')[-1].lower() + ".png"
        if os.path.isfile(iconName):
            return QIcon(iconName)
        else:
            return self.genericElementIcon

    def newTemplate(self):
        self.setCurrentFile(None)
        self.ui.wuiXML.setText('<flow>\n</flow>')
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
        if fileName and fileName[0]:
            self.setFile(fileName[0])

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

        self.ui.wuiSHPAML.setText(template)
        self.lastSaved = template
        self.setCurrentFile(fileName)

        self.gotoEditPage()

    def save(self):
        if not self.currentFile:
            self.saveAs()

        template = self.ui.wuiSHPAML.toPlainText()
        with open(self.currentFile, 'w') as wuiFile:
            wuiFile.write(template)

        self.lastSaved = template
        self.updateSaveIndicator()

        if GuiBuilderConfig.onSave:
            Popen(GuiBuilderConfig.onSave, shell=True)

    def saveAs(self):
        fileName = QFileDialog.getSaveFileName(self, "Save to WUI(WebElement User Interface) file",
                                            self.getLastOpenedDirectory(), "Files (*.wui);;All Files (*)")
        if not fileName:
            return

        fileName = fileName[0]
        if not ".wui" in fileName:
            fileName = fileName + ".wui"

        self.setCurrentFile(fileName)
        self.save()

    def html(self, elementHtml):
        document = WebElements.Document.Document()
        for resourceFile in chain(GuiBuilderConfig.javascriptFiles, GuiBuilderConfig.cssFiles):
            document += WebElements.Resources.ResourceFile(file=resourceFile)
        document += WebElements.Display.StraightHTML(html=elementHtml)

        return document.toHTML()

    def reloadEverything(self):
        self.refreshPreview()

    def refreshPreview(self):
        self.oldTemplate = None
        self.updatePreview()

    def refreshPreviewKeepTree(self):
        self.oldTemplate = None
        self.updatePreview(False)

    def highlightSelected(self, uiStructure, index=0, inTab=None, inStack=None, setStack=False):
        setStackNextLoop = False
        for nestedIndex, element in enumerate((element for element in uiStructure.childElements or ()
                                              if type(element) not in (str, unicode))):
            elementType = element.create.lower()
            element.properties = dict(element.properties)
            properties = element.properties
            properties.setdefault('javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                     (index, properties.get('onclick', '')))
            if 'field' in elementType:
                properties.setdefault('userInput.javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                             (index, properties.get('onclick', '')))
                properties.setdefault('label.javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                             (index, properties.get('onclick', '')))
            elif elementType in ('tab', 'containers-tab'):
                inTab = element
                properties.setdefault('tabLabel.javascriptEvents', {})['onclick'] = ("document.title = '%s';%s" %
                                                                             (index, properties.get('onclick', '')))
            elif elementType in ('stack', 'layout-stack'):
                inStack = [element, None]
                setStackNextLoop = True
            elif setStack:
                inStack[1] = nestedIndex

            if index == int(self.selectedKey or -1):
                if 'field' in elementType:
                    properties['labelStyle'] = "border:2px blue dashed;" + properties.get('labelStyle', '')

                if elementType in ('tab', 'containers-tab'):
                    properties['select'] = True
                elif inTab:
                    inTab.properties['select'] = True
                elif inStack and inStack[1]:
                    inStack[0].properties['index'] = inStack[1]
                properties['style'] = "border:2px blue dashed;" + properties.get('style', '')
            index += 1
            index = self.highlightSelected(element, index, inTab, inStack, setStackNextLoop)
        return index

    def updatePreview(self, redrawTree=True):
        if not self.ui.wuiXML.toPlainText() or self.ui.wuiXML.toPlainText() == self.oldTemplate:
            return

        self.oldTemplate = self.ui.wuiXML.toPlainText()
        try:
            self.structure = UITemplate.fromXML(unicode(self.ui.wuiXML.toPlainText()))
            validTemplate = True
        except Exception:
            validTemplate = False
            print("There was an error converting the template to structure")

        if validTemplate:
            structureCopy = copy.deepcopy(self.structure)
            self.highlightSelected(structureCopy)
            element = GuiBuilderConfig.Factory.buildFromTemplate(structureCopy)
            scriptContainer = GuiBuilderConfig.Factory.build('ScriptContainer')
            element.setScriptContainer(scriptContainer)
            element.addChildElement(scriptContainer)
            self.ui.preview.setHtml(self.html(element.toHTML()), sharedFilesRoot)
            if redrawTree:
                self.updateTree()
                self.disconnect(self.ui.wuiSHPAML, SIGNAL("textChanged()"), self.updateXML)
                self.convertTreeToTemplate()
                self.connect(self.ui.wuiSHPAML, SIGNAL("textChanged()"), self.updateXML)

        self.updateSaveIndicator()

    def updateProperties(self, item, ignored):
        if not item or item.text(4) == self.selectedKey:
            return
        if not item.text(4):
            item.setText(4, self.newElementKey())

        self.currentItem = item
        self.selectedKey = item.text(4)

        self.ui.properties.clear()
        self.ui.properties.setColumnCount(3)
        self.ui.properties.setHorizontalHeaderLabels(['Name', 'Value', ''])

        elementName = unicode(item.text(0)).lower()
        if elementName == "textnode":
            properties = {'text':{}}
        else:
            properties = OrderedDict()
            properties['accessor'] = {}
            properties['id'] = {}
            properties['name'] = {}
            properties['create'] = {}
            element = GuiBuilderConfig.Factory.products[elementName]
            properties.update(element.properties)

        self.ui.properties.setRowCount(len(properties))
        for propertyIndex, propertyData in enumerate(iteritems(properties)):
            (propertyName, propertyDict) = propertyData
            propertyType = propertyDict.get('type', "string")

            label = QLabel()
            label.setText(propertyName[0].upper() + propertyName[1:] + ": ")
            label.setToolTip(propertyDict.get('info', label.text()))
            self.ui.properties.setCellWidget(propertyIndex,  0, label)

            controller = PropertyController(unicode(item.text(4)), propertyName, propertyType, self)
            self.ui.properties.setCellWidget(propertyIndex, 1, controller.widget)
            self.ui.properties.setCellWidget(propertyIndex, 2, controller.extendedEdit)

            self.propertyControls[propertyName] = controller

        filterText = self.ui.filterProperties.text()
        if filterText:
            self.filterProperties(filterText)
        else:
            self.resetPropertyLayout()

    def resetPropertyLayout(self):
        self.ui.properties.setColumnWidth(0, 120)
        self.ui.properties.setColumnWidth(1, 140)
        self.ui.properties.setColumnWidth(2, 20)
        self.ui.properties.resizeRowsToContents()

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
            for productName, product in iteritems(factory.products):
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
    openFile = ""
    if len(sys.argv) > 1:
        openFile = os.path.abspath(sys.argv[1])
    os.chdir(os.path.dirname(__file__) or ".")
    app = QApplication(sys.argv)
    with open("GuiBuilder.css") as cssFile:
        app.setStyleSheet(cssFile.read())
    window = GuiBuilder()
    if openFile:
        window.setFile(openFile)
    window.resize(1024, 768)
    window.show()


    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
