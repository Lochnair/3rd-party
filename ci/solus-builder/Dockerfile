FROM silkeh/solus:ypkg

ARG JENKINS_UID=1000
ARG JENKINS_GID=1000
ARG JENKINS_USER=jenkins

RUN eopkg update-repo && \
    eopkg install -y shadow sudo python-eopkg && \
    groupadd -g "${JENKINS_GID}" "${JENKINS_USER}" && \
    useradd -m -u "${JENKINS_UID}" -g "${JENKINS_GID}" -s /bin/bash "${JENKINS_USER}" && \
    mkdir -p /etc/sudoers.d && \
    echo "${JENKINS_USER} ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/jenkins && \
    chmod 0440 /etc/sudoers.d/jenkins

WORKDIR /workspace
USER ${JENKINS_USER}