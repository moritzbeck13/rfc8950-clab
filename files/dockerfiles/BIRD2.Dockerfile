FROM alpine

RUN apk add --no-cache bird

ENTRYPOINT ["/usr/sbin/bird", "-d"]
