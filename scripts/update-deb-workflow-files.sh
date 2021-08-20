#!/bin/bash -e

####################################
# Note: DOES THIS NEED TO BE BASH? #
####################################

# Other thoughts -
# We can make a CLI for managing our repo
# i.e. use args for things like "--debian"
# "pt-repo-mgr --filter=debian,pybuild,recovery --action=<path_to_script>"

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
META_REPO_ROOT_PATH="$(dirname "${SCRIPTS_DIR}")"
MASTER_WORKFLOWS_PATH="${META_REPO_ROOT_PATH}/workflow-files"

# Build up library of functions
# and source them for easy functionality

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

is_deb_pkg() {
    [[ -d "debian" ]] || return 1
    return 0
}

print_current_git_branch() {
    git rev-parse --abbrev-ref HEAD
}

if is_deb_pkg; then
    print_current_git_branch
    git status
    git stash

    # git checkout master

    # rm -f .github/workflows/deb*.yml || true
    # cp ${MASTER_WORKFLOWS_PATH}/master/* .github/workflows/

    # gqc "Update master workflow files"

    git checkout bullseye

    rm -f .github/workflows/deb*.yml || true
    cp ${MASTER_WORKFLOWS_PATH}/bullseye/* .github/workflows/

    gqc "Update bullseye workflow files"
fi
