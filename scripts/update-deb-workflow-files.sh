#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

root="$(dirname "${DIR}")"

gqc() {
    pre-commit install --allow-missing-config
    echo "Fetching from remote..."
    git fetch
    branch_name=$(git symbolic-ref -q HEAD)
    branch_name=${branch_name##refs/heads/}
    if [[ -z ${branch_name} ]]; then
        echo "No branch name found"
        return 1
    fi
    echo "Branch: ${branch_name}"
    if [[ -z $(git branch -a | ag "remotes/origin/${branch_name}") ]]; then
        echo "No remote branch found - skipping pull"
    else
        echo "Setting upstream on remote"
        git branch --set-upstream-to=origin/${branch_name} ${branch_name}
        git pull
        if [[ $? -ne 0 ]]; then
            echo "Failed to pull - exiting..."
            return 1
        fi
    fi
    if [[ -z "${1}" ]]; then
        git add --all && git commit -v && git push
    else
        git add --all && git commit -m "${1}" && git push
    fi
}

for D in "${root}"/packages/*; do
    if [[ -d "${D}/debian" ]]; then
        (
            echo "$D"

            rm -f ${D}/.github/workflows/deb*.yml || true
            cp ./workflow-files/deb/* ${D}/.github/workflows/

            cd "${D}"
            gqc "Update Debian build workflow files"
        ) &
    fi
done
