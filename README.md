# aws-switchrole
a script to generate temporary credentials for aws roles.

use it if you need environment variablised credentials for use with tools
that don't support role switching (looking at you apex).


### usage
provide a profile name that you have configured in `~/.aws/config`

```
$ aws-switchrole.py --profile profile-name [--duration-seconds <secs>]
```

if you don't provide a profile, you'll be asked to pick from a list.

optionally, provide a period of time you'd like the generated credentials
to be valid for, in seconds (`--duration-seconds`).  the minimum is 15 mins
(900s).  the maximum is 12 hrs (43200).  an aws exception will be thrown if
this is not valid.  defaults to 1 hr (3600)

we then use the `role_arn` to perform an `aws sts assume-role` command and
print out the resultant credentials as `export` commands, ready for you to
use.  for example:

```
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_SESSION_TOKEN=xxx
export AWS_SECURITY_TOKEN=xxx
```

paste 'em into your shell and you're good to go for a while.  creds last for
one hour.  sadly we can't set up the environment from a child process, so copy
and pasting into your environment will have to do.

optionally the '--copy' option will copy the exports to the clipboard automatically


# Installation
  1. pip install aws-switchrole
  2. ensure your `~/.aws/credentials` and `~/.aws/config` files are configured.  i use the latter for profiles:

  ```
  $ cat ~/.aws/credentials
  [default]
  aws_access_key_id = XXX
  aws_secret_access_key = XXX
  ```

  ```
  $ cat ~/.aws/config
  [profile samplerole]
  output = json
  region = us-east-1
  role_arn = arn:aws:iam::${aws_account_id_with_target_role}:role/SampleRoleName
  mfa_serial = arn:aws:iam::${aws_account_id_with_iam_info}:mfa/your.iam.username
  source_profile = default
  ```

# Development

PRs welcome and encouraged.

Contributed code has to be compatible with python 2 and python 3

## Set up

* `mkvirtualenv aws-switchrole`
* `make requirements`


## Simulating package install

If you want to use the code as if it was installed in your virtualenv (for example to use the CLI tool while you develop):

* `pip install --editable .` , where `.` is the path to the folder containing `setup.py`
