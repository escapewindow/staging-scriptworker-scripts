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
        env = job["worker"].setdefault("env", {})
        # XXX
        yield job


# XXX nuke me, just here to get a workable json
@transforms.add
def hack(config, jobs):
    for job in jobs:
        job.pop("push-docker-image")
        job.pop("deploy-secret-url")
        job.pop("docker-repo")
        yield job
