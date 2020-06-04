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
    for job in jobs:
        # XXX look at kind deps and add the matching attr
        # tasks as deps
        yield job


# XXX nuke me, just here to get a workable json
@transforms.add
def hack(config, jobs):
    for job in jobs:
        job.pop("push-docker-image")
        job.pop("deploy-secret-url")
        job.pop("docker-repo")
        yield job
