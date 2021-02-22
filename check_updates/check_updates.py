#!/usr/bin/python

import json
import platform
import subprocess

PLUGIN_VERSION = "1"
HEARTBEAT="true"

data={}
data['plugin_version'] = PLUGIN_VERSION
data['heartbeat_required']=HEARTBEAT

command_check_dnf="type dnf"
command_yum="yum check-update --security | grep -i 'needed for security'"
command_dnf_security="dnf --refresh -q check-update --security |sed '/Obsoleting Packages/,$d' | grep . | wc -l"
command_dnf_all="dnf -q check-update |sed '/Obsoleting Packages/,$d' | grep . | wc -l"

command_check_unattended_upgrade="type unattended-upgrade"
command_debian_security="unattended-upgrade --dry-run 2>&1 | grep unpack | wc -l"
command_debian_all="(apt-get update && apt-get upgrade --dry-run) | grep '^Inst' | wc -l"

os_info = platform.linux_distribution()[0].lower()

def get_command_output(command):
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    return output

if 'centos' in os_info or 'red hat' in os_info:
        dnf = get_command_output(command_check_dnf)
        if dnf:
            out = get_command_output(command_dnf_security)
            if out:
                data['security_updates'] = out.split()[0]
            out = get_command_output(command_dnf_all)
            if out:
                data['packages_to_be_updated'] = out.split()[0]
        else:
            out = get_command_output(command_yum)
            if out:
                out = out.rstrip()
                count = out.split("needed for security")
                security_count = count[0].split()[0]
                if security_count == 'No':
                    data['security_updates'] = 0
                else:
                    data['security_updates'] = security_count
                packages_count = count[1].split()
                for each in packages_count:
                    if each.isdigit():
                        data['packages_to_be_updated']=each
                
else:
    unattended_upgrade = get_command_output(command_check_unattended_upgrade)
    if unattended_upgrade:
        out = get_command_output(command_debian_security)
        if out:
            data['security_updates'] = out.split()[0]
    out = get_command_output(command_debian_all)
    if out:
        data['packages_to_be_updated'] = out.split()[0]

print(json.dumps(data))
