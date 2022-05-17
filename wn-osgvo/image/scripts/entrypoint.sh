#!/bin/bash

# Allow the derived images to run any additional runtime customizations
for x in /etc/entrypoint/image-config.d/*.sh; do source "$x"; done

# properly cleanup on signal
trap 'echo signal received!; kill $(jobs -p); wait' SIGINT SIGTERM

export HOME=/pilot
su osg -p -c "/bin/entrypoint.osg.sh $@" &
myproc=$!

# protection in case it does not terminate oby itself when condor dies or restarts
(/bin/check_master.sh 300 1; kill ${myproc}; echo "`date` Sending kill") &


wait ${myproc}
rc=$?
echo "`date` entrypoint.osg.sh terminated with $rc"

exit 0
