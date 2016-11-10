#!/usr/bin/env python
# switchrole.py: a script to generate temporary credentials for aws roles.
# use it if you need environment variablised credentials for use with tools
# that don't support role switching (looking at you apex).
import os
import ConfigParser
import argparse
import time
import subprocess
import json
import sys

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

# parse command-line arguments
parser = argparse.ArgumentParser(
  description='gets temporary credentials for switching to an aws role'
)

parser.add_argument(
  '--profile',
  type=str,
  required=True,
  help='profile in ~/.aws/config with role you want to switch to'
)

args = parser.parse_args()
profile = args.profile
print_color(color.yellow)
print "Using profile '{}'".format(profile)
print_color(color.normal)

# read aws config and get role_arn from profile provided
config_file = '~/.aws/config'
config = ConfigParser.ConfigParser()
config.read(os.path.expanduser(config_file))

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
