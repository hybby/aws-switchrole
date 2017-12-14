#!/usr/bin/env python
# switchrole.py: a script to generate temporary credentials for aws roles.
# use it if you need environment variablised credentials for use with tools
# that don't support role switching (looking at you apex and terraform).
import os
import ConfigParser
import argparse
import time
import subprocess
import json
import sys
import re
from distutils.spawn import find_executable


# colors
class color:
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    bold = '\033[1m'
    underline = '\033[4m'
    normal = '\033[0m'


# print color codes that correspond with the above class
def print_color(color):
    sys.stdout.write(color)  # no pesky newlines plz
    sys.stdout.flush()


# red text and bomb out
def print_error(text):
    print_color(color.red)
    print text
    print_color(color.normal)
    sys.exit(1)


# yellow text
def print_warning(text):
    print_color(color.yellow)
    print text
    print_color(color.normal)


# green text
def print_ok(text):
    print_color(color.green)
    print text
    print_color(color.normal)


# blue text
def print_info(text):
    print_color(color.blue)
    print text
    print_color(color.normal)


# given a list of config sections, return ones that look like profiles
def get_profiles(config_sections):
    profiles = []
    profile_re = r'^profile ([A-Za-z0-9_-]+)$'
    profile_pattern = re.compile(profile_re)

    for section in config_sections:
        result = profile_pattern.search(section)
        if result:
            profiles.append(result.group(1))

    return sorted(profiles)


# given a list of profiles, ask the user to pick one and return that.
def get_profile_choice(profiles):
    i = 0
    valid_choice = False
    valid_profiles = []

    print_warning('please choose a profile to source role from:')

    if profiles:
        # loop through all profiles
        for profile in profiles:
            # make sure profile has a role_arn to assume
            if config.has_option("profile {}".format(profile), "role_arn"):
                role = config.get("profile {}".format(profile), "role_arn")
                print "  {}. {} ({})".format((i + 1), profile, role)
                valid_profiles.append(profile)
                i += 1
    else:
        print_error(
            "FATAL: couldn't find any profiles in '{}'".format(config_file)
        )

    while not valid_choice:
        try:
            choice = int(raw_input("-> "))
        except ValueError:
            choice = 0

        if choice > 0 and choice < (len(valid_profiles) + 1):
            valid_choice = True
            return valid_profiles[(choice - 1)]
        else:
            print_warning('please choose a valid value')


if __name__ == "__main__":
    # open our aws config file
    config_file = '~/.aws/config'
    config = ConfigParser.RawConfigParser()
    config.read(os.path.expanduser(config_file))
    profiles = get_profiles(config.sections())

    # parse command-line arguments
    parser = argparse.ArgumentParser(
        description='gets temporary credentials for switching to an aws role'
    )

    parser.add_argument(
        '--use-default',
        '--use-the-force',
        action='store_true',
        required=False,
        default=False,
        help='Use the default profile and credentials when assuing the role'
    )

    parser.add_argument(
        '--profile',
        type=str,
        required=False,
        help='profile in ~/.aws/config with role you want to switch to'
    )

    args = parser.parse_args()

    if args.profile:
        profile = args.profile
    else:
        profile = get_profile_choice(profiles)

    print_ok("using profile '{}'".format(profile))

    try:
        role = config.get("profile {}".format(profile), "role_arn")
    except:
        print_error(
            "FATAL: couldn't find a role_arn section in profile '{}'".format(
                profile,
                config_file
            )
        )

    # give our role switch session a name and build our aws command
    session = profile + '-' + time.strftime('%d%m%y%H%M%S')
    cmd = [
        find_executable('aws'), 'sts', 'assume-role',
        '--role-arn', role,              # Role ARN
        '--role-session-name', session,  # Session ID given to temp credentials
    ]

    if not args.use_default:
        cmd.append('--profile')
        cmd.append(profile) # Profile name from ~/.aws/config

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = process.communicate()

    # load the json response into a dict
    try:
        creds = json.loads(out)
    except:
        print_warning('problem parsing AWS response. STDOUT and STDERR below:')
        print_warning('STDOUT:')
        print out
        print_warning('STDERR:')
        print err
        sys.exit(1)

    # print out our returned values as export commands, ready to go.
    try:
        env_vars = {
            'AWS_ACCESS_KEY_ID': creds['Credentials']['AccessKeyId'],
            'AWS_SECRET_ACCESS_KEY': creds['Credentials']['SecretAccessKey'],
            'AWS_SESSION_TOKEN': creds['Credentials']['SessionToken'],
            'AWS_SECURITY_TOKEN': creds['Credentials']['SessionToken'],
        }

        print_ok("got temporary credentials for profile '{}'".format(profile))
        print_info(
            "---- load these vars into your env to assume profile's role ----"
        )

        for k, v in env_vars.iteritems():
            print " export {}={}".format(k, v)

        print_info(
            '----------------------------------------------------------------'
        )

    except:
        print_error('AWS response did not contain expected valuess. dumping:')
        print creds
        sys.exit(1)
