define HELP
make requirements   - Install requirements in your virtualenv
endef

export HELP

all help:
	@echo "$$HELP"

clean:
	rm -rf .requirements.txt
	find . -name '*.pyc' -delete

requirements: .requirements.txt

.requirements.txt: requirements.txt
	pip install -r requirements.txt
	pip freeze > $@

release:
	python setup.py sdist upload -r internal