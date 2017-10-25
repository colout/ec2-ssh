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

Summary
-------

The ec2-ssh client allows you to filter on pre-configured ec2 tags with some level of interactivity (rather than ssh'ing to an IP address or hostname directly).

Why?
----

The original code from YPlan (although more useful than vanilla ssh) could only filter on a single tag specified in commandline arguments.  In the case of servers as cattle, ec2 instances are often part of environments and have roles (and would be tagged accordingly).  These tags are usually static and don't change (*Role* and *Environment* tags for example), so preconfiguring them can save precious keystrokes.  

Secondly, a single AWS account supporting multiple enviornments is becoming increasingly common (you don't want to ssh to an "appserver" picked at random from Dev, QA, Prod, Staging, etc).  Filtering by an arbitrary number of tags and removing the randomizer (temporarily) makes this a very powerful cattle herding tool.  

Configuration:
--------------
The YAML configuration file lives in `/.ssh-ec2.conf.yml` and is generated automatically on the first run if it doesn't exist.  
The each item in the `tags:` tree defines arguments and a tag to filter it on:

.. code-block:: yaml

  tags:
    environment:
      arg: -e
      tag: network_namespace
    roles:
      arg: -r
      tag: Roles
      
In this example:
  * `environment:` is the longform argument (`--environment`)
  * `-e` is the shortform argument
  * `network_namespace` is the EC2 tag to search:

Since tags are evaluated in order (especially in fully-interactive mode), it is a good idea to put more general filters first. 

Usage: Interactive Mode:
------------------------
Using the default config (above), if the command `$ ssh-ec2 -i` will bring you into interactive mode:

Select the Environment:

.. code-block:: bash

    $ ssh-ec2 -i
    [?] Which value from tag network_namespace?: staging
       production
     > staging

Select the Role:

.. code-block:: bash

    [?] Which value from tag Role?: appserver
     > appserver
       database

Select the host:

.. code-block:: bash

    [?] Which host?: ['staging', 'appserver', '10.11.7.186']
     > ['staging', 'appserver', '10.11.7.186']
       ['staging', 'appserver', '10.11.0.140']
       
    ec2-ssh connecting to 10.11.7.186

*Tip: You can also add tag filtering in the commandline arguments to skip a prompt*

Usage: Semi-interactive Mode:
-----------------------------
*TODO: Come up with a better name for this mode*

By using semi-interactive mode, you won't be prompted to fill in the filter tags.  Specify all filter tags via commandline arguments, and all hosts that match that query are listed immediately.  
 
List all instances in the "staging" environment and choose one to ssh to:

.. code-block:: bash

    $ ec2-ssh -e staging
    [?] Which host?: ['staging', 'appserver', '10.11.7.186']
     > ['staging', 'appserver', '10.11.7.186']
       ['staging', 'appserver', '10.11.0.140']
       ['staging', 'database', '10.11.0.15']

    ec2-ssh connecting to 10.11.7.186

List all "appserver" instances regardless of environment and choose one to ssh to:

.. code-block:: bash

    $ ec2-ssh -r appserver
    [?] Which host?: ['staging', 'appserver', '10.11.7.186']
     > ['staging', 'appserver', '10.11.7.186']
       ['staging', 'appserver', '10.11.0.140']
       ['production', 'appserver', '10.12.0.41']

    ec2-ssh connecting to 10.11.7.186

SSH into the "database" instance in the "staging" environment (no selection screen since it's the only one):

.. code-block:: bash

    $ ec2-ssh -e production -r appserver
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
  * Add a "random" tag that chooses a random server rather than prompting.  

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