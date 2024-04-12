#!/usr/local/bin/python3.10

# -*- coding: utf-8 -*-

import random
import re
import socket
import string
import sys
import time
import traceback
from multiprocessing.dummy import Pool as ThreadPool

import dns.resolver
from termcolor import colored

from .bluto_logging import info, INFO_LOG_FILE

targets = []


def data_getdns1():
    global data_Name_Server
    return data_Name_Server


def data_getdns2():
    global data_Mail_Server
    return data_Mail_Server


def set_resolver(timeout_value):
    myResolver = dns.resolver.Resolver()
    myResolver.timeout = timeout_value
    myResolver.lifetime = timeout_value
    myResolver.nameservers = ['8.8.8.8', '8.8.4.4']

    return myResolver


def get_dns_details(domain, myResolver):
    info('Gathering DNS Details')
    ns_list = []
    zn_list = []
    mx_list = []
    try:
        print("\nName Server:\n")
        global data_Name_Server
        list_Name_Server = []
        myAnswers = myResolver.query(domain, "NS")
        for data in myAnswers.rrset:
            data1 = str(data)
            data2 = data1.rstrip('.')
            addr = socket.gethostbyname(data2)
            ns_list.append(data2 + '\t' + addr)
            zn_list.append(data2)
            list(set(ns_list))
            ns_list.sort()
        for i in ns_list:
            print(colored(i, 'green'))
            list_Name_Server.append(i)
            domains = []
            ips = []
            data_Name_Server = []
            for item in list_Name_Server:
                domain, ip = re.split(r"\t", item)
                domains.append(domain)
                ips.append(ip)
                domain_ip = {
                    "domain": domain,
                    "ip": ip,
                }
                data_Name_Server.append(domain_ip)
            print("\n\n", data_Name_Server)
    except dns.resolver.NoNameservers:
        info('\tNo Name Servers\nConfirm The Domain Name Is Correct.' + INFO_LOG_FILE, exc_info=True)

        sys.exit()
    except dns.resolver.NoAnswer:
        print("\tNo DNS Servers")
    except dns.resolver.NXDOMAIN:
        info("\tDomain Does Not Exist" + INFO_LOG_FILE, exc_info=True)
        sys.exit()
    except dns.resolver.Timeout:
        info('\tTimeout\nConfirm The Domain Name Is Correct.' + INFO_LOG_FILE, exc_info=True)

        sys.exit()
    except Exception:
        info('An Unhandled Exception Has Occurred, Please Check The Log For Details\n' + INFO_LOG_FILE, exc_info=True)

    try:
        print("\nMail Server:\n")
        global data_Mail_Server
        data_Mail_Server = []
        myAnswers = myResolver.query(domain, "MX")
        for data in myAnswers:
            data1 = str(data)
            data2 = data1.split(' ', 1)[1].rstrip('.')
            addr = socket.gethostbyname(data2)
            mx_list.append(data2 + '\t' + addr)
            list(set(mx_list))
            mx_list.sort()
        for i in mx_list:
            print(colored(i, 'green'))
            data_Mail_Server.append(i)
    except dns.resolver.NoAnswer:
        print("\tNo Mail Servers")
    except Exception:
        info(f'An Unhandled Exception Has Occurred, Please Check The Log For Details{INFO_LOG_FILE}')

    info('Completed Gathering DNS Details')
    return zn_list


def action_wild_cards(domain, myResolver):
    info('Checking Wild Cards')
    try:
        one = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))
        myAnswers = myResolver.query(f'{one}.{str(domain)}')
    except dns.resolver.NoNameservers:
        pass
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        info('Wild Cards False')
        return False
    else:
        info('Wild Cards True')
        return True


def action_brute(subdomain):
    global myResolverG
    try:
        print(f'Testing subdomain {subdomain}')
        myAnswers = myResolverG.query(subdomain)
        for data in myAnswers:
            print(f'{subdomain} {str(data)}')
            targets.append(f'{subdomain} {str(data)}')
    except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.SyntaxError):
        pass
    except dns.exception.Timeout:
        info(f'Timeout: {subdomain}')
    except Exception:
        info(f'An Unhandled Exception Has Occurred, Please Check The Log For Details{INFO_LOG_FILE}')
        info(traceback.print_exc())


def action_brute_start(subs, myResolver):
    global myResolverG
    myResolverG = myResolver
    info('Brute forcing SubDomains')
    print('\nBrute Forcing Sub-Domains\n')
    pool = ThreadPool(8)
    pool.map(action_brute, subs)
    pool.close()
    info('Completed Brute forcing SubDomains')

    return targets


def action_brute_wild(sub_list, domain, myResolver):
    info('Brute forcing Wild Card SubDomains')
    target_results = []
    random_addresses = []
    for _ in range(10):
        one = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

        myAnswers = myResolver.query(f'{one}.{str(domain)}')
        name = myAnswers.canonical_name
        random_addr = socket.gethostbyname(str(name))
        random_addresses.append(random_addr)
    random_addresses = sorted(set(random_addresses))
    for host in sub_list:
        try:
            host_host, host_addr = host.split(' ')
            if host_addr not in random_addresses:
                target_results.append(host)
        except (dns.resolver.NoNameservers, dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.name.EmptyLabel):
            pass
        except Exception:
            continue
    info('Completed Brute forcing Wild Card SubDomains')
    return target_results


def action_zone_transfer(zn_list, domain):
    info('Attempting Zone Transfers')
    print("\nAttempting Zone Transfers")
    zn_list.sort()
    vuln = True
    vulnerable_listT = []
    vulnerable_listF = []
    dump_list = []
    global data_Attempting_Zone_Transfers
    data_Attempting_Zone_Transfers = []
    for ns in zn_list:
        try:
            z = dns.zone.from_xfr(dns.query.xfr(ns, domain, timeout=3, lifetime=5))
            names = sorted(list(z.nodes.keys()))
            if vuln:
                info(f'Vuln: {ns}')
                vulnerable_listT.append(ns)
        except Exception:
            # error = str(e)
            info(f'Not Vuln: {ns}')
            vuln = False
            vulnerable_listF.append(ns)
    if vulnerable_listF:
        print("\nNot Vulnerable:\n")
        for ns in vulnerable_listF:
            print(colored(ns, 'green'))
            data_Attempting_Zone_Transfers.append(ns)
    if vulnerable_listT:
        _extracted_from_action_zone_transfer_36(vulnerable_listT, domain, dump_list)
    info('Completed Attempting Zone Transfers')
    return vulnerable_listT, sorted(set(dump_list))


# TODO Rename this here and in `action_zone_transfer`
def _extracted_from_action_zone_transfer_36(vulnerable_listT, domain, dump_list):
    info('Vulnerable To Zone Transfers')
    print("\nVulnerable:\n")
    for ns in vulnerable_listT:
        print(colored(ns, 'red'), colored("\t" + "TCP/53", 'red'))
    z = dns.zone.from_xfr(dns.query.xfr(vulnerable_listT[0], domain, timeout=3, lifetime=5))

    names = sorted(list(z.nodes.keys()))
    print("\nRaw Zone Dump\n")
    for n in names:
        data1 = f"{n}.{domain}"
        try:
            addr = socket.gethostbyname(data1)
            dump_list.append(f"{n}.{domain} {addr}")
        except Exception as e:
            error = str(e)
            if error != 'Errno -2] Name or service not known':
                info('An Unhandled Exception Has Occurred, Please Check The Log For Details\n' + INFO_LOG_FILE,
                     exc_info=True)

        print(z[n].to_text(n))
