"""Command-line interface."""
import click
import subprocess
import tempfile
from pyfiglet import Figlet
import os
import stat
import pathlib


@click.command()
###########################
# Group: action OR script #
###########################
@click.option('--action', type=str,
              help='The action to run on each child repo.',
              default="ls -l", show_default=True,
             )
# --script="update-deb-workflow-files"
#####################
# meta-exec options #
#####################
@click.option('--parallel/--no-parallel', type=bool,
              help='Run \'meta exec\' in parallel.',
              default=False, show_default=True,
             )
##################
# Script options #
##################
@click.option('conditions', '--condition', envvar='CONDITIONS', type=str,
             help='Bash condition to evaluate before running.',
             multiple=True,
             )
def main(action, parallel, conditions):
    """pi-topOS meta-exec."""
    click.echo(Figlet().renderText("pi-topOS meta-exec"))

    # Wrap action around if statements in new file
    handle, path = tempfile.mkstemp(text=True)
    with os.fdopen(handle, "w") as f:
        f.write("#!/bin/bash\n")
        for condition in conditions:
            f.write(f"if ! {condition}; then exit; fi\n")
        f.write(action + "\n")

    os.chmod(path, 0o777)

    args = ["meta", "exec", path]
    if parallel:
        args.append("--parallel")

    subprocess.run(args, cwd="..")
    f.close()

    os.remove(path)


if __name__ == "__main__":
    main(prog_name="pt-os-meta-exec")  # pragma: no cover
