.PHONY: test/acceptance


lint/pycodestyle:
	@pipenv run python -m pycodestyle \
		--max-line-length=120 \
		.

test/acceptance:
	@pipenv run pytest acceptance