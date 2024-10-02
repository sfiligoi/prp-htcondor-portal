#
# Fetch OSGInstitutionID from k8s and set it as an env variable
# unless it is already set
#
if [ "x${OSG_INSTITUTION_ID}" == "x" ]; then
   OSG_INSTITUTION_ID=`/usr/sbin/kubectl get node ${PHYSICAL_HOSTNAME} -L nautilus.io/OSGInstitutionID | tail -1 | awk '{print $6}'`
   if [ "x${OSG_INSTITUTION_ID}" != "x" ]; then
      export OSG_INSTITUTION_ID
   fi
fi
