# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Kubernetes docker image builds.
"""

from __future__ import absolute_import, print_function, unicode_literals
from copy import deepcopy

from taskgraph.transforms.base import TransformSequence


transforms = TransformSequence()


@transforms.add
def add_dependencies(config, jobs):
    """Add dependencies that match python-version and script-name.

    Also copy the digest-directories attribute, and fail if there are
    unexpected discrepancies in upstream deps.

    """
    for job in jobs:
        attributes = job["attributes"]
        dependencies = job.setdefault("dependencies", {})
        digest_directories = None
        for dep_task in config.kind_dependencies_tasks:
            dep_attrs = dep_task.attributes
            dep_kind = dep_task.kind
            if dep_attrs["python-version"]  == attributes["python-version"] and \
                    dep_attrs["script-name"] == attributes["script-name"]:
                if dependencies.get(dep_kind):
                    raise Exception("Duplicate kind {kind} dependencies: {existing_label}, {new_label}".format(
                        kind=dep_kind,
                        existing_label=dependencies[dep_kind]["label"],
                        new_label=dep_task.label,
                    ))
                dependencies[dep_kind] = dep_task.label
                if dep_attrs.get("digest-directories"):
                    if digest_directories and digest_directories != dep_attrs["digest-directories"]:
                        raise Exception("Conflicting digest_directories: {existing_digest} {new_digest}".format(
                            existing_digest=digest_directories,
                            new_digest=dep_attrs["digest-directories"],
                        ))
                    digest_directories = dep_attrs["digest-directories"]
        if digest_directories:
            attributes["digest-directories"] = digest_directories
        yield job


@transforms.add
def set_environment(config, jobs):
    """Set the environment variables for the docker hub task."""
    for job in jobs:
        project_name = job["attributes"]["script-name"]
        docker_repo = job.pop("docker-repo")
        secret_url = job.pop("deploy-secret-url")
        tasks_for = config.params['tasks_for']
        scopes = job.setdefault("scopes", [])
        env = job["worker"].setdefault("env", {})
        env["GIT_HEAD_REV"] = config.params['head_rev']
        env["REPO_URL"] = config.params['head_repository']
        env["PROJECT_NAME"] = project_name
        env["TASKCLUSTER_ROOT_URL"] = "$TASKCLUSTER_ROOT_URL"
        env["DOCKER_TAG"] = "unknown"
        if tasks_for == 'github-pull-request':
            env["DOCKER_TAG"] = "pull-request"
        elif tasks_for == 'github-push':
            for ref_name in ("dev", "production"):
                if config.params['head_ref'] == "refs/heads/{}-{}".format(ref_name, project_name):
                    docker_tag = ref_name
                    break
            else:
                if config.params['head_ref'].startswith('refs/heads/'):
                    docker_tag = config.params['head_ref'].replace('refs/heads/', '')
        if job.pop("push-docker-image"):
            env["PUSH_DOCKER_IMAGE"] = "1"
            env["DOCKER_REPO"] = docker_repo
            env["SECRET_URL"] = secret_url
            # XXX move to config
            scopes.append('secrets:get:project/releng/scriptworker-scripts/deploy')
        else:
            env["PUSH_DOCKER_IMAGE"] = "0"
        yield job
