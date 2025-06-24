FROM alpine

RUN apk add --no-cache --repository=https://dl-cdn.alpinelinux.org/alpine/edge/testing bird3

ENTRYPOINT ["/usr/sbin/bird", "-d"]
