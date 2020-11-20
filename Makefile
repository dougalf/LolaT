install:
	rsync -t --verbose --recursive --human-readable \
		--delete --exclude *.json \
		--executability --exclude=".?*" . raspberrypi:LolaT/

# Seeing as I'm not using a virtual dev env just add PYTHONPATH=. so the
# tests can find the sources in directory lolat/
test:
	PYTHONPATH=. \
	pytest --ignore=tests/sensor_test.py
