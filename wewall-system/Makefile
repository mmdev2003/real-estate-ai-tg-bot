.PHONY: deploy build-all stop-all update-all rebuild-all
.PHONY: rebuild-app stop-app
.PHONY: rebuild-monitoring stop-monitoring
.PHONY: rebuild-db stop-db
.PHONY: set-dev-env set-prod-env set-env-to-config-template
.PHONY: tg-parsing calc-sale-offer-irr m2data-parsing trend-agent-parsing pdf-analysis

set-dev-env:
	@export $(cat env/dev/.env env/dev/.env.app env/dev/.env.db env/dev/.env.monitoring | xargs)

set-prod-env:
	@export $(cat env/prod/.env env/prod/.env.app env/prod/.env.db env/prod/.env.monitoring | xargs)

set-env-to-config-template:
	@envsubst < ${WEWALL_LOKI_CONFIG_FILE}.template > ${WEWALL_LOKI_CONFIG_FILE}
	@envsubst < ${WEWALL_MONITORING_REDIS_CONFIG_FILE}.template > ${WEWALL_MONITORING_REDIS_CONFIG_FILE}
	@envsubst < ${WEWALL_TEMPO_CONFIG_FILE}.template > ${WEWALL_TEMPO_CONFIG_FILE}
	@envsubst < ${WEWALL_OTEL_COLLECTOR_CONFIG_FILE}.template > ${WEWALL_OTEL_COLLECTOR_CONFIG_FILE}
	@envsubst < ${WEWALL_GRAFANA_DATASOURCES}.template > ${WEWALL_GRAFANA_DATASOURCES}

deploy:
	@cd ..
	@git clone git@github.com:mmdev-wewall/wewall-tg-bot.git
	@git clone git@github.com:mmdev-wewall/wewall-chat.git
	@git clone git@github.com:mmdev-wewall/wewall-estate-calculator.git
	@git clone git@github.com:mmdev-wewall/wewall-estate-expert.git
	@git clone git@github.com:mmdev-wewall/wewall-estate-search.git
	@git clone git@github.com:mmdev-wewall/wewall-admin-tg-bot.git
	@cd wewall-system
	@./infrastructure/nginx/install.sh
	@./infrastructure/docker/install.sh
	@mkdir -p volumes/{grafana,loki,tempo,redis,postgresql,victoria-metrics}
	@mkdir -p volumes/redis/wewall-monitoring
	@mkdir -p volumes/weed
	@mkdir -p volumes/postgresql/{wewall-tg-bot,wewall-chat,wewall-estate-calculator,wewall-estate-expert,wewall-estate-search,wewall-admin-tg-bot,wewall-grafana}
	@chmod -R 777 volumes

build-all: set-env-to-config-template
	@docker compose -f ./docker-compose/db.yaml up -d --build
	sleep 20
	@docker compose -f ./docker-compose/apps.yaml up -d --build
	sleep 20
	@docker compose -f ./docker-compose/monitoring.yaml up -d --build

stop-all:
	@docker compose -f ./docker-compose/monitoring.yaml down
	@docker compose -f ./docker-compose/apps.yaml down
	@docker compose -f ./docker-compose/db.yaml down

update-all:
	@git pull
	@cd ../wewall-tg-bot/ && git pull && cd ../wewall-system/
	@cd ../wewall-estate-expert/ && git pull && cd ../wewall-system/
	@cd ../wewall-estate-search/ && git pull && cd ../wewall-system/
	@cd ../wewall-estate-calculator/ && git pull && cd ../wewall-system/
	@cd ../wewall-chat/ && git pull && cd ../wewall-system/
	@cd ../wewall-admin-tg-bot/ && git pull && cd ../wewall-system/

rebuild-all: update-all build-all

rebuild-app: update-all set-env-to-config-template
	@docker compose -f ./docker-compose/apps.yaml up -d --build

stop-app:
	@docker compose -f ./docker-compose/apps.yaml down

stop-monitoring:
	@docker compose -f ./docker-compose/monitoring.yaml down

stop-db:
	@docker compose -f ./docker-compose/db.yaml down

rebuild-monitoring: update-all set-env-to-config-template
	@docker compose -f ./docker-compose/monitoring.yaml down
	@docker compose -f ./docker-compose/monitoring.yaml up -d --build

rebuild-db: update-all set-env-to-config-template
	@docker compose -f ./docker-compose/db.yaml down
	@docker compose -f ./docker-compose/db.yaml up -d --build

tg-parsing: update-all
	@docker compose -f docker-compose/script.yaml up --build wewall-estate-expert-tg-parsing

calc-sale-offer-irr: update-all
	@docker compose -f docker-compose/script.yaml up --build wewall-estate-search-calc-sale-offer-irr

m2data-parsing: update-all
	@docker compose -f docker-compose/script.yaml up --build wewall-estate-search-parsing-m2data

trend-agent-parsing: update-all
	@docker compose -f docker-compose/script.yaml up --build wewall-estate-search-parsing-trend-agent

pdf-analysis: update-all
	@docker compose -f docker-compose/script.yaml up --build wewall-estate-expert-pdf-analysis