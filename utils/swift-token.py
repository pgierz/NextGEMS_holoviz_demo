#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2016 Deutsches Klimarechenzentrum GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import getpass
import os
import os.path
import stat
import sys
import time
from datetime import datetime, timedelta

import requests

SWIFT_BASE = "https://swift.dkrz.de/"


def is_sh_family():
    return os.environ.get("SHELL", "").split("/")[-1] in ["bash", "sh", "ksh", "zsh"]


def get_env_content(sh, token, storage_url):
    if sh:
        return (
            "OS_AUTH_TOKEN={}\nOS_STORAGE_URL={}\n"
            "export OS_AUTH_TOKEN\nexport OS_STORAGE_URL\n"
            "unset OS_AUTH_URL\n"
            "unset OS_USERNAME\n"
            "unset OS_PASSWORD\n".format(token, storage_url)
        )
    else:
        return (
            "setenv OS_AUTH_TOKEN {}\n"
            "setenv OS_STORAGE_URL {}\n"
            'setenv OS_AUTH_URL " "\n'
            'setenv OS_USERNAME " "\n'
            'setenv OS_PASSWORD " "\n'.format(token, storage_url)
        )


def create_token():
    account = input("Account: ")
    username = input("Username: ")
    password = getpass.getpass()

    timezone = time.tzname[-1]
    expires = token = storage_url = None

    try:
        resp = requests.get(
            SWIFT_BASE + "auth/v1.0",
            headers={
                "X-Auth-User": "{}:{}".format(account, username),
                "X-Auth-Key": password,
            },
        )
        resp.raise_for_status()

        token = resp.headers["x-auth-token"]
        storage_url = resp.headers["x-storage-url"]
        expires_in = int(resp.headers["x-auth-token-expires"])
        expires_at = datetime.fromtimestamp(time.time() + expires_in)
        expires = expires_at.strftime("%a %d. %b %H:%M:%S {tz} %Y".format(tz=timezone))

        if expires and token and storage_url:
            with open(os.path.expanduser("~/.swiftenv"), "w") as f:
                content = get_env_content(is_sh_family(), token, storage_url)
                f.write("#token expires on: {}\n{}".format(expires, content))
                os.chmod(
                    os.path.expanduser("~/.swiftenv"), stat.S_IREAD | stat.S_IWRITE
                )
    except requests.RequestException:
        print("Login failed.")
        sys.exit(-1)


def info_token():
    try:
        with open(os.path.expanduser("~/.swiftenv"), "r") as f:
            line = f.readline()[:-1]
            expire_s = " ".join(line.split(" ")[3:])
            expire_d = datetime.strptime(expire_s, "%a %d. %b %H:%M:%S %Z %Y")
            now = datetime.now()
            soon = now + timedelta(hours=8)

            if now > expire_d:
                print(
                    "Your swift token is expired. "
                    "Please create a new one with swift-token. "
                )
                sys.exit(0)

            print("Your swift token will expire on {}".format(expire_s))

            if soon > expire_d:
                print(
                    "Your swift token will expire soon. "
                    "You might create a new one with swift-token new. "
                )

            if opt == "new":
                print(
                    (
                        "Please type {} ~/.swiftenv".format(
                            "." if is_sh_family() else "source"
                        )
                    )
                )

    except IOError:
        print(
            (
                "Error while reading environment variables in "
                "{}".format(os.path.expanduser("~/.swiftenv"))
            )
        )


if __name__ == "__main__":
    opt = sys.argv[1] if len(sys.argv) > 1 else None
    if opt == "new":
        create_token()
        info_token()
    elif opt == "info":
        info_token()
    else:
        print("Usage: python swift-token.py <new|info>")
