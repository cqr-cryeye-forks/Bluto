#!/usr/local/bin/python3.10
# -*- coding: utf-8 -*-

import datetime
import os
import re
import socket
import sys
import time
from errno import ETIMEDOUT
import random
import dns.query
import dns.resolver
import dns.zone
import pythonwhois
import requests
from pythonwhois.shared import WhoisException
from termcolor import colored

from .bluto_logging import info, INFO_LOG_FILE

default_s = False


def get_size(dir_location):
    start_path = dir_location
    total_size = 0
    for dir_path, dir_names, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dir_path, f)
            total_size += os.path.getsize(fp)
    total_size = total_size / 1024.0
    total_size = total_size / 1024.0
    return total_size


def action_whois(domain):
    company = None
    try:
        whois_things = pythonwhois.get_whois(domain)
        try:
            company = whois_things['contacts']['registrant']['name']
        except Exception:
            print('\nThere seems to be no Registrar for this domain.')
            company = domain
        splitup = domain.lower().split('.')[0]
        pattern = re.compile('|'.join(splitup))
        while True:
            if pattern.search(splitup):
                company = splitup
                info(f'Whois Results Are Good {company}')
                print('\nThe Whois Results Look Promising: ' + colored('{}', 'green').format(company))
                accept = input(colored('\nIs The Search Term sufficient?: ', 'green')).lower()
                if accept in ('y', 'yes'):
                    company = company
                    break
                elif accept in ('n', 'no'):
                    temp_company = input(colored('\nRegistered Company Name: ', 'green'))
                    if temp_company == '':
                        info('User Supplied Blank Company')
                        company = domain
                    else:
                        info(f'User Supplied Company {company}')
                        company = temp_company
                    break
                else:
                    print(f'\nThe Options Are yes|no Or y|no Not {accept}')

            else:
                info(f'Whois Results Not Good {company}')
                print(colored(f"\n\tThe Whois Results Don't Look Very Promising: '{company}'", "red"))
                print('\nPlease Supply The Company Name\n\n\tThis Will Be Used To Query LinkedIn')
                temp_company = input(colored('\nRegistered Company Name: ', 'green'))
                if temp_company == '':
                    info('User Supplied Blank Company')
                    company = domain
                else:
                    info(f'User Supplied Company {company}')
                    company = temp_company
                break
    except (WhoisException, socket.error, KeyError):
        pass
    except ETIMEDOUT:
        print(colored('\nWhoisError: You may be behind a proxy or firewall preventing whois lookups. '
                      f'Please supply the registered company name, if left blank the domain name "{domain}" will'
                      ' be used for the Linkedin search. The results may not be as accurate.',
                      'red'))
        temp_company = input(colored('\nRegistered Company Name: ', 'green'))
        company = domain if temp_company == '' else temp_company
    except Exception:
        info(f'An Unhandled Exception Has Occurred, Please Check The Log For Details{INFO_LOG_FILE}')

    if 'company' not in locals():
        print('There is no Whois data for this domain.\n\nPlease supply a company name.')
        while True:
            temp_company = input(colored('\nRegistered Company Name: ', 'green'))
            if temp_company == '':
                info('User Supplied Blank Company')
                company = domain
            else:
                company = temp_company
                info(f'User Supplied Company {company}')
            break
    return company


def action_country_id(countries_file, prox):
    def errorcheck(r):
        return 'success' in r.json()


    info('Identifying Country')
    userCountry = ''
    originCountry = ''
    userServer = ''
    # userIP = ''
    userID = False
    o = 0
    t_countries_dic = {}
    with open(countries_file) as fin:
        for line in fin:
            key, value = line.strip().split(';')
            t_countries_dic[key] = value
    countries_dic = {k.lower(): v.lower() for k, v in t_countries_dic.items()}
    country_list = [country for country, server in list(countries_dic.items())]
    country_list = sorted([item.capitalize() for item in country_list])
    api_keys = ['5751cce3503b56584e4b1267a7076904', 'dd763372274e9ae8aed34a55a7a4b36a']
    proxy = {'https': 'http://127.0.0.1:8080'} if prox else {}
    while True:
        try:
            while True:
                random.Random(500)
                key = random.choice(api_keys)
                r = requests.get(f'http://api.ipstack.com/check?access_key={key}',
                                     proxies=proxy, verify=False) if prox \
                    else requests.get(f'http://api.ipstack.com/check?access_key={key}', verify=False)
                response = r.json()
                if 'success' not in response:
                    break
            originCountry = response['country_name']
        except ValueError:
            if o == 0:
                print(colored('\nUnable to connect to the CountryID, we will retry.', 'red'))
            if o > 0:
                print(f'\nThis is {o} of 3 attempts')
            time.sleep(2)
            o += 1
            if o == 4:
                break
            continue
        break
    if o == 4:
        print(colored('\nWe have been unable to connect to the CountryID service.\n', 'red'))
        print('\nPlease let Bluto know what country you hale from.\n')
        print(colored('Available Countries:\n', 'green'))
        if len(country_list) % 2 != 0:
            country_list.append(" ")
        split = len(country_list) / 2
        l1 = country_list[:split]
        l2 = country_list[split:]
        for key, value in zip(l1, l2):
            print("{0:<20s} {1}".format(key, value))
        country_list = [item.lower() for item in country_list]
        while True:
            originCountry = input('\nCountry: ').lower()
            if originCountry in country_list:
                break
            if originCountry == '':
                print('\nYou have not selected a country so the default server will be used')
                originCountry = 'United Kingdom'.lower()
                break
            else:
                print('\nCheck your spelling and try again')
        for country, server in list(countries_dic.items()):
            if country == originCountry:
                userCountry = country
                userServer = server
                userID = True
    else:
        for country, server in list(countries_dic.items()):
            if country == originCountry.lower():
                userCountry = country
                userServer = server
                userID = True
        if not userID:
            if default_s:
                userCountry = 'DEFAULT'
            else:
                print("""Bluto currently doesn\'t have your countries google server available.\n
                Please navigate to "https://freegeoip.net/json/" and post an issue to 
                "https://github.com/darryllane/Bluto/issues"\n
                including the country value as shown in the json output\n
                You have been assigned to http://www.google.co.uk for now."""
                      )

                userServer = 'http://www.google.co.uk'
                userCountry = 'United Kingdom'
    print('\n\tSearching From: {0}\n\tGoogle Server: {1}\n'.format(userCountry.title(), userServer))

    info(f'Country Identified: {userCountry}')
    return userCountry, userServer


def action_bluto_use(countryID):
    now = datetime.datetime.now()
    try:
        link = "http://darryllane.co.uk/bluto/log_use.php"
        payload = {'country': countryID, 'Date': now}
        requests.post(link, data=payload)
    except Exception:
        info(f'An Unhandled Exception Has Occurred, Please Check The Log For Details{INFO_LOG_FILE}')


def check_dom(domain, myResolver):
    try:
        myAnswers = myResolver.query(domain, "NS")
        dom = str(myAnswers.canonical_name).strip('.')
    except dns.resolver.NoNameservers:
        print('\nError: \nDomain Not Valid, Check You Have Entered It Correctly\n')
        sys.exit()
    except dns.resolver.NXDOMAIN:
        print('\nError: \nDomain Not Valid, Check You Have Entered It Correctly\n')
        sys.exit()
    except dns.exception.Timeout:
        print('\nThe connection hit a timeout. Are you connected to the internet?\n')
        sys.exit()
    except Exception:
        info(f'An Unhandled Exception Has Occurred, Please Check The Log For Details{INFO_LOG_FILE}')
