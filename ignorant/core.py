from argparse import ArgumentParser
from bs4 import BeautifulSoup
from datetime import datetime
from subprocess import Popen, PIPE
from termcolor import colored
import csv
import hashlib
import hmac
import httpx
import importlib
import json
import os
import pkgutil
import random
import re
import string
import sys
import time
import trio
import urllib.parse

from ignorant.localuseragent import ua
from ignorant.instruments import TrioProgress

DEBUG = False

__version__ = "1.1"


def import_submodules(package, recursive=True):
    """Get all the ignorant submodules"""
    if isinstance(package, str):
        package = importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name))
    return results

def get_functions(modules,args=None):
    """Transform the modules objects to functions"""
    websites = []

    for module in modules:
        if len(module.split(".")) > 3 :
            modu = modules[module]
            site = module.split(".")[-1]
            websites.append(modu.__dict__[site])
    return websites

def check_update():
    """Check and update ignorant if not the last version"""
    check_version = httpx.get("https://pypi.org/pypi/ignorant/json")
    if check_version.json()["info"]["version"] != __version__:
        if os.name != 'nt':
            p = Popen(["pip3",
                       "install",
                       "--upgrade",
                       "ignorant"],
                      stdout=PIPE,
                      stderr=PIPE)
        else:
            p = Popen(["pip",
                       "install",
                       "--upgrade",
                       "ignorant"],
                      stdout=PIPE,
                      stderr=PIPE)
        (output, err) = p.communicate()
        p_status = p.wait()
        print("Ignorant has just been updated, you can restart it.")
        exit()

def credit():
    """Print Credit"""
    print('Twitter : @palenath')
    print('Github : https://github.com/megadose/ignorant')
    print('For BTC Donations : 1FHDM49QfZX6pJmhjLE5tB2K6CaTLMZpXZ')


def print_result(data,args,phone, country_code,start_time,websites):
    def print_color(text,color,args):
        if args.nocolor == False:
            return(colored(text,color))
        else:
            return(text)

    description = print_color("[+] Phone number used","green",args) + "," + print_color(" [-] Phone number not used", "magenta",args) + "," + print_color(" [x] Rate limit","red",args)
    full_number="+"+str(country_code)+" "+str(phone)
    print("\033[H\033[J")
    print("*" * (len(full_number) + 6))
    print("   " + full_number)
    print("*" * (len(full_number) + 6))

    for results in data:
        if results["rateLimit"] and args.onlyused == False:
            websiteprint = print_color("[x] " + results["domain"], "red",args)
            print(websiteprint)
        elif results["exists"] == False and args.onlyused == False:
            websiteprint = print_color("[-] " + results["domain"], "magenta",args)
            print(websiteprint)
        elif results["exists"] == True:
            toprint = ""
            websiteprint = print_color("[+] " + results["domain"] + toprint, "green",args)
            print(websiteprint)

    print("\n" + description)
    print(str(len(websites)) + " websites checked in " +
          str(round(time.time() - start_time, 2)) + " seconds")


async def launch_module(module, phone, country_code, client, out):
    data={'amazon':'amazon.com','instagram':'instagram.com','snapchat': 'snapchat.com'}
    try:
        await module(phone, country_code, client, out)
    except :
        name=str(module).split('<function ')[1].split(' ')[0]
        out.append({"name": name,"domain":data[name],
                    "rateLimit": True,
                    "exists": False})
async def maincore():
    parser= ArgumentParser(description=f"ignorant v{__version__}")
    parser.add_argument("country_code",
                    nargs='+', metavar='country code',
                    help="Country code of the phone (Example +1)")
    parser.add_argument("phone",
                    nargs='+', metavar='phone number',
                    help="Target phone example (345568554)")
    parser.add_argument("--only-used", default=False, required=False,action="store_true",dest="onlyused",
                    help="Displays only the sites used by the target email address.")
    parser.add_argument("--no-color", default=False, required=False,action="store_true",dest="nocolor",
                    help="Don't color terminal output")
    parser.add_argument("-T","--timeout", default=10, required=False,dest="timeout",
                    help="Set max timeout value (default 10)")

    check_update()
    args = parser.parse_args()
    credit()
    country_code=args.country_code[0]
    phone=args.phone[0]

    # Import Modules
    modules = import_submodules("ignorant.modules")
    websites = get_functions(modules,args)

    timeout=args.timeout
    # Start time
    start_time = time.time()
    # Def the async client
    client = httpx.AsyncClient(timeout=timeout)
    # Launching the modules
    out = []
    instrument = TrioProgress(len(websites))
    trio.lowlevel.add_instrument(instrument)
    async with trio.open_nursery() as nursery:
        for website in websites:
            nursery.start_soon(launch_module, website, phone, country_code, client, out)
    trio.lowlevel.remove_instrument(instrument)
    # Sort by modules names
    out = sorted(out, key=lambda i: i['name'])
    # Close the client
    await client.aclose()
    # Print the result
    print_result(out,args,phone, country_code,start_time,websites)
    credit()
def main():
    trio.run(maincore)
