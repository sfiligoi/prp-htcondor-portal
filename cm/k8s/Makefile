.PHONY: secret_pool

all: secret_pool cm_confiig

secret_pool:
	-kubectl delete secret prp-cm-secret -n htcondor-portal
	kubectl create secret generic prp-cm-secret -n htcondor-portal --from-file=POOL

cm_config:
	-kubectl delete configmap prp-cm-config -n htcondor-portal
	kubectl create configmap prp-cm-config -n htcondor-portal \
             --from-file=01-security.conf=config/01-security.conf \
             --from-file=10-security-prp.conf=config/10-security-prp.conf

