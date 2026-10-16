# ============================================================
#  polymarket-signals — Makefile (point d'entrée unique)
#  make help  → liste des commandes, groupées par section (##@)
# ============================================================

.DEFAULT_GOAL := help
SHELL         := /bin/bash
.SHELLFLAGS   := -eu -o pipefail -c

# Deux espaces de données séparés : on ne mélange JAMAIS fixtures et données réelles
DATA_DIR      ?= $(abspath data)
DEMO_DIR      := $(abspath data-demo)
override DATA_DIR := $(abspath $(DATA_DIR))  # chemins absolus : les vues silver les mémorisent
WEB_DIR       := web
DBT            = cd transform && POLYSIGNALS_DATA_DIR=$(DATA_DIR) uv run dbt
CLI            = POLYSIGNALS_DATA_DIR=$(DATA_DIR) uv run polysignals

.PHONY: help
help: ## Affiche cette aide
	@awk 'BEGIN {FS = ":.*##"; printf "\n  \033[1mpolymarket-signals\033[0m · lecture seule, pédagogique\n"} \
		/^##@/ { printf "\n  \033[36m── %s\033[0m\n", substr($$0, 5) } \
		/^[a-zA-Z0-9_-]+:.*##/ { printf "  \033[32mmake %-14s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

##@ Installation

.PHONY: install
install: ## Installe les dépendances Python (uv) et web (npm, sans scripts d'installation)
	uv sync --locked
	cd $(WEB_DIR) && npm ci --ignore-scripts --no-fund --no-audit
	@echo "✓ Prêt. Essaie : make demo"

##@ Pipeline (bronze → silver → gold)

.PHONY: demo
demo: DATA_DIR = $(DEMO_DIR)
demo: ## 🎓 Pipeline complet HORS LIGNE (données synthétiques, dans data-demo/) + tableau de bord
	$(CLI) ingest --source fixtures
	$(DBT) build --profiles-dir . --quiet
	$(CLI) watchlist

.PHONY: ingest
ingest: ## Ingestion live (API publiques Polymarket) → bronze
	$(CLI) ingest --source live

.PHONY: build
build: ## Transformations dbt + tous les tests de données (silver, gold)
	$(DBT) build --profiles-dir .

.PHONY: pipeline
pipeline: ingest build ## 🚀 Ingestion live + build (la commande du quotidien)

.PHONY: rebuild
rebuild: ## Reconstruit l'entrepôt de zéro à partir de la couche bronze
	rm -f $(DATA_DIR)/warehouse.duckdb
	$(MAKE) build

##@ Site web (export statique)

.PHONY: web-data
web-data: ## Exporte la couche gold vers web/data/gold.json (après make build ou make demo)
	$(CLI) export --out $(WEB_DIR)/data/gold.json --run-results transform/target/run_results.json

.PHONY: web-demo
web-demo: demo ## 🌐 Site sur données synthétiques → http://localhost:3100
	$(MAKE) web-data DATA_DIR=$(DEMO_DIR)
	cd $(WEB_DIR) && npm run dev

.PHONY: web-dev
web-dev: web-data ## Site sur les données de data/ → http://localhost:3100
	cd $(WEB_DIR) && npm run dev

.PHONY: web-build
web-build: ## Build statique du site (web/out)
	cd $(WEB_DIR) && NEXT_TELEMETRY_DISABLED=1 npm run build

##@ Comprendre

.PHONY: watchlist
watchlist: ## Tableau de bord des marchés macro suivis
	$(CLI) watchlist

.PHONY: explain
explain: ## Explication pas à pas d'un marché  →  make explain M=<slug> [DATA_DIR=data-demo]
ifndef M
	$(error ❌  Indique un marché : make explain M=fed-cut-25-dec-2026 (voir make watchlist))
endif
	$(CLI) explain $(M)

.PHONY: docs
docs: ## Documentation dbt (lignage bronze → gold) sur http://localhost:8080
	$(DBT) docs generate --profiles-dir . --quiet
	$(DBT) docs serve --profiles-dir . --port 8080

##@ Exploitation

.PHONY: doctor
doctor: ## Diagnostic réseau (DNS, TLS, blocage ANJ)
	$(CLI) doctor

.PHONY: runs
runs: ## Derniers runs d'ingestion
	$(CLI) runs

.PHONY: contracts
contracts: ## Enregistrements bronze qui violent leur contrat
	$(CLI) contracts

.PHONY: tags
tags: ## Tags Gamma disponibles (choisir la watchlist)  →  make tags Q=fed
	$(CLI) tags $(if $(Q),--search $(Q),)

##@ Qualité (make check = exactement la CI)

.PHONY: lint
lint: ## Ruff (lint + format), mypy strict, workflows GitHub (actionlint)
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy
	uvx --from actionlint-py==1.7.12.25 actionlint

.PHONY: format
format: ## Formate et corrige automatiquement
	uv run ruff check --fix .
	uv run ruff format .

.PHONY: test
test: ## Tests unitaires + bout en bout (fixtures → dbt build)
	uv run pytest

.PHONY: audit
audit: ## Vulnérabilités connues des dépendances installées (pip-audit, base PyPI/OSV)
	uv run pip-audit --skip-editable --progress-spinner off

.PHONY: check-web
check-web: ## Site : lint, types, build sur données de démo, audit npm
	rm -rf $(abspath .check-data)
	$(MAKE) -s demo DEMO_DIR=$(abspath .check-data) >/dev/null
	$(MAKE) -s web-data DATA_DIR=$(abspath .check-data)
	cd $(WEB_DIR) && npm run lint && npm run type-check
	$(MAKE) web-build
	cd $(WEB_DIR) && npm audit --omit=dev --audit-level=high
	rm -rf $(abspath .check-data)

.PHONY: check
check: lint test audit check-web ## ✅ Tout vérifier, comme la CI

##@ Nettoyage

.PHONY: clean
clean: ## Supprime caches et artefacts (garde les données)
	rm -rf .pytest_cache .ruff_cache .mypy_cache transform/target transform/logs .check-data
	rm -rf $(WEB_DIR)/.next $(WEB_DIR)/out
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +

.PHONY: clean-data
clean-data: ## ⚠️  Supprime TOUTES les données locales (bronze compris)
	@read -p "Taper 'supprimer' pour effacer $(DATA_DIR) et $(DEMO_DIR) : " ans && [ "$$ans" = "supprimer" ]
	rm -rf $(DATA_DIR) $(DEMO_DIR)
