"""Command-line interface for working with pi-topOS software repositories."""
import click
from pyfiglet import Figlet

from .classes import InteractivePrompt, ScriptRunConditions, ScriptRunner, ScriptRunOpts
from .terminal import color

# TODO: set opts in interactive mode


@click.command()
###############################
# Command OR sourced function #
###############################
@click.argument(
    "command",
    type=str,
    nargs=-1,
    # help="The command to run on each matching repo. "
    # "Must be available on the system in a new shell after sourcing lib.bash",
)
#####################
# meta-exec options #
#####################
@click.option(
    "--parallel/--no-parallel",
    type=bool,
    help="Run 'meta exec' in parallel.",
    default=False,
    show_default=True,
)
##################
# Script options #
##################
@click.option(
    "--dry-run/--no-dry-run",
    help="Simulate command.",
)
@click.option(
    "--strict/--no-strict",
    help="Apply 'set -euo pipefail' to command(s)/script to run.",
    default=True,
)
@click.option(
    "--debug/--no-debug",
    help="Apply 'set -x' to command(s)/script to run.",
)
@click.option(
    "repo_str_match",
    "--repo-match",
    type=str,
    help="String matching pattern for repository ID (key in .meta) to run the given command(s).",
    multiple=True,
)
@click.option(
    "bash_conditions",
    "--condition",
    envvar="BASH_CONDITIONS",
    type=str,
    help="Bash string condition to return true before running the command on each repo (e.g. 'grep -q 'buster' debian/changelog').",
    multiple=True,
)
@click.option(
    "file_conditions",
    "--condition-file",
    envvar="FILE_CONDITIONS",
    type=str,
    help="Bash string condition (including wildcards) to match before running the command on each repo (e.g. 'debian/*').",
    multiple=True,
)
@click.option(
    "no_file_conditions",
    "--condition-no-file",
    envvar="NO_FILE_CONDITIONS",
    type=str,
    help="Bash string condition (including wildcards) to not match before running the command on each repo (e.g. 'debian/*').",
    multiple=True,
)
def main(
    dry_run,
    strict,
    debug,
    repo_str_match,
    command,
    parallel,
    bash_conditions,
    file_conditions,
    no_file_conditions,
):
    """pi-topOS meta-exec."""
    click.echo(
        color.BOLD + color.GREEN + Figlet().renderText("pi-topOS meta-exec") + color.END
    )

    conditions = ScriptRunConditions(
        repo_str_match, bash_conditions, file_conditions, no_file_conditions
    )

    opts = ScriptRunOpts(dry_run, strict, debug, parallel, conditions)

    runner = ScriptRunner(opts)

    if len(command) == 0:
        InteractivePrompt(runner).cmdloop()
    else:
        # 'command' is actually a tuple of commands
        runner.run_commands(command)


if __name__ == "__main__":
    main(prog_name="pt-os-meta-exec")  # pragma: no cover
