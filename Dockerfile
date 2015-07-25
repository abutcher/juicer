FROM fedora

MAINTAINER Andrew Buthcer <abutcher@redhat.com>

COPY rpm-build/noarch/juicer* /root/
RUN dnf install -y https://repos.fedorapeople.org/repos/pulp/pulp/stable/2/fedora-21/x86_64/python-pulp-common-2.6.2-1.fc21.noarch.rpm \
    https://repos.fedorapeople.org/repos/pulp/pulp/stable/2/fedora-21/x86_64/python-pulp-bindings-2.6.2-1.fc21.noarch.rpm \
    https://repos.fedorapeople.org/repos/pulp/pulp/stable/2/fedora-21/x86_64/python-pulp-docker-common-1.0.1-1.fc21.noarch.rpm \
    http://afrolegs.com/python-pyrpm-0.5.3-1.fc21.noarch.rpm \
    man-db \
    /root/juicer* && \
    dnf clean all
