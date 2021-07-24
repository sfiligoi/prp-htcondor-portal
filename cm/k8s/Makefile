.PHONY: secret_pool

all: secret_pool

secret_pool:
	-kubectl delete secret prp-cm-secret -n htcondor-portal
	kubectl create secret generic prp-cm-secret -n htcondor-portal --from-file=POOL

