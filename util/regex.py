#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
import re


def regex_str(line) :

    line = re.sub('\([ㄱ-ㅎ가-힣0-9a-zA-Z\s%.?&,+*-:\/]+\)\/\(', ' (', line)
    line = re.sub('(b/)|(o/)|(l/)|(n/)|(u/)', '', line)
    line = re.sub('[()]', '', line)
    line = re.sub('[.]', '', line)
    line = re.sub('[,?!/-]', ' ', line)

    line = re.sub('[*+]', '', line)
    line = re.sub('[>]', '', line)
    line = re.sub('[\t\r\f\v]', ' ', line)
    line = re.sub('[ ]+', ' ', line)

    line = line.lower()
    #print(jamo_line)

    return line
    
def addspace(line) :
    
    line = re.sub('[ ]', 'S ', line)
    return line

def isdigit(line) :
    if (re.findall('\d+', line)) :
        return True
    return False

def isNone(line) :
    if (line == None) :
        return True
    return False

def isspecialletter(line) :
    if (re.findall('[~!@#$%^&*():;/\<>?.,]', line)) :
        return True
    return False

def issparseletter(line) :
    if (re.findall('[~!@#$%^&*():;/\<>?.,]', line)) :
        return True
    return False

def isHangul(text):
    #Check the Python Version
    pyVer3 =  sys.version_info >= (3, 0)

    if pyVer3 : # for Ver 3 or later
        encText = text
    else: # for Ver 2.x
        if type(text) is not unicode:
            encText = text.decode('utf-8')
        else:
            encText = text

    hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', encText))
    #print("hancount:", hanCount)
    return hanCount > 0

