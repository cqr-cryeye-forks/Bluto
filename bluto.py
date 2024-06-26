#!/usr/bin/python3.10
# -*- coding: utf-8 -*-

"""
Description:

DNS Recon | Brute Forcer | DNS Zone Transfer | DNS Wild Card Checks | DNS Wild Card Brute Forcer
Email Enumeration | Staff Enumeration | Compromised Account Enumeration | MetaData Harvesting

Author:  Darryl Lane
Twitter: @darryllane101

Usage:
    bluto [--domain=<domain>] [-e] [-u] [--timeout=<timeout>] [--api=<key>] [--output=<output>]
    bluto -h | --help
    bluto --version

Options:
    bluto --output      Save in output file
    bluto -e           Large Subdomain list used for Brute forcing
    bluto -u           Check for latest version of Bluto
    bluto --timeout    Set DNS timeout in seconds
    bluto --domain     Set target domain
    bluto --api        Set Hunter API key
    bluto --help       Help menu
    bluto --version    Current Bluto version

"""


# Google Search Started
# Not Vulnerable
# None of the Name Servers are vulnerable to Zone Transfers
# Wild Cards Are Not In Place
# INFO:MyLogger:Identifying Country
# INFO:MyLogger:Country Identified: ukraine
# Gathering Data From Google, Bing And LinkedIn
# INFO:MyLogger:Data Folder Created /home/user-q/Bluto/doc/dima/
# Brute Forcing Sub-Domains
# INFO:MyLogger:An Unhandled Exception Has Occurred, Please Check The Log For Details /home/user-q/Bluto/log/bluto-info.log


import argparse
import json
import os
import pathlib
import queue
import site
import sys
import threading
import time
from typing import Final

import dns.zone
from docopt import docopt
from termcolor import colored

from Bluto.modules.bluto_logging import info
from Bluto.modules.data_mine import doc_start
from Bluto.modules.general import action_country_id, action_whois, action_bluto_use, check_dom
from Bluto.modules.get_dns import action_brute_start, action_wild_cards, action_zone_transfer, get_dns_details, \
    action_brute_wild, set_resolver
from Bluto.modules.get_file import get_subs, get_sub_interest, get_line_count, get_user_agents
from Bluto.modules.output import action_output_vuln_zone, action_output_wild_false, action_output_wild_false_hunter, \
    action_output_vuln_zone_hunter
from Bluto.modules.search import action_bing_true, action_google, action_linkedin, action_netcraft, action_emailHunter
from Bluto.modules.update import updateCheck

MAIN_DIR: Final[pathlib.Path] = pathlib.Path(__file__).parent

FILENAME_1: str = MAIN_DIR / "Bluto/doc/subdomains-top1mil-20000.txt"
FILENAME_2: str = MAIN_DIR / "Bluto/doc/sub_interest.txt"
USERAGENT_F: str = MAIN_DIR / "Bluto/doc/user_agents.txt"
COUNTRIES_FILE: str = MAIN_DIR / "Bluto/doc/countries.txt"
INFO_LOG_FILE = os.path.expanduser('~/Bluto/log/bluto-info.log')

result1 = None
result2 = None
result3 = None

version = '3.0.3'

title = """
 BBBBBBBBBBBBBBBBB   lllllll                            tttt
 B::::::::::::::::B  l:::::l                          ttt:::t
 B::::::BBBBBB:::::B l:::::l                          t:::::t
 BB:::::B     B::::: l:::::l {0}                   t:::::t
   B::::B     B:::::B l::::l uuuuuu    uuuuu ttttttt:::::ttttttt       oooooooooooo
   B::::B     B:::::B l::::l u::::u    u:::: t:::::::::::::::::t      oo:::::::::::oo
   B::::BBBBBB:::::B  l::::l u::::u    u:::: t:::::::::::::::::t     o:::::::::::::::o
   B:::::::::::::BB   l::::l u::::u    u:::: tttttt:::::::tttttt     o:::::ooooo:::::o
   B::::BBBBBB:::::B  l::::l u::::u    u::::u      t:::::t           o::::o     o::::o
   B::::B     B:::::B l::::l u::::u    u::::u      t:::::t           o::::o     o::::o
   B::::B     B:::::B l::::l u::::u    u::::u      t:::::t           o::::o     o::::o
   B::::B     B:::::B l::::l u:::::uuuu:::::u      t:::::t    tttttt o::::o     o::::o
BB:::::BBBBBB:::::: l::::::l u:::::::::::::::uu    t::::::tttt:::::t o:::::ooooo:::::o
B:::::::::::::::::B l::::::l u:::::::::::::::uu    tt::::::::::::::t o:::::::::::::::o
B::::::::::::::::B  l::::::l  uu::::::::uu:::u      tt:::::::::::ttt  oo:::::::::::oo
BBBBBBBBBBBBBBBBB   llllllll    uuuuuuuu  uuuu        ttttttttttt      ooooooooooo
""".format(colored("v" + version, 'red'))

desc = """  {2} | {3} | {4} | {9}
        {8} | {7} | {10}
               {11}  |  {12}

                 {0}  |  {1}
                     {5}
""".format(colored("Author: Darryl Lane", 'blue'), colored("Twitter: @darryllane101", 'blue'),
           colored("DNS Recon", 'green'), colored("SubDomain Brute Forcer", 'green'),
           colored("DNS Zone Transfers", 'green'), colored("https://github.com/darryllane/Bluto", 'green'),
           colored("v" + version, 'red'), colored("Email Enumeration", 'green'), colored("Staff Enumeration", 'green'),
           colored("DNS Wild Card Checks", 'green'), colored("DNS Wild Card Brute Forcer", 'green'),
           colored("Compromised Account Enumeration", 'green'), colored("MetaData Mining", 'green'))

prox = False

if __name__ == "__main__":
    info('\nBluto Started')
    args = docopt(__doc__, version=version)
    # print(title)
    print(desc)
    q4 = queue.Queue()
    # Check Arguments
    try:
        if args['-u']:
            info('Checking For Update')
            updateCheck(version)

        if args['--timeout']:
            timeout_value = args['--timeout']
            myResolver = set_resolver(timeout_value)
        else:
            myResolver = dns.resolver.Resolver()
            myResolver.timeout = 10
            myResolver.lifetime = 10
            myResolver.nameservers = ['8.8.8.8', '8.8.4.4']

        if args['-e']:
            info('-e Argument Used')
            FILENAME_1: str = MAIN_DIR / "Bluto/doc/lots-of-spinach.txt"

        if args['--api']:
            api = args['--api']
            info('-api Argument Used with api: ' + str(api))
        else:
            api = False

        domain = args['--domain']
        output = args['--output']

        user_agents = get_user_agents(USERAGENT_F)
        info('Domain Identified: ' + str(domain))
        domain_r = domain.split('.')
        report_location = os.path.expanduser('~/Bluto/Bluto-Evidence-{}.html'.format(domain_r[0]))
        # Check if domain valid
        check_dom(domain, myResolver)
        # WhoisGet
        company = action_whois(domain)
        # Detail Call
        sub_interest = get_sub_interest(FILENAME_2, domain)
        zn_list = get_dns_details(domain, myResolver)
        # NetCraft Call
        netcraft_list = action_netcraft(domain, myResolver)
        # ZoneTrans Call
        vulnerable_results = action_zone_transfer(zn_list, domain)
        if vulnerable_results == ([], []):
            print("\nNone of the Name Servers are vulnerable to Zone Transfers")
            # Testing For Wild Cards
            print('\nTesting For Wild Cards')
            value = action_wild_cards(domain, myResolver)
            # Wild Cards True
            if value:
                print(colored('\n\tWild Cards Are In Place', 'green'))
                print(colored("\n\tOh no! You ain't eatin' no spinach in this picture", 'blue'))
                print(colored("\n\nThis Will Take A While Longer, On Average +- 20min", 'grey'))
                check_count = get_line_count(FILENAME_1)
                # Grabbing Subs
                subs = get_subs(FILENAME_1, domain)
                print('\nGathering Data From Google, Bing And LinkedIn')
                # Checking Request Country
                userCountry, userServer = action_country_id(COUNTRIES_FILE, prox)
                action_bluto_use(userCountry)
                start_time_total = time.time()
                # Executing Jobs
                q1 = queue.Queue()
                q2 = queue.Queue()
                q3 = queue.Queue()
                q5 = queue.Queue()
                t1 = threading.Thread(target=action_google,
                                      args=(domain, userCountry, userServer, q1, user_agents, prox))
                t2 = threading.Thread(target=action_bing_true, args=(domain, q2, user_agents, prox))
                t3 = threading.Thread(target=action_linkedin,
                                      args=(domain, userCountry, q3, company, user_agents, prox))
                t5 = threading.Thread(target=doc_start, args=(domain, user_agents, prox, q5))
                start_time_email = time.time()
                if api:
                    t4 = threading.Thread(target=action_emailHunter, args=(domain, api, user_agents, q4,
                                                                           prox))  # Takes domain[str], api[list], user_agents[list] #Returns email,url [list[tuples]] Queue[object], prox[str]
                    t4.start()
                    t4.join()
                else:
                    print(colored(
                        '\nDon\'t forget you can increase your identified email count significantly with a free Hunter API key.\nhttps://hunter.io/api_keys',
                        'green'))
                t1.start()
                t1.join()
                t2.start()
                t2.join()
                time_spent_email = time.time() - start_time_email
                t3.start()
                t3.join()
                start_download_time = time.time()
                t5.start()
                t5.join()
                time_spent_download = time.time() - start_download_time
                google_true_results = q1.get()
                bing_true_results = q2.get()
                linkedin_results = q3.get()
                data_mine = q5.get()
                start_time_brute = time.time()
                targets_t = action_brute_start(subs, myResolver)
                targets = action_brute_wild(targets_t, domain, myResolver)
                time_spent_brute = time.time() - start_time_brute
                time_spent_total = time.time() - start_time_total
                if not targets:
                    targets.append("temp-enter")
                domains = sorted(set(targets + netcraft_list))
                if "temp-enter" in domains: domains.remove("temp-enter")
                brute_results_dict = dict((x.split(' ') for x in domains))
                # Outputting data
                if api:
                    emailHunter_results = q4.get()
                    result1 = action_output_wild_false_hunter(brute_results_dict, sub_interest, google_true_results,
                                                    bing_true_results, linkedin_results, check_count, domain,
                                                    time_spent_email, time_spent_brute, time_spent_total,
                                                    emailHunter_results, args, report_location, company, data_mine)
                else:
                    result1 = action_output_wild_false(brute_results_dict, sub_interest, google_true_results, bing_true_results,
                                             linkedin_results, check_count, domain, time_spent_email, time_spent_brute,
                                             time_spent_total, report_location, company, data_mine)
            # WildCards False
            else:
                print(colored('\n\tWild Cards Are Not In Place', 'red'))
                check_count = get_line_count(FILENAME_1)
                # Grabbing Subs
                subs = get_subs(FILENAME_1, domain)
                print('\nGathering Data From Google, Bing And LinkedIn')
                # Checking Request Country
                userCountry, userServer = action_country_id(COUNTRIES_FILE, prox)
                action_bluto_use(userCountry)
                start_time_total = time.time()
                # Executing Jobs
                q1 = queue.Queue()
                q2 = queue.Queue()
                q3 = queue.Queue()
                q5 = queue.Queue()
                t1 = threading.Thread(target=action_google,
                                      args=(domain, userCountry, userServer, q1, user_agents, prox))
                t2 = threading.Thread(target=action_bing_true, args=(domain, q2, user_agents, prox))
                t3 = threading.Thread(target=action_linkedin,
                                      args=(domain, userCountry, q3, company, user_agents, prox))
                t5 = threading.Thread(target=doc_start, args=(domain, user_agents, prox, q5))
                start_time_email = time.time()
                if api:
                    q4 = queue.Queue()
                    t4 = threading.Thread(target=action_emailHunter, args=(domain, api, user_agents, q4,
                                                                           prox))  # Takes domain[str], api[list], user_agents[list] #Returns email,url [list[tuples]] Queue[object], prox[str]
                    t4.start()
                    t4.join()
                else:
                    print(colored(
                        '\nDon\'t forget you can increase your identified email count significantly with a free Hunter API key.\nhttps://hunter.io/api_keys',
                        'green'))
                t1.start()
                t1.join()
                t2.start()
                t2.join()
                time_spent_email = time.time() - start_time_email
                t3.start()
                t3.join()
                start_download_time = time.time()
                t5.start()
                t5.join()

                time_spent_download = time.time() - start_download_time
                google_true_results = q1.get()
                bing_true_results = q2.get()
                linkedin_results = q3.get()
                if q5.empty():
                    q5.put(None)
                data_mine = q5.get()
                start_time_brute = time.time()
                targets = action_brute_start(subs, myResolver)
                time_spent_brute = time.time() - start_time_brute
                time_spent_total = time.time() - start_time_total
                # Clean Brute Results
                if not targets:
                    targets.append("temp-enter")
                domains = sorted(set(targets + netcraft_list))
                if "temp-enter" in domains: domains.remove("temp-enter")
                brute_results_dict = dict((x.split(' ') for x in domains))
                if api:
                    emailHunter_results = q4.get()
                    result2 = action_output_wild_false_hunter(brute_results_dict, sub_interest, google_true_results,
                                                    bing_true_results, linkedin_results, check_count, domain,
                                                    time_spent_email, time_spent_brute, time_spent_total,
                                                    emailHunter_results, args, report_location, company, data_mine)
                # Outputting data
                else:
                    result2 = action_output_wild_false(brute_results_dict, sub_interest, google_true_results, bing_true_results,
                                             linkedin_results, check_count, domain, time_spent_email, time_spent_brute,
                                             time_spent_total, report_location, company, data_mine)
        else:
            # Vuln Zone Trans
            vulnerable_list = vulnerable_results[0]
            clean_dump = vulnerable_results[1]
            print('\nGathering Data From Google, Bing And LinkedIn')
            userCountry, userServer = action_country_id(COUNTRIES_FILE, prox)
            action_bluto_use(userCountry)
            start_time_total = time.time()
            q1 = queue.Queue()
            q2 = queue.Queue()
            q3 = queue.Queue()
            q5 = queue.Queue()
            t1 = threading.Thread(target=action_google, args=(domain, userCountry, userServer, q1, user_agents, prox))
            t2 = threading.Thread(target=action_bing_true, args=(domain, q2, user_agents, prox))
            t3 = threading.Thread(target=action_linkedin, args=(domain, userCountry, q3, company, user_agents, prox))
            t5 = threading.Thread(target=doc_start, args=(domain, user_agents, prox, q5))
            start_time_email = time.time()
            if api:
                q4 = queue.Queue()
                t4 = threading.Thread(target=action_emailHunter, args=(domain, api, user_agents, q4,
                                                                       prox))  # Takes domain[str], api[list], user_agents[list] #Returns email,url [list[tuples]] Queue[object], prox[str]
                t4.start()
                t4.join()
            else:
                print(colored(
                    '\nDon\'t forget you can increase your identified email count significantly with a free Hunter API key.\nhttps://hunter.io/api_keys',
                    'green'))
            t1.start()
            t1.join()
            t2.start()
            t2.join()
            time_spent_email = time.time() - start_time_email
            t3.start()
            t3.join()
            start_download_time = time.time()
            t5.start()
            t5.join()
            time_spent_download = time.time() - start_download_time
            google_results = q1.get()
            bing_results = q2.get()
            linkedin_results = q3.get()
            data_mine = q5.get()
            time_spent_total = time.time() - start_time_total
            # Outputting data
            if api:
                emailHunter_results = q4.get()
                result3 = action_output_vuln_zone_hunter(google_results, bing_results, linkedin_results, time_spent_email,
                                               time_spent_total, clean_dump, sub_interest, domain, emailHunter_results,
                                               args, report_location, company, data_mine)
            else:
                result3 = action_output_vuln_zone(google_results, bing_results, linkedin_results, time_spent_email,
                                        time_spent_total, clean_dump, sub_interest, domain, report_location, company,
                                        data_mine)

        info('Bluto Finished')
    except KeyboardInterrupt:
        print('\n\nRage Quit!..')
        info('Keyboard Interrupt From User\n')
        sys.exit()
    except Exception as e:
        print(e)

    all_results = {
        "result1": result1,
        "result2": result2,
        "result3": result3,

    }
    output_json: str = MAIN_DIR / output

    with open(output_json, "w") as jf:
        json.dump(all_results, jf, indent=2)
