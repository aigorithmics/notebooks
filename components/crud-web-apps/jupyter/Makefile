IMG ?= registry.aigoml.aigodev.com/kubeflow/notebooks/jupyter-web-app
TAG ?= v1.10.0-1.2.13
DOCKERFILE ?= jupyter/Dockerfile
ARCH ?= linux/amd64


docker-build:
	cd ../ && docker build -t ${IMG}:${TAG} -f ${DOCKERFILE} .

docker-push:
	docker push $(IMG):$(TAG)

.PHONY: docker-build-multi-arch
docker-build-multi-arch: ##  Build multi-arch docker images with docker buildx
	cd ../ && docker buildx build --load --platform ${ARCH} --tag ${IMG}:${TAG} -f ${DOCKERFILE} .

.PHONY: docker-build-push-multi-arch
docker-build-push-multi-arch: ## Build multi-arch docker images with docker buildx and push to docker registry 
	cd ../ && docker buildx build --platform ${ARCH} --tag ${IMG}:${TAG} --push -f ${DOCKERFILE} .

image: docker-build docker-push

COMMON_LIB_COMMIT ?= $(shell head -n 1 frontend/COMMON_LIB_COMMIT)
COMMON_LIB_TARGET_DIR = kubeflow-common-lib
COMMON_LIB_TMP_TGZ := /tmp/kubeflow-$(COMMON_LIB_COMMIT).tar.gz

.PHONY:fetch-common-lib
fetch-common-lib:
	curl -L -f -o $(COMMON_LIB_TMP_TGZ) https://github.com/kubeflow/kubeflow/archive/$(COMMON_LIB_COMMIT).tar.gz

	rm -rf $(COMMON_LIB_TARGET_DIR)
	mkdir -p $(COMMON_LIB_TARGET_DIR)
	tar -C /tmp -xzf $(COMMON_LIB_TMP_TGZ) kubeflow-$(COMMON_LIB_COMMIT)/components/crud-web-apps/common/frontend/kubeflow-common-lib/
	mv /tmp/kubeflow-$(COMMON_LIB_COMMIT)/components/crud-web-apps/common/frontend/kubeflow-common-lib/* $(COMMON_LIB_TARGET_DIR)/

	rm -f $(COMMON_LIB_TMP_TGZ)
	rm -rf /tmp/kubeflow-$(COMMON_LIB_COMMIT)