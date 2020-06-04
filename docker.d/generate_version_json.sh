#/bin/sh
set -e

test $HEAD_REV
test $TASK_ID
test $TASKCLUSTER_ROOT_URL
test $REPO_URL
test $PROJECT_NAME

cat > version.json <<EOF
{
    "commit": "${GIT_HEAD_REV}",
    "version": "$(cat ${PROJECT_NAME}/version.txt)",
    "source": "${REPO_URL}",
    "build": "${TASKCLUSTER_ROOT_URL}/tasks/${TASK_ID}"
}
EOF

cat version.json
