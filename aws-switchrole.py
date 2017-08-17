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


# colors
class color:
  blue = '\033[94m'
  green = '\033[92m'
  yellow = '\033[93m'
  red = '\033[91m'
  bold = '\033[1m'
  underline = '\033[4m'
  normal = '\033[0m'

def print_color(color):
  # no pesky newlines when printing colour escape codes plz
  sys.stdout.write(color)
  sys.stdout.flush()

# given a list of config sections, return a list of those that look like profiles
def get_profiles(config_sections):
  profiles = []
  profile_pattern = re.compile('^profile (\w+)$')

  for section in config_sections:
    result = profile_pattern.search(section)
    if result:
      profiles.append(result.group(1))

  return profiles

def get_profile_choice(profiles):
  i = 0
  valid_choice = False

  print_color(color.yellow)
  print 'please choose your profile:'
  print_color(color.normal)

  for profile in profiles:
    print "  {}. {}".format((i + 1), profile)
    i += 1

  while not valid_choice:
    try:
      choice = int(raw_input("-> "))
    except ValueError:
      choice = 0

    if choice > 0 and choice < (len(profiles) + 1):
        print "nice"
        valid_choice = True
        return profiles[(choice - 1)]
    else:
      print_color(color.yellow)
      print 'please choose a valid value'
      print_color(color.normal)

  else:
    print_color(color.red)
    print "FATAL: couldn't find any profiles in '{}'".format(config_file)
    print_color(color.normal)
    sys.exit(1)


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

print_color(color.yellow)
print "Using profile '{}'".format(profile)
print_color(color.normal)


try:
  role = config.get("profile {}".format(profile), "role_arn")
except:
  print_color(color.red)
  print "FATAL: couldn't find profile '{}' in '{}'".format(profile, config_file)
  print_color(color.normal)
  sys.exit(1)

# give our role switch session a name and build our aws command
session = profile + '-' + time.strftime('%d%m%y%H%M%S')
cmd = [
  'aws', 'sts', 'assume-role',
  '--role-arn', role,             # Role ARN
  '--role-session-name', session, # Session ID given to temporary credentials
  '--profile', profile,           # Profile name from ~/.aws/config
]

process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
out, err = process.communicate()

# load the json response into a dict
try:
  creds = json.loads(out)
except:
  print_color(color.red)
  print 'Problem parsing response from AWS.  STDOUT and STDERR below:'
  print_color(color.yellow)
  print 'STDOUT:'
  print_color(color.normal)
  print out
  print_color(color.yellow)
  print 'STDERR:'
  print_color(color.normal)
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

  print_color(color.green)
  print "Got temporary credentials for profile '{}'".format(profile)
  print_color(color.normal)

  for k, v in env_vars.iteritems():
    print "export {}={}".format(k,v)

except:
  print_color(color.red)
  print 'Response from AWS did not contain expected values.  Dumping below:'
  print_color(color.normal)
  print creds
  sys.exit(1)
