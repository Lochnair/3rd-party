#!groovy

@NonCPS
String sanitizeName(String s) {
    return s.replaceAll(/[^A-Za-z0-9_.-]+/, '_')
}

timestamps {
    ansiColor('xterm') {
        node('docker') {
            properties([
                disableConcurrentBuilds()
            ])

            def baseBuilderImageTag = "solus-3rdparty-builder-base:${env.BUILD_TAG}"
            def depsBuilderImageTag = "solus-3rdparty-builder-deps:${env.BUILD_TAG}"
            def packageDirs = []

            def skippedPackages = [
                'programming/unity-editor'
            ] as Set

            stage('Checkout') {
                checkout scm
            }

            stage('Build base builder image') {
                script {
                    def uid = sh(script: 'id -u', returnStdout: true).trim()
                    def gid = sh(script: 'id -g', returnStdout: true).trim()
                    def userName = sh(script: 'id -un', returnStdout: true).trim()

                    echo "Host Jenkins user: ${userName} (${uid}:${gid})"

                    docker.build(
                        baseBuilderImageTag,
                        "--build-arg JENKINS_UID=${uid} " +
                        "--build-arg JENKINS_GID=${gid} " +
                        "--build-arg JENKINS_USER=${userName} " +
                        "-f ci/solus-builder/Dockerfile ."
                    )
                }
            }

            stage('Discover packages') {
                script {
                    docker.image(baseBuilderImageTag).inside {
                        def raw = sh(
                            script: '''
                                set -euo pipefail

                                find . \
                                  -path '*/.git/*' -prune -o \
                                  -path '*/eopkg/*' -prune -o \
                                  -name pspec.xml -print \
                                | sed 's#^\\./##' \
                                | xargs -r -n1 dirname \
                                | sort -u
                            ''',
                            returnStdout: true
                        ).trim()

                        if (!raw) {
                            error('No package directories with pspec.xml were found.')
                        }

                        packageDirs = raw.split('\n') as List

                        echo "Discovered ${packageDirs.size()} package(s):"
                        packageDirs.each { pkg ->
                            echo " - ${pkg}"
                        }

                        def discoveredSkipped = packageDirs.findAll { it in skippedPackages }
                        def buildablePackages = packageDirs.findAll { !(it in skippedPackages) }

                        echo "Skipping ${discoveredSkipped.size()} package(s):"
                        discoveredSkipped.each { pkg ->
                            echo " - ${pkg}"
                        }

                        packageDirs = buildablePackages
                    }
                }
            }

            stage('Collect build deps') {
                script {
                    docker.image(baseBuilderImageTag).inside {
                        sh '''
                            set -euo pipefail

                            mkdir -p ci
                            : > ci/all-build-deps.txt

                            find . \
                              -path '*/.git/*' -prune -o \
                              -path '*/eopkg/*' -prune -o \
                              -name pspec.xml -print \
                            | while IFS= read -r pspec; do
                                python3 ci/list-build-deps.py "$pspec"
                              done \
                            | sort -u > ci/all-build-deps.txt

                            echo "Collected build deps:"
                            if [ -s ci/all-build-deps.txt ]; then
                                cat ci/all-build-deps.txt
                            else
                                echo "(none)"
                            fi
                        '''
                    }
                }
            }

            stage('Build deps builder image') {
                script {
                    writeFile file: 'ci/solus-builder/Dockerfile.deps', text: """
FROM ${baseBuilderImageTag}

COPY ci/all-build-deps.txt /tmp/all-build-deps.txt

RUN sudo eopkg update-repo && \\
    if [ -s /tmp/all-build-deps.txt ]; then \\
        echo "Installing pre-collected build deps:" && \\
        cat /tmp/all-build-deps.txt && \\
        sudo xargs -r eopkg -y it < /tmp/all-build-deps.txt; \\
    else \\
        echo "No build deps to install."; \\
    fi
"""

                    docker.build(
                        depsBuilderImageTag,
                        "-f ci/solus-builder/Dockerfile.deps ."
                    )
                }
            }

            stage('Stash source') {
                stash name: 'source-tree', includes: '**/*', useDefaultExcludes: false
            }

            stage('Build packages') {
                script {
                    def branches = [:]

                    for (int i = 0; i < packageDirs.size(); i++) {
                        def pkg = packageDirs[i]
                        def pkgSafe = sanitizeName(pkg)

                        branches[pkg] = {
                            node('docker') {
                                ws("${env.JOB_NAME}@${pkgSafe}") {
                                    deleteDir()
                                    unstash 'source-tree'

                                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                                        docker.image(depsBuilderImageTag).inside {
                                            stage("Build: ${pkg}") {
                                                dir(pkg) {
                                                    sh '''
                                                        set -euo pipefail

                                                        rm -f ./*.eopkg || true

                                                        sudo eopkg.py3 bi --ignore-safety pspec.xml
                                                    '''
                                                }
                                            }

                                            stage("Artifact summary: ${pkg}") {
                                                dir(pkg) {
                                                    sh '''
                                                        set +e
                                                        echo "Artifacts in $(pwd):"
                                                        find . -maxdepth 1 -type f -name '*.eopkg' -print | sort
                                                    '''
                                                }
                                            }
                                        }
                                    }

                                    stage("Archive: ${pkg}") {
                                        archiveArtifacts(
                                            artifacts: "${pkg}/*.eopkg",
                                            allowEmptyArchive: true,
                                            fingerprint: true,
                                            onlyIfSuccessful: false
                                        )
                                    }
                                }
                            }
                        }
                    }

                    parallel branches
                }
            }
        }
    }
}
