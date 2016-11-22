# -*- coding: utf-8 -*-
#
#   Auto sync and compile maya script
#   Author : Chia Xin Lin
#
#   1.0.01 : First development
#   1.0.11 : Add archive and test execute
#
import argparse
import py_compile
import zipfile
import tempfile
import shutil
import re
import time
import sys
import os
import os.path

_VERSION = '1.0.11'
_VERBOSE = False
_TEMPDIR = ''

_ASK_VERSION = 'Please enter archive version (*.*.** or q for quit) >'
_ARCH_OVERRIDE = 'Archive is exists, override it? ( Y / N ) >'

def _dir_exists_(folder):
    if not os.path.isdir(folder):
        msg = '{0} is not exists!'.format(folder)
        raise argparse.ArgumentError(msg)
    return folder

def _file_exists_(data):
    if not os.path.isfile(data):
        msg = '{0} is not exist!'.format(data)
        raise argparse.ArgumentError(msg)
    return data

def _read_ignore_(f):
    if not f:
        return set(), set()
    ignore_items = f.readlines()
    f.close()
    add_ignore_file = []
    add_ignore_ext = []
    for item in ignore_items:
        item = item.strip()
        if item.startswith('*.'):
            add_ignore_ext.append(item[1:])
        else:
            add_ignore_file.append(item)
    return set(add_ignore_file), set(add_ignore_ext)

def _parse_args_(command_line):
    #
    parser = argparse.ArgumentParser(
        description='Submit your Maya script package to repository')
    # Position arguments
    parser.add_argument('source', type=_dir_exists_, 
        help='Maya script source directory', metavar='Source')
    parser.add_argument('target', type=_dir_exists_, help='Target directory',
        metavar='Target')
    # Optional arguments
    # Ignore options
    parser.add_argument('-l', '--ignore-file', type=file, metavar='txt',
        help='Specific ignore list from file *.txt')
    parser.add_argument('-i', '--ignore',  type=str, nargs='+',
        help='Specific ignore files', metavar='name')
    parser.add_argument('-e', '--ignore-ext', type=str, nargs='+', 
        help='Specific ignore extensions', metavar='.*')
    parser.add_argument('-d', '--ignore-dot', action='store_true',
        help='Ignore any file or directory starts with dot')
    parser.add_argument('-u', '--ignore-underscore', action='store_true',
        help='Ignore any file or directory starts with underscore')
    parser.add_argument('-c', '--compile-py', action='store_true',
        help='Compile python script to repository')
    # Archive option
    parser.add_argument('-a', '--archive', action='store_true',
        help='Archive script to be zip file')
    # Test option
    parser.add_argument('-t', '--test', action='store_true',
        help='Just test not really submit')
    # Silent
    parser.add_argument('-s', '--silent', action='store_true',
        help='Sync with silent mode, do not confirm before process')
    # Verbose
    parser.add_argument('-b', '--no-verbose', action='store_false',
        help='Turn off the verbose output')
    # Version argument
    parser.add_argument('-v', '--version', action='version',
        version='submitMayaScript - version '+_VERSION)
    return parser.parse_args(command_line)

# Common info print, if _VERBOSE is False, will print nothing
def _info_(message, item=''):
    if _VERBOSE:
        print '\t{0} {1}.'.format(item.ljust(24, ' '), message)
    else:
        pass

# Check target file is oldest than source
def _is_new_than_(new_data, old_data):
    if not os.path.isfile(old_data):
        return True
    new_time = '%.2f'%os.path.getmtime(new_data)
    old_time = '%.2f'%os.path.getmtime(old_data)
    return float(new_time) > float(old_time)

# Obtain ignore list file and extensions
def _obtain_ignore(ignore_files, ignore_exts, ignore_list_file):
    add_ignore_files, add_ignore_ext = _read_ignore_(ignore_list_file)
    # Ignore files
    if ignore_files:
        ignore_files = set(ignore_files)
        if add_ignore_files:
            ignore_files |= add_ignore_files
        ignore_files = tuple(ignore_files)
    else:
        ignore_files = tuple(add_ignore_files)
    # Ignore extensions
    if ignore_exts:
        ignore_exts = set(ignore_exts)
        if add_ignore_ext:
            ignore_exts |= add_ignore_ext
        ignore_exts = tuple(ignore_exts)
    else:
        ignore_files = tuple(add_ignore_ext)

# Remove temporary directory
def _remove_temp(temp):
    try:
        shutil.rmtree(temp)
    except:
        sys.stderr.write('# Failed remove temporary directory...')
    else:
        print '# Remove temporary :', temp

# Obtain all files need to sync
def _find_need_(
    workspace, 
    repository, 
    with_compile_py=False,
    ignore_dot=False,
    ignore_underscore=False,
    ignore_files=[], 
    ignore_ext=[]):
    dir_len = len(workspace)
    need_items = []
    for dirPath, dirNames, fileNames in os.walk(workspace):
        if dirPath.find('.') >= 0: # ignore any directory start with dot
            continue
        for f in fileNames:
            if ignore_dot and f.startswith('.'): # // ignore start with dot
                _info_('ignore', f)
                continue
            if ignore_underscore and f.startswith('_'):
                _info_('ignore', f)
                continue
            if ignore_files and f in ignore_files: # // ignore specific file
                _info_('ignore', f)
                continue
            source_file = os.path.join(dirPath, f)
            target_file = repository + source_file[dir_len:]
            basename, ext = os.path.splitext(f) # get extension
            if ignore_ext and ext in ignore_ext:
                _info_('ignore', f)
                continue
            elif with_compile_py and ext == '.py': 
                target_file += 'c' # pyc compile
            # //
            if _is_new_than_(source_file, target_file):
                need_items.append((source_file, target_file))
            else:
                _info_('is not new than source, skip...', f)
    return need_items

def _sync_():
    global _VERBOSE, _TEMPDIR, _ASK_VERSION, _ARCH_OVERRIDE
    # Parse arguments
    args = _parse_args_(sys.argv[1:])
    # Verbose
    _VERBOSE = args.no_verbose
    # Get source and target
    workspace = args.source
    project_name = os.path.basename(workspace)
    repository = args.target
    arch_path = ''
    ignore_files = args.ignore
    ignore_exts  = args.ignore_ext
    ignore_list_file = args.ignore_file
    archive = args.archive
    test = args.test
    # list ignore file and extension from text file
    _obtain_ignore(ignore_files, ignore_exts, ignore_list_file)
    # in archive mode, make repository to temporary directory
    if archive:
        try:
            repository, arch_path = tempfile.mkdtemp(project_name), repository
            # Here preserve temp dir path
            _TEMPDIR = repository
        except:
            os.sys.stderr('# Failed when create temp directory : ' + repository)
            raise
        # Ask user what version append in archive mode
        user_input = ''
        while(not user_input or not re.match(r'\d\.\d.\d{1,2}', user_input)):
            user_input = raw_input(_ASK_VERSION)
            if user_input == 'q':
                print '# Process terminated'
                return 0
        zippath = arch_path + '/' + project_name + '_v' + user_input + '.zip'
        if os.path.isfile(zippath):
            user_input = raw_input(_ARCH_OVERRIDE)
            if user_input != 'Y':
                print '# Process terminated'
                return 0
    # Get items
    need_items = _find_need_(workspace, 
                             repository, 
                             args.compile_py,
                             args.ignore_dot, 
                             args.ignore_underscore, 
                             ignore_files, 
                             ignore_exts)
    # No any file need to sync
    if not need_items:
        print '>>> There have no any files need to sync!'
        return 0
    # Hint how many file need to sync
    print '\n>>> Sync Project : {0}, Total {1} files >>>'.format(
        project_name, len(need_items))
    # Ask user whether want to sync? skip if silent options has been set up
    if args.test:
        print '@@@ Submit test @@@'
        for source, target in need_items:
            print '# ' + source + ' -> ' + target
        print '@@@ Test end @@@'
        return 0
    # Slient mode
    if not args.silent:
        user_input = raw_input('Do you want to sync to repository? ( Y / N ) >')
        if user_input != 'Y':
            print '>>> OK, bye.'
            return 0
    # Sync process start...
    for source, target in need_items:
        # Check directory is exists, if not, create it.
        dir_name = os.path.dirname(target)
        if not os.path.isdir(dir_name): # make new directory if not exists
            os.makedirs(dir_name)
        # Do compile python script
        if target.endswith('.pyc'):
            try:
                py_compile.compile(source, target, doraise=True)
            except py_compile.PyCompileError:
                _info_('# Failed compile', target)
                raise
            else:
                shutil.copystat(source, target)
                _info_(' -> Compiled.', target)
        # Others is normal copy
        else:
            try:
                shutil.copyfile(source, target)
            except:
                _info_('# Failed copy', target)
                raise
            else:
                shutil.copystat(source, target)
                _info_(' -> Sync.', target)
    # Archive part
    if archive:
        dir_token_pos = len(repository)
        print '>>> Submit archive >>>'
        try:
            zip_object = zipfile.ZipFile(zippath, 'w')
            for target in [item[1] for item in need_items]:
                include_file = target[dir_token_pos:]
                zip_object.write(target, 
                                 include_file, 
                                 zipfile.ZIP_DEFLATED)
                _info_('# archive', include_file)
        except:
            print '# Failed archive!'
            raise
        else:
            print '# Archive successiful : ', zippath
        finally:
            zip_object.close()
    #
    return 0

if __name__=='__main__':
    _sync_()
    if _TEMPDIR:
        _remove_temp(_TEMPDIR)
