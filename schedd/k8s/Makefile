.PHONY: secret_pool

all: secret_pool

secret_pool:
	-kubectl delete secret prp-schedd-secret -n htcondor-portal
	kubectl create secret generic prp-schedd-secret -n htcondor-portal --from-file=prp-schedd.token

