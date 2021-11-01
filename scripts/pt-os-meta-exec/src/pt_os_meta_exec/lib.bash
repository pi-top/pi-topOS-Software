# Quick test
hello_world() {
    echo "Hello World"
}

# Quick commit-all
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
    git add --all && git commit -m "${1}" && git push
}

# Print Github repository page
repo_url() {
    repo_name=$(basename `git rev-parse --show-toplevel`)
    echo "https://github.com/pi-top/${repo_name}"
}

# Open github page for repository
open_browser() {
    open "$(repo_url)"
}
