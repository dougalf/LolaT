all:
	rsync -t --verbose --recursive --human-readable \
		--delete --exclude *.json \
		--executability --exclude=".?*" . raspberrypi:LolaT/
