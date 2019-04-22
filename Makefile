.PHONY: mb/install test/acceptance lint/pycodestyle test/test

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

test/test:
	@pipenv run python -m pytest tests


acceptance/test_flow_time/20190109-20190122-0-issues.json:
	@pipenv run python tools/query_with_mb.py \
		--out $@ \
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/09"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/10"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/11"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/14"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/15"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/16"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/17"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/18"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/20"'\
		'project=SCRUM3 and status was in ("In Progress") on "2019/01/21"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/09"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/10"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/11"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/14"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/15"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/16"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/17"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/18"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/20"'\
		'project=SCRUM3 and status changed to ("Done") on "2019/01/21"'


tests/daos/test_jira_dao/all-issues-in-scrum1.json:
	@pipenv run python tools/query_with_mb.py \
		--out $@ \
		'project=SCRUM1'
