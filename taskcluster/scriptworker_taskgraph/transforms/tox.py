# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""

from __future__ import absolute_import, print_function, unicode_literals
from copy import deepcopy

from taskgraph.transforms.base import TransformSequence


transforms = TransformSequence()


def _replace_string(obj, repl_dict):
    if isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = obj[k].format(**repl_dict)
    elif isinstance(obj, list):
        for c in range(0, len(obj)):
            obj[c] = obj[c].format(**repl_dict)
    else:
        obj = obj.format(**repl_dict)
    return obj


@transforms.add
def tasks_per_python_version(config, jobs):
    for job in jobs:
        for python_version in job.pop("python-versions"):
            task = deepcopy(job)
            repl_dict = {"name": job["name"], "python_version": python_version}
            task["label"] = "tox-{name}-python{python_version}".format(**repl_dict)
            task['worker']['docker-image'] = _replace_string(task['worker']['docker-image'], repl_dict)
            task['description'] = _replace_string(task['description'], repl_dict)
            task['run']['command'] = _replace_string(task['run']['command'], repl_dict)
            # XXX default files-changed? e.g. taskcluster/ .tc.yml docker
            yield task
