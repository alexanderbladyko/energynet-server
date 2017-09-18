
.PHONY: up_dev_env
dev_up:
	ansible-playbook --ask-become-pass -i ansible/hosts ansible/playbook.yaml

.PHONY: up_dev_env
dev_down:
	docker stop energynet_redis && docker stop energynet_postgres
