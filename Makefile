test:
	pytest --ignore=tests/sensor_test.py

install:
	rsync -t --verbose --recursive --human-readable \
		--delete --exclude *.json \
		--executability --exclude=".?*" . raspberrypi:LolaT/
