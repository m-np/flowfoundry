# FlowFoundry — developer Makefile (functional-only)
# Usage:
#   make help
#   make dev                 # install editable w/ extras
#   make lint type test      # static checks + tests
#   make build               # sdist/wheel
#   make cli-list            # show discovered CLI strategies
#   make chunk index query compose  # quick CLI pipeline
#   make examples            # run python examples

# ---- Config -----------------------------------------------------------------

PY ?= python3
PKG := flowfoundry

# Install extras for local dev (override: make dev EXTRAS="dev")
EXTRAS ?= dev,rag,rerank,openai,llm-openai

# Demo index settings
INDEX_PATH ?= .ff_chroma
COLLECTION ?= docs
DOCS_DIR   ?= docs/samples
QUESTION   ?= What is people's budget?

# ---- Helpers ----------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS":.*##"; printf "\n\033[1mTargets\033[0m\n"} /^[a-zA-Z0-9_.-]+:.*?##/ {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST); \
	echo ""

# ---- Environment / Install ---------------------------------------------------

.PHONY: install
install: ## Install core (editable)
	$(PY) -m pip install -e .

.PHONY: dev
dev: ## Install editable with extras (EXTRAS="$(EXTRAS)")
	$(PY) -m pip install -e ".[$(EXTRAS)]"

.PHONY: precommit-install
precommit-install: ## Install & enable pre-commit hooks
	$(PY) -m pip install pre-commit
	pre-commit install

.PHONY: precommit
precommit: ## Run all pre-commit hooks on all files
	pre-commit run -a

# ---- Test ------------------------------------------------------

.PHONY: test
test: ## Run tests
	pytest -q

.PHONY: test-cov
test-cov: ## Run tests with coverage
	pytest --cov=$(PKG) --cov-report=term-missing -q

# ---- Build / Clean -----------------------------------------------------------

.PHONY: build
build: ## Build wheel + sdist
	$(PY) -m pip install --upgrade build
	$(PY) -m build

.PHONY: clean
clean: ## Remove caches and build artifacts
	rm -rf \
	  .pytest_cache .mypy_cache .ruff_cache \
	  __pycache__ */__pycache__ src/**/__pycache__ \
	  .coverage htmlcov \
	  build dist *.egg-info \
	  $(INDEX_PATH)

# ---- CLI convenience (auto-discovered commands) ------------------------------

.PHONY: cli-list
cli-list: ## List discovered families/strategies
	flowfoundry list

