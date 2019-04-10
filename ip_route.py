#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Jason Williams <uberlinuxguy@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ip_route
short_description: Manage routes via the 'ip route' command
version_added: historical
description:
     - The C(ip_route) module attempts to manage static routes via the 'ip_route' command
options:
  prefix:
    description:
      - The ip prefix in CIDR format to add
    required: yes
  next_hop:
    description:
      - The IP of the host that the prefix will be reachable by
    required: yes
  state: 
    description: 
      - Should the route be 'present' (default) or 'absent'
author:
    - Jason Williams
'''

EXAMPLES = r'''
- name: Add a route for 192.168.0.0/16 via 10.1.2.3
  ip_route:
    prefix: 192.168.0.0/16
    next_hop: 10.1.2.3
    state: present 

- name: Remote a route for 10.99.0.0/16 that points to 172.16.0.1
  ip_route: 
    prefix: 10.99.0.0/16
    next_hop: 172.16.0.1
    state: absent
  
'''

RETURN = r'''
'''

import datetime
import glob
import os
import shlex

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
from ansible.module_utils.common.collections import is_iterable


def check_route(module, prefix, next_hop, present):
    # TODO: check if the route is in state 'present'(bool) and return true if it is
    # TODO: and false if the state is not in the requested state.
    # ip route list 10.0.0.0/8 via 10.99.130.1
    args = '/sbin/ip route list ' + prefix + ' via ' + next_hop
    rc, out, err = module.run_command(args, executable=None, use_unsafe_shell=False, encoding=None)
    module.log('Ran: ' + args)
    if rc != 0 :
        # TODO: return an ansible error.
        result = dict(
            stdout=out,
            stderr=err,
            rc=rc,
            changed=False,
        )
        module.fail_json(msg='non-zero return code', **result)
    else: 
        # see if we got any output.
        if out != "" and present: 
            module.log('Output was: ' + out + ' and present was set')
            return True
        else: 
            if out == "" and not present: 
                module.log('Output was: ' + out + ' and present was not set')
                return True
        return False

def main():

    module = AnsibleModule(
        argument_spec=dict(
            prefix=dict(required=True),
            next_hop=dict(required=True),
            state=dict(default='present', choices=['present', 'absent']),
        ),
        supports_check_mode=True,
    )
    prefix = module.params['prefix']
    next_hop = module.params['next_hop']
    state = True if module.params['state'] == 'present' else False
    rc = 0
    changed = False
    out = ""
    err = ""  

    if check_route(module, prefix, next_hop, state):
        # Route is already in the requested state, return unchanged OK.
        rc = 0
        changed = False
        stdout = "Route already in requested state."
        
    else: 
    

        # for check mode
        if not module.check_mode:
            action = 'add' if state else 'del'
            args = '/sbin/ip route ' + action + ' ' + prefix + ' via ' + next_hop 
            rc, out, err = module.run_command(args, executable=None, use_unsafe_shell=False, encoding=None)
            changed=True
        else:
            module.exit_json(msg="skipped, running in check mode", skipped=True)



    result = dict(
        stdout=out,
        stderr=err,
        rc=rc,
        changed=changed,
    )

    if rc != 0:
        module.fail_json(msg='non-zero return code', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
