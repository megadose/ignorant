from argparse import ArgumentParser, Namespace
from subprocess import Popen, PIPE
from typing import Any
from termcolor import colored
import httpx
from httpx import AsyncClient
import os
import time
import trio
from src.module import Module, ModuleResult
from importlib import import_module

import pkgutil

DEBUG = False
CHECK_FOR_UPDATES = False

__version__ = "1.2"


def import_submodules(package: Any, recursive: bool = True) -> None:
    """Get all the ignorant submodules"""
    if isinstance(package, str):
        package = import_module(package)
    for __, name, is_pkg in pkgutil.walk_packages(package.__path__):
        module_name = f"{package.__name__}.{name}"
        import_module(module_name)
        if recursive and is_pkg:
            import_submodules(module_name)


def check_update():
    """Check and update ignorant if not the last version"""
    if not CHECK_FOR_UPDATES:
        return
    check_version = httpx.get("https://pypi.org/pypi/ignorant/json")
    if check_version.json()["info"]["version"] != __version__:
        if os.name != "nt":
            p = Popen(
                ["pip3", "install", "--upgrade", "ignorant"], stdout=PIPE, stderr=PIPE
            )
        else:
            p = Popen(
                ["pip", "install", "--upgrade", "ignorant"], stdout=PIPE, stderr=PIPE
            )
        p.communicate()
        p.wait()
        print("Ignorant has just been updated, you can restart it.")
        exit()


def credit():
    """Print Credit"""
    print("Twitter : @palenath")
    print("Github : https://github.com/megadose/ignorant")
    print("For BTC Donations : 1FHDM49QfZX6pJmhjLE5tB2K6CaTLMZpXZ")


def print_result(
    out: list[ModuleResult],
    args: Namespace,
    phone: str,
    country_code: str,
    start_time: float,
    websites: list[type[Module]],
):
    def print_color(text: str, color: str, args: Namespace):
        if args.nocolor == False:
            return colored(text, color)
        else:
            return text

    description = (
        print_color("[+] Phone number used", "green", args)
        + ","
        + print_color(" [-] Phone number not used", "magenta", args)
        + ","
        + print_color(" [x] Rate limit", "red", args)
    )
    full_number = "+" + str(country_code) + " " + str(phone)
    # if args.noclear == False:
    #     print("\033[H\033[J")
    # else:
    #     print("\n")
    print("*" * (len(full_number) + 6))
    print("   " + full_number)
    print("*" * (len(full_number) + 6))

    for results in out:
        if results["rateLimit"] and args.onlyused == False:
            websiteprint = print_color("[x] " + results["domain"], "red", args)
            print(websiteprint)
        elif results["exists"] == False and args.onlyused == False:
            websiteprint = print_color("[-] " + results["domain"], "magenta", args)
            print(websiteprint)
        elif results["exists"] == True:
            toprint = ""
            websiteprint = print_color(
                "[+] " + results["domain"] + toprint, "green", args
            )
            print(websiteprint)

    print("\n" + description)
    print(
        str(len(websites))
        + " websites checked in "
        + str(round(time.time() - start_time, 2))
        + " seconds"
    )


async def launch_module(
    module: Module,
    phone: str,
    country_code: str,
    client: AsyncClient,
    out: list[ModuleResult],
):
    data = {
        "amazon": "amazon.com",
        "instagram": "instagram.com",
        "snapchat": "snapchat.com",
    }
    try:
        out.append(await module.run(phone, country_code, client))
    except:
        name = str(module).split("<function ")[1].split(" ")[0]
        out.append(
            {
                "name": name,
                "domain": data[name],
                "rateLimit": True,
                "exists": False,
                "method": None,
                "frequent_rate_limit": False,
            }
        )


async def maincore():
    parser = ArgumentParser(description=f"ignorant v{__version__}")
    parser.add_argument(
        "country_code",
        nargs="+",
        metavar="country code",
        help="Country code of the phone (Example +1)",
    )
    parser.add_argument(
        "phone",
        nargs="+",
        metavar="phone number",
        help="Target phone example (345568554)",
    )
    parser.add_argument(
        "--only-used",
        default=False,
        required=False,
        action="store_true",
        dest="onlyused",
        help="Displays only the sites used by the target email address.",
    )
    parser.add_argument(
        "--no-color",
        default=False,
        required=False,
        action="store_true",
        dest="nocolor",
        help="Don't color terminal output",
    )
    parser.add_argument(
        "--no-clear",
        default=False,
        required=False,
        action="store_true",
        dest="noclear",
        help="Do not clear the terminal to display the results",
    )
    parser.add_argument(
        "-T",
        "--timeout",
        default=10,
        required=False,
        dest="timeout",
        help="Set max timeout value (default 10)",
    )

    check_update()
    args = parser.parse_args()
    country_code = args.country_code[0]
    phone = args.phone[0]
    import_submodules("src.modules")
    websites: list[type[Module]] = Module.__subclasses__()

    timeout = args.timeout
    # Start time
    start_time = time.time()
    # Def the async client
    client = AsyncClient(timeout=timeout)
    # Launching the modules
    out: list[ModuleResult] = []
    async with trio.open_nursery() as nursery:
        for website in websites:
            nursery.start_soon(
                launch_module, website(), phone, country_code, client, out
            )
    # Sort by modules names
    out = sorted(out, key=lambda i: i["name"])
    # Close the client
    await client.aclose()
    # Print the result
    credit()
    print_result(out, args, phone, country_code, start_time, websites)


def main():
    trio.run(maincore)
