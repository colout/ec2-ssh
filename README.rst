=======
ec2-ssh
=======

Forked from Instagram original code by YPlan.

Installation
------------

Clone from GitHub:

.. code-block:: bash

    git clone git@github.com:colout/ec2-ssh.git


Install the app:

.. code-block:: bash

    cd ec2-ssh
    python setup.py install


Usage
-----

This client allows you to filter on ec2 "Roles" or "Environment" tags (Rather than ssh'ing to an IP address or hostname directly).

List all instances in the "staging" environment and choose one to ssh to:

.. code-block:: bash

    ec2-ssh -e staging
    [?] Which host?: ['staging', 'appserver', '10.11.7.186']
     > ['staging', 'appserver', '10.11.7.186']
       ['staging', 'appserver', '10.11.0.140']
       ['staging', 'database', '10.11.0.15']

    ec2-ssh connecting to 10.11.7.186

List all "appserver" instances regardless of environment and choose one to ssh to:

.. code-block:: bash

    ec2-ssh -r appserver
    [?] Which host?: ['staging', 'appserver', '10.11.7.186']
     > ['staging', 'appserver', '10.11.7.186']
       ['staging', 'appserver', '10.11.0.140']
       ['production', 'appserver', '10.12.0.41']

    ec2-ssh connecting to 10.11.7.186

SSH into the "database" instance in the "staging" environment (no selection screen since it's the only one):

.. code-block:: bash

    ec2-ssh -e production -r appserver
    ec2-ssh connecting to 10.12.0.41

TODO
----

Configuration:
  * Explicitly configure arg_longform and arg_shortform in config
  * Heirarchy of assumptions
    - no longform?  assume tag name
    - no tag name? assume top level
    - no shortform?  take first letter
    - first letter is in use? iterate through longform
    - no free letters?  iterate through alphabet
  * Blacklist (fail) -h, -u, -i, --help, --user, --interactive
  * Greylist  (warn) on ssh command

Filters:
  * Interactive Mode
    - Allow "None" as an option for each tag list (nice to have)

Code Cleanup:
  * `if args.user != "":` <-- this needs to be cleaner
  * Make use of functions
  * Consistant naming convention for vars / functions
  * A Pythonic way to manage settings file.  
  * Fix the --help (-h) description
  * Scope variables (for instance calling arguments directly from functions)
  * No need for ec2-host. Create a dry-run flag to return only the IP address.  