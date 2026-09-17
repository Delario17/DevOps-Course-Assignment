FROM ubuntu:22.04

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . .
RUN make clean && make -j2

CMD ["./bin/demo", "--version"]
