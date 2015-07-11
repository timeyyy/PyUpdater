deps:
	pip install -r requirements.txt

deps-dev: deps-upgrade
	pip install -r dev/requirements.txt --upgrade

deps-upgrade:
	pip install -r requirements.txt --upgrade

deploy: pypi
	twine upload dist/*
	python dev/make.py remove-dist

deploy-docs:
	mkdocs build --clean
	python dev/move.py

pypi:
	python setup.py sdist bdist_wheel

pypi-test:
	python setup.py sdist upload -r pypitest

register:
	python setup.py register -r pypi

register-test:
	python setup.py register -r pypitest

test:
	python setup.py test

test-cover:
	python setup.py mytest

test-script:
	py.test --genscript=runtests.py
