test:
	pytest --ignore=tests/sensor_test.py

check:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=80 --statistics


install:
	rsync -t --verbose --recursive --human-readable \
		--delete --exclude *.json \
		--executability --exclude=".?*" . raspberrypi:LolaT/
