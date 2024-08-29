#!/usr/bin/env python3
# Written by Rupe version 2.1
#
"""
s3r4ph1
Tor script is an anonymizer
that sets up iptables and tor to route all services
and traffic including DNS through the tor network.
"""

from __future__ import print_function
import subprocess
from os.path import isfile, basename
from os import devnull
from sys import exit, stdout, stderr
from atexit import register
from argparse import ArgumentParser
from json import load
from urllib.request import urlopen
from urllib.error import URLError
from time import sleep


class s3r4ph1(object):

    def __init__(self):
        self.local_dnsport = "53"  # DNSPort
        self.virtual_net = "10.0.0.0/10"  # VirtualAddrNetwork
        self.local_loopback = "127.0.0.1" # Local loopback
        self.non_tor_net = ["192.168.0.0/16", "172.16.0.0/12"]
        self.non_tor = ["127.0.0.0/9", "127.128.0.0/10", "127.0.0.0/8"]
        self.tor_uid = subprocess.getoutput("id -ur debian-tor")  # Tor user uid
        self.trans_port = "9040"  # Tor port
        self.tor_config_file = '/etc/tor/torrc'
        self.torrc = f'''
## Inserted by {basename(__file__)} for tor iptables rules set
## Transparently route all traffic thru tor on port {self.trans_port}
VirtualAddrNetwork {self.virtual_net}
AutomapHostsOnResolve 1
TransPort {self.trans_port}
DNSPort {self.local_dnsport}
'''

    def flush_iptables_rules(self):
        subprocess.call(["iptables", "-F"])
        subprocess.call(["iptables", "-t", "nat", "-F"])

    def load_iptables_rules(self):
        self.flush_iptables_rules()
        self.non_tor.extend(self.non_tor_net)

        @register
        def restart_tor():
            with open(devnull, 'w') as fnull:
                try:
                    tor_restart = subprocess.check_call(
                        ["service", "tor", "restart"],
                        stdout=fnull, stderr=fnull
                    )

                    if tor_restart == 0:
                        print(" [\033[92m+\033[0m] Anonymizer status \033[92m[ON]\033[0m")
                        self.get_ip()
                except subprocess.CalledProcessError as err:
                    print(f"\033[91m[!] Command failed: {' '.join(err.cmd)}\033[0m")

        # See https://trac.torproject.org/projects/tor/wiki/doc/TransparentProxy#WARNING
        # See https://lists.torproject.org/pipermail/tor-talk/2014-March/032503.html
        subprocess.call(["iptables", "-I", "OUTPUT", "!", "-o", "lo", "!", "-d",
                         self.local_loopback, "!", "-s", self.local_loopback, "-p", "tcp",
                         "-m", "tcp", "--tcp-flags", "ACK,FIN", "ACK,FIN", "-j", "DROP"])
        subprocess.call(["iptables", "-I", "OUTPUT", "!", "-o", "lo", "!", "-d",
                         self.local_loopback, "!", "-s", self.local_loopback, "-p", "tcp",
                         "-m", "tcp", "--tcp-flags", "ACK,RST", "ACK,RST", "-j", "DROP"])

        subprocess.call(["iptables", "-t", "nat", "-A", "OUTPUT", "-m", "owner", "--uid-owner",
                         f"{self.tor_uid}", "-j", "RETURN"])
        subprocess.call(["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "udp", "--dport",
                         self.local_dnsport, "-j", "REDIRECT", "--to-ports", self.local_dnsport])

        for net in self.non_tor:
            subprocess.call(["iptables", "-t", "nat", "-A", "OUTPUT", "-d", f"{net}", "-j",
                             "RETURN"])

        subprocess.call(["iptables", "-t", "nat", "-A", "OUTPUT", "-p", "tcp", "--syn", "-j",
                         "REDIRECT", "--to-ports", f"{self.trans_port}"])

        subprocess.call(["iptables", "-A", "OUTPUT", "-m", "state", "--state",
                         "ESTABLISHED,RELATED", "-j", "ACCEPT"])

        for net in self.non_tor:
            subprocess.call(["iptables", "-A", "OUTPUT", "-d", f"{net}", "-j", "ACCEPT"])

        subprocess.call(["iptables", "-A", "OUTPUT", "-m", "owner", "--uid-owner", f"{self.tor_uid}", "-j", "ACCEPT"])
        subprocess.call(["iptables", "-A", "OUTPUT", "-j", "REJECT"])

    def get_ip(self):
        print(" [\033[92m*\033[0m] Getting public IP, please wait...")
        retries = 0
        my_public_ip = None
        while retries < 12 and not my_public_ip:
            retries += 1
            try:
                my_public_ip = load(urlopen('https://check.torproject.org/api/ip'))['IP']
            except URLError:
                sleep(5)
                print(" [\033[93m?\033[0m] Still waiting for IP address...")
            except ValueError:
                break
        if not my_public_ip:
            my_public_ip = subprocess.getoutput('wget -qO - ident.me')
        if not my_public_ip:
            exit(" \033[91m[!]\033[0m Can't get public IP address!")
        print(f" [\033[92m+\033[0m] Your IP is \033[92m{my_public_ip}\033[0m")


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Tor Iptables script for loading and unloading iptables rules'
    )
    parser.add_argument('-l',
                        '--load',
                        action='store_true',
                        help='This option will load tor iptables rules')
    parser.add_argument('-f',
                        '--flush',
                        action='store_true',
                        help='This option flushes the iptables rules to default')
    parser.add_argument('-r',
                        '--refresh',
                        action='store_true',
                        help='This option will change the circuit and gives new IP')
    parser.add_argument('-i',
                        '--ip',
                        action='store_true',
                        help='This option will output the current public IP address')
    args = parser.parse_args()

    try:
        load_tables = s3r4ph1()
        if isfile(load_tables.tor_config_file):
            if 'VirtualAddrNetwork' not in open(load_tables.tor_config_file).read():
                with open(load_tables.tor_config_file, 'a+') as torrconf:
                    torrconf.write(load_tables.torrc)

        if args.load:
            load_tables.load_iptables_rules()
        elif args.flush:
            load_tables.flush_iptables_rules()
            print(" [\033[93m!\033[0m] Anonymizer status \033[91m[OFF]\033[0m")
        elif args.ip:
            load_tables.get_ip()
        elif args.refresh:
            subprocess.call(['kill', '-HUP', f'{subprocess.getoutput("pidof tor")}'])
            load_tables.get_ip()
        else:
            parser.print_help()
    except Exception as err:
        print(f"[!] Run as super user: {err}")