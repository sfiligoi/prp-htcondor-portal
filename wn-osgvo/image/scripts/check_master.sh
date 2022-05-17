#!/bin/bash

#
#  Wait until condor is first terminated
#   $1 provides initial wait time, to give time to initialization to do its job
#   $2 is the wait time between checks
#

wait "$1"

awk '/CondorVersion/{split($3,a,":"); split(a[2],b,")"); print b[1]}' /pilot/log/MasterLog > /root/master_pids.txt
npids=`cat /root/master_pids.txt | wc -l`

if [ $npids -lt 1 ]; then
  echo "condor_master log empty, unexpected" 1>&2
  exit 1
fi
if [ $npids -gt 1 ]; then
  echo "condor_master restrated at first step" 1>&2
  exit 1
fi

orgpid=`cat /root/master_pids.txt`

nprocs=`ps $orgpid |grep condor_master |wc -l`
if [ $nprocs -ne 1 ]; then
  echo "condor_master not running at first step" 1>&2
  exit 1
fi


while [ 0 -eq 0 ]; do 
  sleep "$2"

  rm -f /root/master_pids.txt
  awk '/CondorVersion/{split($3,a,":"); split(a[2],b,")"); print b[1]}' /pilot/log/MasterLog > /root/master_pids.txt
  npids=`cat /root/master_pids.txt | wc -l`

  if [ $npids -lt 1 ]; then
    echo "condor_master log empty, unexpected after first step" 1>&2
    exit 1
  fi

  if [ $npids -gt 1 ]; then
    echo "condor_master restrated" 1>&2
    break
  fi

  if [ $nprocs -ne 1 ]; then
    echo "condor_master not running" 1>&2
    break
  fi
done

echo "`date` End of condor_master"

echo "=== tail /pilot/log/MasterLog"
tail -100 /pilot/log/MasterLog

echo "=== tail /pilot/log/StartLog"
tail -100 /pilotl/log/StartLog

echo "========= startd_history ============="
cat /pilot/log/startd_history
echo "========== end history  =============="


exit 0

