# -*- coding: utf-8 -*-
import sys
import datetime
import os
import os.path

_AUTHOR = 'Chia Xin Lin'
_YEAR = '2016'
_EMAIL = 'nnnight@gmail.com'
_GITHUB = 'http://github.com/chiaxin'
_DATE = datetime.datetime.strftime(datetime.datetime.now(), '%Y/%m/%d')
_PROJECT_NAME = raw_input('# Please enter the project name (q for Quit) > ')
if _PROJECT_NAME == 'q':
    sys.exit(0)
_UI_TYPE = raw_input('# PySide UI type : [1] Dialog [2] MainWindow [3] uic >')
if _UI_TYPE not in ('1', '2', '3'):
    sys.exit(0)
_CAPTAL_PROJ_NAME = _PROJECT_NAME[0].capitalize() + _PROJECT_NAME[1:]
#

_HEAD = '''# -*- coding: utf-8 -*-
# {0}
#
# Made by {1}, Copyright (c) {2} by {1}
# 
# E-Mail : {3}
#
# Github : {4}
#
# Licensed under MIT : http://opensource.org/licenses/MIT
'''.format(_PROJECT_NAME, _AUTHOR, _YEAR, _EMAIL, _GITHUB)

_LOG = '''SCRIPT NAME : {0}
FIRST UPDATE : {1}
LAST UPDATE : {1}
VERSION : 0.0.01 beta
'''.format(_PROJECT_NAME, _DATE)

_README = '''# {0}
# How to install

Copy the scripts and prefs folder into Maya script path,
Default path should be C:\%USERNAME%\document\maya\%MAYA_VERSION%
and restart your Maya application, enter below commands in python command :

import {0}
reload({0})

If success, will open the {0} window

# Maya Support
'''.format(_PROJECT_NAME)

_GITIGNORE = '''*.pyc
*.swp
'''

_INIT_CORE = '''import maya.cmds as mc

# script end
'''

_INIT_INIT = '''import ui
try:
    {0}UI.close()
except:
    {0}UI = ui.{1}Win()
{0}UI.show()

# init end
'''.format(_PROJECT_NAME, _CAPTAL_PROJ_NAME)

_UI_HEAD = '''from shiboken import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as mc
from core import *

VERSION = 'v0.0.01 beta'

def _getMayaMainWindow():
    pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtGui.QWidget)

'''

_INIT_UI_MAINWIN = 'from PySide import QtCore, QtGui\n' + _UI_HEAD + \
'''
class {0}Win(QtGui.QMainWindow):
    global VERSION
    def __init__(self, parent=_getMayaMainWindow()):
        super({0}Win, self).__init__(parent)
        self.setWindowTitle('{1} ' + VERSION)
        self.setObjectName({1}Win')
        self.initUI()

    def initUI(self):
        self.setCentralWidget(self.makeCentralWin())

    def makeCentralWin(self):
        self.centralWin = QtGui.QWidget()
        return self.centralWin
# Script end
'''.format(_CAPTAL_PROJ_NAME, _PROJECT_NAME)

_INIT_UI_DIALOG = 'from PySide import QtCore, QtGui\n' + _UI_HEAD + \
'''
class {0}Win(QtGui.QDialog):
    global VERSION
    def __init__(self, parent=_getMayaMainWindow()):
        super({0}Win, self).__init__(parent)
        self.setWindowTitle('{1} ' + VERSION)
        self.setObjectName('{1}Win')
        self.initUI()

    def initUI(self):
        pass

# Script end
'''.format(_CAPTAL_PROJ_NAME, _PROJECT_NAME)

_INIT_UI_UIC = 'from PySide import QtGui, QtCore, QtUiTools' + _UI_HEAD + \
'''
class {0}Win(QtGui.QDialog):
    global VERSION
    _uic_ = '{1}UIC.uic'
    def __init__(self, parent=_getMayaMainWindow()):
        super({0}Win, self).__init__(parent)
        self.setWindowTitle('{1} ' + VERSION)
        self.setObjectName('{1}Win')
        self.initUI()

    def initUI(self):
        loader = QtUiTools.QUiLoader()
        ouif = QtCore.QFile()
        ouif.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(self._uic_, parentWidget=self)
        ouif.close()

# Script end
'''.format(_CAPTAL_PROJ_NAME, _PROJECT_NAME)

_LICENSE = '''The MIT License (MIT)

Copyright (c) {0} {1}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''.format(_YEAR, _AUTHOR)

def _makeLog(p):
    try:
        fs = open(p, 'w')
    except IOError:
        sys.stderr.write('Failed in write file :' + p)
    else:
        fs.write(_LOG)
    finally:
        fs.close()

def _makeLicense(p):
    try:
        fs = open(p, 'w')
    except IOError:
        sys.stderr.write('Failed in write file :' + p)
    else:
        fs.write(_LICENSE)
    finally:
        fs.close()

def _makeReadme(p):
    try:
        fs = open(p, 'w')
    except IOError:
        sys.stderr.write('Failed in write file :' + p)
    else:
        fs.write(_README)
    finally:
        fs.close()

def _makeGitignore(p):
    try:
        fs = open(p, 'w')
    except IOError:
        sys.stderr.write('Failed in write file :' + p)
    else:
        fs.write(_GITIGNORE)
    finally:
        fs.close()

def _makeScriptInit(p):
    try:
        fs = open(p, 'w')
    except IOError:
        sys.stderr.write('Failed in write file :' + p)
    else:
        fs.write(_HEAD)
        fs.write(_INIT_INIT)
    finally:
        fs.close()

def _makeScriptCore(p):
    try:
        fs = open(p, 'w')
    except IOError:
        sys.stderr.write('Failed in write file :' + p)
    else:
        fs.write(_HEAD)
        fs.write(_INIT_CORE)
    finally:
        fs.close()

def _makeScriptUi(p):
    global _UI_TYPE
    try:
        fs = open(p, 'w')
    except IOError:
        sys.stderr.write('Failed in write file :' + p)
    else:
        fs.write(_HEAD)
        if _UI_TYPE == '1':
            fs.write(_INIT_UI_DIALOG)
        elif _UI_TYPE == '2':
            fs.write(_INIT_UI_MAINWIN)
        elif _UI_TYPE == '3':
            fs.write(_INIT_UI_UIC)
    finally:
        fs.close()

def main():
    workspace_dir = os.path.join(os.getcwd(), _PROJECT_NAME)
    if os.path.isdir(workspace_dir):
        print '# Project is exists !'
        return -1
    provide_file = [os.path.join(workspace_dir, f) \
        for f in ('LOG', 'LICENSE', 'README.md', '.gitignore')]
    make_functions= [_makeLog, _makeLicense, _makeReadme, _makeGitignore]
    script_dir = os.path.join(workspace_dir, 'scripts/' + _PROJECT_NAME)
    prefs_dir = os.path.join(workspace_dir, 'perfs/icons')
    provide_file.append(os.path.join(script_dir, '__init__.py'))
    make_functions.append(_makeScriptInit)
    provide_file.append(os.path.join(script_dir, 'core.py'))
    make_functions.append(_makeScriptCore)
    provide_file.append(os.path.join(script_dir, 'ui.py'))
    make_functions.append(_makeScriptUi)
    provide_file.append(prefs_dir)
    provide_file = map(lambda p: p.replace('\\', '/'), provide_file)
    print '\t# Below files will be create :'
    print '\n'.join(map(lambda p: '\t' + p, provide_file))
    user_input = raw_input('\tDo you want to continue? ( Y / N ) >')
    if user_input != 'Y':
        return 0
    for idx, data in enumerate(provide_file):
        parent_dir = os.path.dirname(data)
        if not os.path.isdir(parent_dir):
            os.makedirs(parent_dir)
            print '\t# Create directory : ' + parent_dir
        if idx < len(make_functions):
            make_functions[idx](data)
            print '\t# Write file successiful : ' + data
    print '\t# Create project finish #'

if __name__=='__main__':
    main()
