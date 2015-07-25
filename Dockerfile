FROM fedora

MAINTAINER Andrew Butcher <abutcher@redhat.com>

RUN dnf install -y 'dnf-command(copr)' && dnf copr enable -y abutcher/juicer
RUN dnf install -y juicer man-db && dnf clean all

COPY config /root/.config/juicer/config
