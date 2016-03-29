DOCKER:=docker
IMAGE:=twspam/twitter-ff
CONTAINER:=twspam-twitter-ff
VNC_IP:=127.0.0.1
VNC_PORT:=5900
KEYS_VOLUME:=$(CURDIR)/../../shares/twitter_linux_ff

.PHONY: default
default:
	$(MAKE) build
	$(MAKE) create

.PHONY: build
build:
	$(DOCKER) build --tag=$(IMAGE) .

.PHONY: create run
create run:
	$(DOCKER) $@ \
		-p $(VNC_IP):$(VNC_PORT):5900 \
		-v $(KEYS_VOLUME):/root/volume \
		-e SSLKEYLOGFILE=/root/volume/sslkeylog.txt \
		--name=$(CONTAINER) $(IMAGE)

.PHONY: start stop rm
start stop rm:
	$(DOCKER) $@ $(CONTAINER)
