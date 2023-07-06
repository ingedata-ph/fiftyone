
.PHONY: app python docker docker-export

.DEFAULT_GOAL := docker-export

app:
	@cd app && yarn && yarn build && cd ..

python: app
	@python setup.py sdist bdist_wheel

docker-production: python
	@docker build -t voxel51/fiftyone-production . -f ./Dockerfile.production

docker-staging: python
	@docker build -t voxel51/fiftyone-staging . -f ./Dockerfile.staging

docker-export: docker
	@docker save voxel51/fiftyone:latest | gzip > fiftyone.tar.gz
