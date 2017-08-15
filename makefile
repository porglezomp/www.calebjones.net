all: publish

upload: publish
	aws s3 sync output/posts/ "s3://www.calebjones.net/posts/" --acl public-read --delete
	aws s3 sync output/theme/ "s3://www.calebjones.net/theme/" --acl public-read --delete
	aws s3 sync output/about/ "s3://www.calebjones.net/about/" --acl public-read --delete
	aws s3 sync output/feeds/ "s3://www.calebjones.net/feeds/" --acl public-read --delete
	aws s3 sync output/page/ "s3://www.calebjones.net/page/" --acl public-read --delete
	aws s3 cp output/archives.html "s3://www.calebjones.net/" --acl public-read
	aws s3 cp output/tags.html "s3://www.calebjones.net/" --acl public-read
	aws s3 cp output/index.html "s3://www.calebjones.net/" --acl public-read

publish:
	pelican -s publishconf.py
	mkdir -p output/page/
	@echo 'Do `make upload` to upload'

clean:
	rm -rf output
