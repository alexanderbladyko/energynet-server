.PHONY: requirements
requirements:
	pip install -r etc/requirements.txt

.PHONY: requirements
dev_requirements:
	pip install -r etc/requirements.dev.txt

.PHONY: dev_up
dev_up:
	ansible-playbook -i ansible/hosts ansible/playbook.yaml

.PHONY: dev_down
dev_down:
	docker stop energynet_redis && docker stop energynet_postgres
