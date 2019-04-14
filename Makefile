.PHONY: mb/install test/acceptance lint/pycodestyle

OUT ?= "config.json"

mb/install:
	@npm install


mb/query:
	@pipenv run python tools/query_with_mb.py --out $(OUT) '$(QUERY)'


lint/pycodestyle:
	@pipenv run python -m pycodestyle \
		--max-line-length=120 \
		.

test/acceptance:
	@pipenv run python -m pytest acceptance