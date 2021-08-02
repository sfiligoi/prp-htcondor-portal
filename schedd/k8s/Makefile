.PHONY: secret_pool

all: secret_pool schedd_config

secret_pool:
	-kubectl delete secret prp-schedd-secret -n htcondor-portal
	kubectl create secret generic prp-schedd-secret -n htcondor-portal --from-file=prp-schedd.token

schedd_config:
	-kubectl delete configmap prp-schedd-config -n htcondor-portal
	kubectl create configmap prp-schedd-config -n htcondor-portal \
             --from-file=01-security.conf=config/01-security.conf \
             --from-file=10-security-multiuser-client.conf=config/10-security-multiuser-client.conf

