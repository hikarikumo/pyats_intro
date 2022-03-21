#!/usr/bin/python -tt
# Project: pyats


from __future__ import absolute_import, division, print_function

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "4/25/20"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

from genie.testbed import load
import json
import os
import re
from git import Repo


def print_repository_info(repo):
    print('Repository description: {}'.format(repo.description))
    print('Repository active branch is {}'.format(repo.active_branch))

    for remote in repo.remotes:
        print('Remote named "{}" with URL "{}"'.format(remote, remote.url))

    print('Last commit for repository is {}.'.format(
        str(repo.head.commit.hexsha)))


def print_commit_data(commit):
    print('-----')
    print(str(commit.hexsha))
    print("\"{}\" by {} ({})".format(commit.summary,
          commit.author.name, commit.author.email))
    print(str(commit.authored_datetime))
    print(str("count: {} and size: {}".format(commit.count(), commit.size)))


def main():
    """
    This first pyATS Genie script instantiates the devnet_sbx_testbed.yml Testbed file which has two DevNet Always On
    Sandbox devices.   It then establishes a connection to each device and executes a show command ("show version").
    All of this is hardcoded and there is lots of code repetition but this first script is intended to show the basics
    without alot of "extras" or flexibility.
    :return:
    """
    output_dir = 'outputs'
    try:
        os.makedirs(output_dir)
    except OSError as e:
        pass

    # Instantiate the Testbed
    testbed = load('hikari-testbed001.yaml')
    print(f"\n======= TESTBED INFO =======\n")
    print(f"\tTestbed Value (object): {testbed}")
    print(f"\n======= END TESTBED INFO =======\n")


    # Sandbox NXOS Device
    # CLI: genie parse "show version" --testbed-file "devnet_sbx_testbed.yml" --devices "nxos0"
    # This CLI command outputs the results into a directory called "out1" which does not have to exist
    # CLI & SAVE: genie parse "show version" --testbed-file "devnet_sbx_testbed.yml" --devices "nxos0" --output PRE
    # DIFF CLI:  genie diff PRE POST
    
    # netdev = 'nxos0'
    command = 'show ip interface vrf all'
    
    devices = testbed.devices
    devices.connect()
    response = devices.parse(command)

    regexp_convert_cmd_to_slug = re.sub(r'\s','_', command)

    # nxos0 = devices.get('nxos0')
    netdev = devices.get('nxos0')

    output_path = '../network-lab-git-as-iac'
    if not os.path.exists(f'{output_path}/{netdev}'):
        os.makedirs(f'{output_path}/{netdev}')

    os.environ.update({"CFG_REPO_PATH": "/home/hikari/git/network-lab-git-as-iac/"})
    cfg_repo_path = os.environ.get("CFG_REPO_PATH")
    repo = Repo(cfg_repo_path)
    if not repo.bare:
        print(f'Repo at {cfg_repo_path} successfully loaded.')
        print_repository_info(repo)

    with open(f'{output_path}/{netdev}/{regexp_convert_cmd_to_slug}.json', 'w') as netdev_cfg:
        json.dump(response, netdev_cfg)
    assert os.path.isdir(cfg_repo_path)

    repo.git.add(all=True)
    repo.index.commit(f'Added new data from {netdev} via {regexp_convert_cmd_to_slug}')
    repo.commit()

    repo.remote().push()
    # # r1 IOS-XE
    # # CLI: genie parse "show version" --testbed-file devnet_sbx_testbed.yml --devices "R1"
    # netdev = 'R1'
    # device = testbed.devices[netdev]
    # device.connect()
    # response = device.parse('show running-config')
    # print(f"\nResponse from {netdev} is of type {type(response)} and length {len(response)}")
    # print(response)
    # print()
    # print(json.dumps(response, indent=4))
    # print(response.keys())
    # with open(f'outputs/{netdev}.yaml', 'w') as netdev_cfg:
    #     yaml.safe_dump(json.dumps(response), netdev_cfg, allow_unicode=True)

# Standard call to the main() function.
if __name__ == '__main__':
    main()
