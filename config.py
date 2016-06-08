#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os
import configparser


def readschemelist():
    config = configparser.ConfigParser()
    if not os.path.exists('backup.ini'):
        return ''
    else:
        config.read('backup.ini')
        sectionslist = config.sections()
        sectionslist.remove('SELECT')
        return sectionslist


def readbackup(current_scheme=None):
    config = configparser.ConfigParser()
    if not os.path.exists('backup.ini'):
        return ('','','','')
    else:
        try:
            if current_scheme == '':
                return ('','','','')
            config.read('backup.ini')
            if not current_scheme:
                current_scheme = config.get('SELECT', 'current_scheme')
            server_ip = config.get(current_scheme, 'server_ip')
            server_port = config.get(current_scheme, 'server_port')
            qs_id = config.get(current_scheme, 'qs_id')
            return (current_scheme, server_ip, server_port, qs_id)
        except configparser.NoSectionError:
            return ('','','','')


def writebackup(current_scheme=None, server_ip=None, server_port=None, qs_id=None):
    config = configparser.ConfigParser()
    config.read('backup.ini')
    if not os.path.exists('backup.ini'):
        config.add_section('SELECT')
    config.set('SELECT', 'current_scheme', current_scheme)
    if not config.has_section(current_scheme):
        config.add_section(current_scheme)
    config.set(current_scheme, 'server_ip', server_ip)
    config.set(current_scheme, 'server_port', server_port)
    config.set(current_scheme, 'qs_id', qs_id)    
    config.write(open('backup.ini', 'w'))
    
    
def deletebackup(current_scheme, prev_scheme):
    config = configparser.ConfigParser()
    config.read('backup.ini')
    if os.path.exists('backup.ini') and config.has_section(current_scheme):
        config.set('SELECT', 'current_scheme', prev_scheme)        
        config.remove_section(current_scheme)
        config.write(open('backup.ini', 'w'))
        return True
    else:
        return False
    
    
def readfunc(config_file, section, option=None):
    commset = ['1016','1030','1207','1203','1032','1005','1205']
    config = configparser.ConfigParser()
    try:
        config.read('dictionary\\' + config_file + '.ini')
        if option == None:
            return config.items(section)
        if option in commset:
            return config.get('commset', option)
        else:
            return config.get(section, option)
    except:
        return ''
    
    
def writefunc(config_file, section, option, value=''):
    commset = ['1016','1030','1207','1203','1032','1005','1205']
    config = configparser.ConfigParser()
    config.read('dictionary\\' + config_file + '.ini')
    if option in commset:
        config.set('commset', option, value)
    else:
        config.set(section, option, value)
    config.write(open('dictionary\\' + config_file + '.ini', 'w'))
    
    
def initfunc(config_file, sections, options):
    commset = ['1016','1030','1207','1203','1032','1005','1205']
    if not os.path.exists('dictionary\\' + config_file + '.ini'):
        config = configparser.ConfigParser()
        config.add_section('commset')
        for option in commset:
            config.set('commset', option, '')
        for section in sections:
            config.add_section(section)
            for option in options[section]:
                if option not in commset:
                    config.set(section, option, '')
        config.write(open('dictionary\\' + config_file + '.ini', 'w'))


