#!/bin/bash

# Allow the derived images to run any additional runtime customizations
for x in /etc/entrypoint/image-config.d/*.sh; do source "$x"; done

export HOME=/pilot
su osg -p -c "/bin/entrypoint.osg.sh $@"
