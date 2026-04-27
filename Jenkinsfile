#!groovy

import groovy.json.JsonOutput
import groovy.json.JsonSlurperClassic

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

            def builderImage = null
            def packageDirs = []

            stage('Checkout') {
                checkout scm
            }

            stage('Build builder image') {
                script {
                    def uid = sh(script: 'id -u', returnStdout: true).trim()
                    def gid = sh(script: 'id -g', returnStdout: true).trim()
                    def userName = sh(script: 'id -un', returnStdout: true).trim()

                    echo "Host Jenkins user: ${userName} (${uid}:${gid})"

                    builderImage = docker.build(
                        "solus-3rdparty-builder:${env.BUILD_TAG}",
                        "--build-arg JENKINS_UID=${uid} " +
                        "--build-arg JENKINS_GID=${gid} " +
                        "--build-arg JENKINS_USER=${userName} " +
                        "-f Dockerfile ."
                    )
                }
            }

            stage('Discover packages') {
                script {
                    builderImage.inside {
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
                    }
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
                                        builderImage.inside {
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