.PHONY: requirements test quality

requirements:
	pip install -r requirements/travis.txt

test:
	@echo 'Tests are contained in edx-platform. See openedx/tests/xblock_integration/test_review_xblock.py for tests'

quality:
	tox -e quality
