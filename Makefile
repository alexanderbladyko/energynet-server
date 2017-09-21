.PHONY: requirements
requirements:
	pip install -r etc/requirements.txt

.PHONY: requirements
dev_requirements:
	pip install -r etc/requirements.dev.txt

.PHONY: environment_up
environment_up:
	ansible-playbook -i ansible/hosts ansible/playbook.yaml

.PHONY: environment_down
environment_down:
	docker stop energynet_redis && docker stop energynet_postgres

.PHONY: test
test:
	TEST=true nose2 $(test)

.PHONY: test_coverage
test_coverage:
	TEST=true nose2 --with-coverage --coverage-report html
