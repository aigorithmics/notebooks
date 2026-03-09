# Top-level Makefile for building and pushing all CRUD web apps and controllers
#
# Usage:
#   make docker-build-all                       # Build all images
#   make docker-push-all                        # Push all images
#   make docker-build-push-all                  # Build and push all images
#   make docker-build-all TAG=v1.10.0-2.2.0     # Override tag for all images
#   make docker-build-push-multi-arch-all       # Multi-arch build and push all
#   make docker-build-jupyter                   # Build a single component
#

TAG ?= v1.10.0-2.1.0
ARCH ?= linux/amd64

# Image registries (matching sub-project defaults)
JUPYTER_IMG        ?= registry.aigoml.aigodev.com/kubeflow/notebooks/jupyter-web-app
TENSORBOARDS_IMG   ?= registry.aigoml.aigodev.com/kubeflow/tensorboards-web-app
VOLUMES_IMG        ?= registry.aigoml.aigodev.com/kubeflow/notebooks/volumes-web-app
NOTEBOOK_CTRL_IMG  ?= registry.aigoml.aigodev.com/kubeflow/kubeflow/notebook-controller
PVCVIEWER_CTRL_IMG ?= registry.aigoml.aigodev.com/kubeflow/notebooks/pvcviewer-controller
TENSORBOARD_CTRL_IMG ?= registry.aigoml.aigodev.com/kubeflow/tensorboard-controller

# Sub-project directories
JUPYTER_DIR        = crud-web-apps/jupyter
TENSORBOARDS_DIR   = crud-web-apps/tensorboards
VOLUMES_DIR        = crud-web-apps/volumes
NOTEBOOK_CTRL_DIR  = notebook-controller
PVCVIEWER_CTRL_DIR = pvcviewer-controller
TENSORBOARD_CTRL_DIR = tensorboard-controller

ALL_COMPONENTS = jupyter tensorboards volumes notebook-controller pvcviewer-controller tensorboard-controller

##@ All targets

.PHONY: docker-build-all
docker-build-all: $(addprefix docker-build-,$(ALL_COMPONENTS)) ## Build all docker images

.PHONY: docker-push-all
docker-push-all: $(addprefix docker-push-,$(ALL_COMPONENTS)) ## Push all docker images

.PHONY: docker-build-push-all
docker-build-push-all: docker-build-all docker-push-all ## Build and push all docker images

.PHONY: docker-build-multi-arch-all
docker-build-multi-arch-all: $(addprefix docker-build-multi-arch-,$(ALL_COMPONENTS)) ## Build all multi-arch docker images

.PHONY: docker-build-push-multi-arch-all
docker-build-push-multi-arch-all: $(addprefix docker-build-push-multi-arch-,$(ALL_COMPONENTS)) ## Build and push all multi-arch docker images

##@ CRUD Web Apps

.PHONY: docker-build-jupyter
docker-build-jupyter: ## Build jupyter web app image
	$(MAKE) -C $(JUPYTER_DIR) docker-build IMG=$(JUPYTER_IMG) TAG=$(TAG)

.PHONY: docker-push-jupyter
docker-push-jupyter: ## Push jupyter web app image
	$(MAKE) -C $(JUPYTER_DIR) docker-push IMG=$(JUPYTER_IMG) TAG=$(TAG)

.PHONY: docker-build-multi-arch-jupyter
docker-build-multi-arch-jupyter: ## Build jupyter web app multi-arch image
	$(MAKE) -C $(JUPYTER_DIR) docker-build-multi-arch IMG=$(JUPYTER_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-push-multi-arch-jupyter
docker-build-push-multi-arch-jupyter: ## Build and push jupyter web app multi-arch image
	$(MAKE) -C $(JUPYTER_DIR) docker-build-push-multi-arch IMG=$(JUPYTER_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-tensorboards
docker-build-tensorboards: ## Build tensorboards web app image
	$(MAKE) -C $(TENSORBOARDS_DIR) docker-build IMG=$(TENSORBOARDS_IMG) TAG=$(TAG)

.PHONY: docker-push-tensorboards
docker-push-tensorboards: ## Push tensorboards web app image
	$(MAKE) -C $(TENSORBOARDS_DIR) docker-push IMG=$(TENSORBOARDS_IMG) TAG=$(TAG)

.PHONY: docker-build-multi-arch-tensorboards
docker-build-multi-arch-tensorboards: ## Build tensorboards web app multi-arch image
	$(MAKE) -C $(TENSORBOARDS_DIR) docker-build-multi-arch IMG=$(TENSORBOARDS_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-push-multi-arch-tensorboards
docker-build-push-multi-arch-tensorboards: ## Build and push tensorboards web app multi-arch image
	$(MAKE) -C $(TENSORBOARDS_DIR) docker-build-push-multi-arch IMG=$(TENSORBOARDS_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-volumes
docker-build-volumes: ## Build volumes web app image
	$(MAKE) -C $(VOLUMES_DIR) docker-build IMG=$(VOLUMES_IMG) TAG=$(TAG)

.PHONY: docker-push-volumes
docker-push-volumes: ## Push volumes web app image
	$(MAKE) -C $(VOLUMES_DIR) docker-push IMG=$(VOLUMES_IMG) TAG=$(TAG)

.PHONY: docker-build-multi-arch-volumes
docker-build-multi-arch-volumes: ## Build volumes web app multi-arch image
	$(MAKE) -C $(VOLUMES_DIR) docker-build-multi-arch IMG=$(VOLUMES_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-push-multi-arch-volumes
docker-build-push-multi-arch-volumes: ## Build and push volumes web app multi-arch image
	$(MAKE) -C $(VOLUMES_DIR) docker-build-push-multi-arch IMG=$(VOLUMES_IMG) TAG=$(TAG) ARCH=$(ARCH)

##@ Controllers

.PHONY: docker-build-notebook-controller
docker-build-notebook-controller: ## Build notebook controller image
	$(MAKE) -C $(NOTEBOOK_CTRL_DIR) docker-build IMG=$(NOTEBOOK_CTRL_IMG) TAG=$(TAG)

.PHONY: docker-push-notebook-controller
docker-push-notebook-controller: ## Push notebook controller image
	$(MAKE) -C $(NOTEBOOK_CTRL_DIR) docker-push IMG=$(NOTEBOOK_CTRL_IMG) TAG=$(TAG)

.PHONY: docker-build-multi-arch-notebook-controller
docker-build-multi-arch-notebook-controller: ## Build notebook controller multi-arch image
	$(MAKE) -C $(NOTEBOOK_CTRL_DIR) docker-build-multi-arch IMG=$(NOTEBOOK_CTRL_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-push-multi-arch-notebook-controller
docker-build-push-multi-arch-notebook-controller: ## Build and push notebook controller multi-arch image
	$(MAKE) -C $(NOTEBOOK_CTRL_DIR) docker-build-push-multi-arch IMG=$(NOTEBOOK_CTRL_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-pvcviewer-controller
docker-build-pvcviewer-controller: ## Build pvcviewer controller image
	$(MAKE) -C $(PVCVIEWER_CTRL_DIR) docker-build IMG=$(PVCVIEWER_CTRL_IMG) TAG=$(TAG)

.PHONY: docker-push-pvcviewer-controller
docker-push-pvcviewer-controller: ## Push pvcviewer controller image
	$(MAKE) -C $(PVCVIEWER_CTRL_DIR) docker-push IMG=$(PVCVIEWER_CTRL_IMG) TAG=$(TAG)

.PHONY: docker-build-multi-arch-pvcviewer-controller
docker-build-multi-arch-pvcviewer-controller: ## Build pvcviewer controller multi-arch image
	$(MAKE) -C $(PVCVIEWER_CTRL_DIR) docker-build-multi-arch IMG=$(PVCVIEWER_CTRL_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-push-multi-arch-pvcviewer-controller
docker-build-push-multi-arch-pvcviewer-controller: ## Build and push pvcviewer controller multi-arch image
	$(MAKE) -C $(PVCVIEWER_CTRL_DIR) docker-build-push-multi-arch IMG=$(PVCVIEWER_CTRL_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-tensorboard-controller
docker-build-tensorboard-controller: ## Build tensorboard controller image
	$(MAKE) -C $(TENSORBOARD_CTRL_DIR) docker-build IMG=$(TENSORBOARD_CTRL_IMG) TAG=$(TAG)

.PHONY: docker-push-tensorboard-controller
docker-push-tensorboard-controller: ## Push tensorboard controller image
	$(MAKE) -C $(TENSORBOARD_CTRL_DIR) docker-push IMG=$(TENSORBOARD_CTRL_IMG) TAG=$(TAG)

.PHONY: docker-build-multi-arch-tensorboard-controller
docker-build-multi-arch-tensorboard-controller: ## Build tensorboard controller multi-arch image
	$(MAKE) -C $(TENSORBOARD_CTRL_DIR) docker-build-multi-arch IMG=$(TENSORBOARD_CTRL_IMG) TAG=$(TAG) ARCH=$(ARCH)

.PHONY: docker-build-push-multi-arch-tensorboard-controller
docker-build-push-multi-arch-tensorboard-controller: ## Build and push tensorboard controller multi-arch image
	$(MAKE) -C $(TENSORBOARD_CTRL_DIR) docker-build-push-multi-arch IMG=$(TENSORBOARD_CTRL_IMG) TAG=$(TAG) ARCH=$(ARCH)

##@ Help

.PHONY: help
help: ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-45s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
