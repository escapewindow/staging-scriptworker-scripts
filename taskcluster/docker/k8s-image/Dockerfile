# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# We need to run a really old docker version because taskcluster is using a
# really old version in their setup
FROM          docker:1.6.2

RUN apk add --update python3

RUN mkdir /builds && \
    mkdir /builds/worker/artifacts

# %include-run-task

ENV SHELL=/bin/sh \
    HOME=/builds/worker \
    PATH=/builds/worker/.local/bin:$PATH

VOLUME /builds/worker/checkouts
VOLUME /builds/worker/.cache

# Set a default command useful for debugging
CMD ["/bin/sh"]
