.PHONY: test test-py test-ts eval ablations llm-eval llm-eval-live audit paper-tables clean clean-cache help

help:
	@echo "ASM Build & Experiment Targets"
	@echo ""
	@echo "  make test          Run all tests (Python + TypeScript)"
	@echo "  make test-py       Run Python scorer tests only"
	@echo "  make test-ts       Run TypeScript MCP server tests only"
	@echo "  make eval          Run A/B evaluation (Section 6.5)"
	@echo "  make ablations     Run ablation studies (Section 6.3a)"
	@echo "  make llm-eval      LLM-as-selector dry-run (no API calls)"
	@echo "  make llm-eval-live LLM-as-selector with live LLM (needs API key)"
	@echo "  make audit         Run MCP ecosystem audit (Section 2)"
	@echo "  make paper-tables  Generate paper tables from experiment results"
	@echo "  make clean         Remove cache artifacts"
	@echo "  make clean-cache   Remove raw-doc cache (large)"
	@echo ""

# ---------------------------------------------------------------------------
# Test targets
# ---------------------------------------------------------------------------

test: test-py test-ts
	@echo "[OK] All tests passed."

test-py:
	python -m pytest scorer/test_scorer.py -v

test-ts:
	cd registry && npx tsx src/test_scorer.ts
	cd registry && npx tsx src/test_topsis.ts

# ---------------------------------------------------------------------------
# Experiment targets
# ---------------------------------------------------------------------------

eval:
	python experiments/ab_test.py
	python experiments/analyze.py

ablations:
	python experiments/ablation_experiments.py --seed 2024

llm-eval:
	python experiments/expert_annotation/run_ranking_experiment.py \
	  --tasks-file experiments/expert_annotation/tasks_objective.yaml \
	  --dry-run

llm-eval-live:
	@if [ -z "$$DEEPSEEK_API_KEY" ] && [ -z "$$QWEN_API_KEY" ] && [ -z "$$KIMI_API_KEY" ]; then \
		echo "Error: set DEEPSEEK_API_KEY, QWEN_API_KEY, or KIMI_API_KEY"; \
		exit 1; \
	fi
	python experiments/expert_annotation/run_ranking_experiment.py \
	  --tasks-file experiments/expert_annotation/tasks_objective.yaml

audit:
	python experiments/mcp_ecosystem_audit.py

paper-tables:
	@echo "TODO: paper-tables script not yet wired;"
	@echo "tables are produced by individual experiment scripts above:"
	@echo "  make eval      -> Section 6.5 tables"
	@echo "  make ablations -> Section 6.3a tables"
	@echo "  make llm-eval  -> Section 6.7 tables"

# ---------------------------------------------------------------------------
# Clean targets
# ---------------------------------------------------------------------------

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -path "*/registry/node_modules" -exec rm -rf {} + 2>/dev/null || true
	@echo "[OK] Cleaned build artifacts."

clean-cache:
	rm -rf experiments/expert_annotation/cache/raw_docs
	@echo "[OK] Removed raw-doc cache."
