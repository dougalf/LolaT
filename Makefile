all:
	rsync -t --verbose --recursive --delete --human-readable \
		--executability --exclude=".?*" . raspberrypi:LolaT/
