COMPOSE = docker compose --env-file .env --env-file .env.images

.PHONY: test config preflight build up corpus replay verify analyze queries down schema
test:
	PYTHONPATH=src python3 -m unittest discover -s tests -v
config:
	docker compose --env-file .env.example --env-file deployment/images.example.env config --quiet
preflight:
	python3 scripts/preflight.py --pull
build:
	$(COMPOSE) build
	python3 scripts/check_budget.py
up:
	$(COMPOSE) up -d opensearch rabbitmq dashboards setup adapter worker
corpus:
	$(COMPOSE) run --rm tools generate --root /data/corpus
replay:
	$(COMPOSE) run --rm tools adapter --root /data/corpus --state /data/adapter/checkpoints.sqlite --once --replay "manual-$$(date +%s)"
verify:
	mkdir -p artifacts
	$(COMPOSE) run --rm -T tools verify --oracle /data/corpus/oracle.json --state /data/worker/quarantine.sqlite --output - > artifacts/reconciliation.json
analyze:
	mkdir -p artifacts
	$(COMPOSE) run --rm -T tools analyze --oracle /data/corpus/oracle.json --output - > artifacts/analysis.json
queries:
	mkdir -p artifacts
	$(COMPOSE) run --rm -T tools queries --output - > artifacts/queries.json
schema:
	$(COMPOSE) run --rm tools validate-schema
down:
	$(COMPOSE) down
