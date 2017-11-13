from __future__ import print_function

import argparse
import os
import random
import sys
import inquirer
import yaml

import boto3

__version__ = '1.9.0'

# If config file doesn't exist, create it with some defaults
if not os.path.exists(os.getenv("HOME") + '/.ssh-ec2.conf.yml'):
    print (os.getenv("HOME") + '/.ssh-ec2.conf.yml' + " doesn't exist.  Generating with defaults.")
    f = open(os.getenv("HOME") + '/.ssh-ec2.conf.yml', 'w')
    f.write("""
tags:
  environment:
    arg: -e
    tag: network_namespace
  roles:
    arg: -r
    tag: Roles
""")
    f.close() 

# Read config file
try:
    with open(os.getenv("HOME") + '/.ssh-ec2.conf.yml', 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
except:
    print ("The required file `~/.ssh-ec2.conf.yml` is broken.")
    print ("  Please delete the file and re-run the app to generate a new one)")
    exit(5);

parser = argparse.ArgumentParser(
    description="""
    SSH into an ec2 host where <tag-value> matches a tag which defaults to
    'Name' or environment variable EC2_HOST_TAG. In the case there is more than
    one such instance, one will be chosen at random. 'username' defaults to
    ubuntu.  A small bashrc file is added over ssh to give a nice prompt. Any
    extra arguments at the end are passed to ssh directly.
    """
)
parser.add_argument('-u', '--user', 
                    type=str,
                    default=os.getenv('EC2_SSH_USER', ""),
                    help="Which user to connect with, defaults to 'ubuntu'")
parser.add_argument('-i', '--interactive', 
                    action='store_true',
                    help="Interactively prompt to select for each tag filter")

# Dynamically load filter arguments from config
for tag in cfg['tags']:
    parser.add_argument(cfg['tags'][tag]['arg'], '--' + tag, 
                        type=str,
                        default=os.getenv('EC2_' + tag.upper()),
                        help= tag.upper() + " tag to match")

def main():
    args, unparsed = parser.parse_known_args()
    
    # Build the filters query
    applied_filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['running'],
        }
    ]

    # Initialize filters from arguments
    for cfg_tag in cfg['tags']:
        if vars(args)[cfg_tag]:
            applied_filters.append({
                'Name': 'tag:' + cfg['tags'][cfg_tag]['tag'],
                'Values': [vars(args)[cfg_tag]]
            })

    # Interactive mode:
    if args.interactive:
        for cfg_tag in cfg['tags']:
            if not vars(args)[cfg_tag]:
                applied_filters.append(add_filter_from_gui (applied_filters, cfg['tags'][cfg_tag]['tag']))

    # TODO: Let's be elegant about this:
    if args.user != "":
        username = args.user + "@"
    else:
        username = args.user

    # Go to selection screen
    host_name = get_host_name(applied_filters)

    if not host_name:
        print("ec2-ssh: no hosts matched", file=sys.stderr)
        sys.exit(1)

    command = [
        'ssh',
        '-t', '-t',
        username + host_name,
    ]

    # Add extra arguments to ssh command
    if unparsed:
        command.extend(unparsed)

    # Connect
    print("ec2-ssh connecting to {}".format(host_name), file=sys.stderr)
    sys.stdout.flush()
    os.execlp(*command)

def get_host_name(args):
    host_list = get_instance_list(args)

    if len(host_list) == 1:
        host = host_list[0]
        print ("There is only one host connecting to: ")
        print (host_list[0])
        print ()

    else:
        questions = [
                inquirer.List('host',
                    message="Which host?",
                    choices=host_list,
                ),
            ]
        host = inquirer.prompt(questions)["host"]
    return host[2]

def add_filter_from_gui (applied_filters, tag):
    options = get_list_of_filters(applied_filters, tag)
    if len(options) == 1:
        filter = options[0]
    else:
        questions = [
                inquirer.List('filter',
                    message="Which value from tag " + tag + "?",
                    choices=options,
                ),
            ]

        filter = ({
                'Name': 'tag:' + tag,
                'Values': [inquirer.prompt(questions)["filter"]]
            })
    return filter

def get_list_of_filters(filters, tag):
    conn = boto3.client('ec2')

    data = conn.describe_instances(Filters=filters)
    possible_values = []
    for reservation in data['Reservations']:
        for instance in reservation['Instances']:
            for ec2_tag in instance['Tags']:
                if ec2_tag['Key'] == tag:
                    if ec2_tag['Value'] not in possible_values:
                        possible_values.append(ec2_tag['Value'] or 'None')

    return sorted(possible_values)

def get_instance_list(filters):
    conn = boto3.client('ec2')

    data = conn.describe_instances(Filters=filters)
    instance_list = []
    for reservation in data['Reservations']:
        for instance in reservation['Instances']:
            instance_meta = []

            for cfg_tag in cfg['tags']:
                for ec2_tag in instance['Tags']:
                    if ec2_tag['Key'] == cfg['tags'][cfg_tag]['tag']:
                        instance_meta.append(ec2_tag['Value'] or 'None')

            # IP address last
            instance_meta.append(instance['PrivateIpAddress'])

            # Add to instance_list
            instance_list.append(instance_meta)
    return sorted(instance_list)


if __name__ == '__main__':
    main()
