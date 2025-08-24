# FlowFoundry — developer Makefile
# Usage examples:
#   make help
#   make dev                # install in editable mode with dev + providers extras
#   make lint type test     # run static checks and tests
#   make serve              # run local API server
#   make ingest rag-local   # run example workflows
#   make build              # build sdist/wheel
#   make precommit          # run pre-commit hooks on all files

# ---- Config ---------------------------------------------------------------

PY ?= python3
PKG := flowfoundry

# Install extras for local dev. Override if you want fewer extras:
#   make dev EXTRAS="dev"
EXTRAS ?= dev,rag,rerank,qdrant

# Default query for the rag-local example
QUERY ?= "Summarize the refund policy."

# ---- Helpers --------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS":.*##"; printf "\n\033[1mTargets\033[0m\n"} /^[a-zA-Z0-9_.-]+:.*?##/ {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST); \
	echo ""

# ---- Environment / Install ------------------------------------------------

.PHONY: install
install: ## Install core (editable)
	$(PY) -m pip install -e .

.PHONY: dev
dev: ## Install editable with dev + provider extras (EXTRAS="$(EXTRAS)")
	$(PY) -m pip install -e ".[$(EXTRAS)]"

.PHONY: precommit-install
precommit-install: ## Install pre-commit hooks
	$(PY) -m pip install pre-commit
	pre-commit install

.PHONY: precommit
precommit: ## Run all pre-commit hooks on all files
	pre-commit run -a

# ---- Code quality ---------------------------------------------------------

.PHONY: lint
lint: ## Lint with ruff
	ruff check .

.PHONY: fmt
fmt: ## Format with ruff-format
	ruff format .

.PHONY: fmt-check
fmt-check: ## Check formatting (no changes)
	ruff format --check .

.PHONY: type
type: ## Type-check with mypy
	mypy src tests

.PHONY: qa
qa: lint fmt-check type ## Lint + format check + type check

# ---- Tests ----------------------------------------------------------------

.PHONY: test
test: ## Run tests
	pytest -q

.PHONY: test-cov
test-cov: ## Run tests with coverage
	pytest --cov=$(PKG) -q

# ---- Build / Clean --------------------------------------------------------

.PHONY: build
build: ## Build wheel and sdist
	$(PY) -m pip install --upgrade build
	$(PY) -m build

.PHONY: clean
clean: ## Remove caches and build artifacts
	rm -rf \
	  .pytest_cache .mypy_cache .ruff_cache \
	  __pycache__ */__pycache__ src/**/__pycache__ \
	  .coverage htmlcov \
	  build dist *.egg-info \
	  .ff_chroma

# ---- CLI / API ------------------------------------------------------------

.PHONY: serve
serve: ## Start local FastAPI server (uvicorn)
	$(PY) -m flowfoundry.cli serve

.PHONY: schema
schema: ## Write workflow JSON Schema to schema.json
	$(PY) -m flowfoundry.cli schema schema.json
	@echo "Wrote schema.json"

# ---- Examples -------------------------------------------------------------

.PHONY: ingest
ingest: ## Run examples/ingestion.yaml to index docs/sample.pdf
	$(PY) -m flowfoundry.cli run examples/ingestion.yaml

.PHONY: rag-local
rag-local: ## Run examples/rag_local.yaml with QUERY (override with: make rag-local QUERY="...")
	$(PY) -m flowfoundry.cli run examples/rag_local.yaml --state '{"query": $(QUERY)}'

.PHONY: rag-agentic
rag-agentic: ## Run examples/rag_agentic.yaml with QUERY
	$(PY) -m flowfoundry.cli run examples/rag_agentic.yaml --state '{"query": $(QUERY)}'

# ---- Meta -----------------------------------------------------------------

.PHONY: all
all: qa test ## Run quality gates and tests
