# make lint and make test should be run here during development.
# They will also be called by Github actions on pull request
lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings.
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=80 --statistics

test:
	pytest --ignore=tests/sensor_test.py

install:
	rsync -t --verbose --recursive --human-readable \
		--delete --exclude *.json \
		--executability --exclude=".?*" . raspberrypi:LolaT/
