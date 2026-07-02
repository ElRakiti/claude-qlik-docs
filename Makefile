# Thin wrapper around tasks.py — convenience for macOS / Linux / WSL users.
# Native Windows users: invoke `python tasks.py <target>` directly (or
# `uv run python tasks.py <target>`) — same targets, identical behaviour.

.PHONY: help crawl cluster topics index validate build test clean fresh \
        cc-install cc-uninstall chat-bundle project-bundle doctor

PY := uv run python tasks.py

help:
	@$(PY) help
	@echo
	@echo "Build pipeline (run in order, or use 'make fresh'):"
	@echo "  make crawl          — full crawl from help.qlik.com (~30 min)"
	@echo "  make cluster        — cluster raw pages into topics"
	@echo "  make topics         — build distilled topic.md files"
	@echo "  make index          — build skill index + per-group sub-indexes"
	@echo "  make validate       — validate citations + crawl manifest"
	@echo "  make build          — cluster + topics + index + validate"
	@echo
	@echo "Distribution targets — pick the surface you need:"
	@echo "  make cc-install     — Claude Code: link skill into ~/.claude/skills/"
	@echo "  make cc-uninstall   — Claude Code: remove link"
	@echo "  make chat-bundle    — Claude Chat Skill (slash + auto): dist/qlik-talend-chat.zip"
	@echo "  make project-bundle — Claude Project Knowledge: dist/qlik-talend-project/"
	@echo
	@echo "Convenience:"
	@echo "  make fresh          — wipe outputs, recrawl, rebuild, cc-install"
	@echo "  make clean          — wipe build artefacts (keeps raw mirror)"
	@echo "  make test           — run unit tests (no network, ~1s)"
	@echo "  make doctor         — check for drift after a pull (config vs build vs install)"

crawl:          ; @$(PY) crawl
cluster:        ; @$(PY) cluster
topics:         ; @$(PY) topics
index:          ; @$(PY) index
validate:       ; @$(PY) validate
build:          ; @$(PY) build
test:           ; @$(PY) test
cc-install:     ; @$(PY) cc-install
cc-uninstall:   ; @$(PY) cc-uninstall
chat-bundle:    ; @$(PY) chat-bundle
project-bundle: ; @$(PY) project-bundle
fresh:          ; @$(PY) fresh
clean:          ; @$(PY) clean
doctor:         ; @$(PY) doctor
