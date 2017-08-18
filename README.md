## aws-switchrole
a script to generate temporary credentials for aws roles.

use it if you need environment variablised credentials for use with tools
that don't support role switching (looking at you apex).


### usage
provide a profile name that you have configured in `~/.aws/config`

```
$ aws-switchrole.py --profile profile-name
```

if you don't provide a profile, you'll be asked to pick from a list.

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


### installation
  1. clone this repo
  2. set up an alias or symlink to the script.  for example:  
    a) `alias aws-switchrole="${HOME}/git/aws-switchrole/aws-switchrole.py"` (remember to put in your dotfiles)  
    b) `ln -s ${HOME}/git/aws-switchrole/aws-switchrole.py ${HOME}/bin/aws-switchrole`  
