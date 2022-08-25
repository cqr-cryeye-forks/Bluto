#!/usr/local/bin/python3.10
# -*- coding: utf-8 -*-

import random
import sys

from .bluto_logging import info, INFO_LOG_FILE


def get_user_agents(useragent_f):
    info('Gathering UserAgents')
    uas = []
    with open(useragent_f, 'rb') as uaf:
        uas.extend(ua.strip()[1:-1 - 1] for ua in uaf if ua)
    random.shuffle(uas)
    info('Completed Gathering UserAgents')
    return uas


def get_subs(filename, domain):
    info('Gathering SubDomains')
    full_list = []
    try:
        subs = [line.rstrip('\n') for line in open(filename)]
        full_list.extend(str(f"{sub.lower()}.{domain}") for sub in subs)
    except Exception:
        info(f'An Unhandled Exception Has Occurred, Please Check The Log For Details{INFO_LOG_FILE}')
        sys.exit()
    info('Completed Gathering SubDomains')
    return full_list


def get_sub_interest(filename, domain):
    info('Gathering SubDomains Of Interest')
    full_list = []
    try:
        subs = [line.rstrip('\n') for line in open(filename)]
        full_list.extend(str(f"{sub.lower()}.{domain}") for sub in subs)
    except Exception:
        info(f'An Unhandled Exception Has Occurred, Please Check The Log For Details{INFO_LOG_FILE}')
        sys.exit()
    info('Completed Gathering SubDomains Of Interest')
    return full_list


def get_line_count(filename):
    info('Gathering SubDomains Count')
    lines = sum(1 for _ in open(filename))
    info('Completed Gathering SubDomains Count')
    return lines
