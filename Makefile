COMPOSE = docker compose --env-file .env --env-file .env.images
RATE ?= 10
DURATION ?= 120
SCENARIO ?= mixed
INCIDENT_RATE ?= 0.1
SEED ?=
LIVE_CONTAINER = $(if $(COMPOSE_PROJECT_NAME),$(COMPOSE_PROJECT_NAME),alma-poc)-live-source

.PHONY: test config preflight build up corpus replay verify analyze queries down schema live live-stop
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
live:
	$(MAKE) up
	$(MAKE) corpus
	$(COMPOSE) run --rm --name "$(LIVE_CONTAINER)" tools stream --root /data/corpus --oracle /data/corpus/oracle.json --rate "$(RATE)" --seconds "$(DURATION)" --scenario "$(SCENARIO)" --incident-rate "$(INCIDENT_RATE)" $(if $(SEED),--seed "$(SEED)")
live-stop:
	docker stop "$(LIVE_CONTAINER)"
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
