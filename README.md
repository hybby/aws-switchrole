## aws-switchrole
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

optionally the '--copy' option will cvopy the exports to the clipboard automatically


### installation
  1. clone this repo
  2. make sure you have [`aws-cli`](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) installed:

  ```
  pip install awscli --upgrade --user
  ```

  3. ensure your `~/.aws/credentials` and `~/.aws/config` files are configured.  i use the latter for profiles:

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

  3. set up an alias or symlink to the script.  for example:

  ```
  # create a shell alias (remember to add to your dotfiles!)
  alias aws-switchrole="${HOME}/git/aws-switchrole/aws-switchrole.py"

  # or alternatively, symlink it to a place in your $PATH (i use `${HOME}/bin` for this)
  ln -s ${HOME}/git/aws-switchrole/aws-switchrole.py ${HOME}/bin/aws-switchrole`
  ```
