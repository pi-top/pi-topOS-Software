"""Command-line interface for working with pi-topOS software repositories."""
import os
import subprocess
import tempfile

import click
from pyfiglet import Figlet


class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


@click.command()
############################
# Group: command OR script #
############################
@click.option(
    "--command",
    type=str,
    help="The command to run on each matching repo.",
    default="ls -l",
    show_default=True,
)
# TODO: add function support
# mutually exclusive with command
# @click.option(
#     "--function",
#     type=str,
#     help="The function to run on each matching repo (sourced from lib.bash).",
# )
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
@click.option('--dry-run/--no-dry-run')
@click.option('--debug/--no-debug')
@click.option(
    "bash_conditions",
    "--condition",
    envvar="BASH_CONDITIONS",
    type=str,
    help="Bash condition to evaluate before running.",
    multiple=True,
)
@click.option(
    "file_conditions",
    "--condition-file",
    envvar="FILE_CONDITIONS",
    type=str,
    help="File regex condition that must match in order to continue.",
    multiple=True,
)
@click.option(
    "no_file_conditions",
    "--condition-no-file",
    envvar="NO_FILE_CONDITIONS",
    type=str,
    help="File regex condition that must not match in order to continue.",
    multiple=True,
)
def main(dry_run, debug, command, parallel, bash_conditions, file_conditions, no_file_conditions):
    """pi-topOS meta-exec."""
    click.echo(color.BOLD + color.GREEN + Figlet().renderText("pi-topOS meta-exec") + color.END)

    # Wrap command around if statements in new file
    handle, path = tempfile.mkstemp(text=True)
    with os.fdopen(handle, "w") as f:
        f.write("#!/bin/bash\n")

        if debug:
            f.write("set -ex\n")

        def add_exit_on_condition_failure(f, array, type_str, condition_prefix="!", condition_suffix=""):
            for elem in array:
                command = "exit"
                if debug:
                    f.write(f"echo Checking {type_str}: '{elem}'...\n")
                    command = f"echo '{type_str.capitalize()} not met: {elem}'; exit"
                f.write(
                    f"if {condition_prefix} {elem} {condition_suffix}; then {command}; fi\n"
                )

        add_exit_on_condition_failure(f, bash_conditions, "bash condition")
        add_exit_on_condition_failure(f, file_conditions, "file condition", condition_prefix="! compgen -G", condition_suffix=">/dev/null")
        add_exit_on_condition_failure(f, no_file_conditions, "no file condition", condition_prefix="compgen -G", condition_suffix=">/dev/null")

        f.write(command + "\n")

    if debug or dry_run:
        click.echo(f"{color.BOLD}{color.UNDERLINE}Script contents:{color.END}")
        with open(path, "r") as f:
            click.echo(f.read())

    if not dry_run:
        os.chmod(path, 0o755)

        args = ["meta", "exec", path]
        if parallel:
            args.append("--parallel")

        subprocess.run(args, cwd="..")

    os.remove(path)


if __name__ == "__main__":
    main(prog_name="pt-os-meta-exec")  # pragma: no cover
