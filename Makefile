lint: bandit black flake8 isort

bandit:
	pipenv run bandit -r dsaps

black:
	pipenv run black --check --diff dsaps tests

coveralls: test
	pipenv run coveralls

flake8:
	pipenv run flake8 dsaps tests

isort:
	pipenv run isort dsaps tests --diff

test:
	pipenv run pytest --cov=dsaps
