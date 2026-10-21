#!/bin/bash

HERE="$(cd "$(dirname "$0")" && pwd)"
KEY="$HOME/.ssh/lab_vm_key"
VM="vishnevskiy@192.168.64.5"
SSH="ssh -i $KEY -o IdentitiesOnly=yes -o BatchMode=yes"
SCP="scp -q -r -i $KEY -o IdentitiesOnly=yes"

$SSH $VM 'mkdir -p ~/lab7/scripts ~/lab7/tools ~/lab7/gui ~/lab7/config ~/lab7/logs ~/lab7/run ~/lab7/qgc' || exit 1
$SCP "$HERE"/scripts/* $VM:~/lab7/scripts/ || exit 1
$SCP "$HERE"/tools/* $VM:~/lab7/tools/ || exit 1
$SCP "$HERE"/gui/* $VM:~/lab7/gui/ || exit 1
$SCP "$HERE"/config/* $VM:~/lab7/config/ || exit 1
$SCP "$HERE/variant.env" $VM:~/lab7/ || exit 1
$SSH $VM 'chmod +x ~/lab7/scripts/*.sh ~/lab7/scripts/*.py ~/lab7/tools/*.py'
echo "Розгорнуто на $VM:~/lab7"
