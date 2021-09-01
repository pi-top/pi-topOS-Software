"""Command-line interface for working with pi-topOS software repositories."""
import atexit
import os
import pathlib
import subprocess
import tempfile
from cmd import Cmd
from dataclasses import dataclass

import click

from .terminal import color


masterWorkflowsPath = str(pathlib.Path(__file__).parent.absolute()) + "/workflow-files"


class InteractivePrompt(Cmd):
    prompt = "pt-os-meta-exec> "
    intro = "Type the command you would like to run against your currently filtered meta repos."

    def __init__(self, runner):
        super(InteractivePrompt, self).__init__()
        self.runner = runner

    def do_update_workflow_files(self, userInputStr):
        inputFields = userInputStr.split(" ")
        if len(inputFields) < 2:
            print("No branch specified...")
            return

        branch = inputFields[1]
        workflowDir = pathlib.Path(f"{str(masterWorkflowsPath)}/{branch}")

        if not workflowDir.is_dir():
            print(f"No workflow files for branch found: {workflowDir}")
            return

        # Get current branch
        commands = list()
        # Do not report touched files with contents identical to index as 'dirty'
        commands.append("git update-index --refresh || true")
        # Show if anything needed stashing before starting
        commands.append("git status")
        # Stash if necessary
        commands.append("if ! git diff-index --quiet HEAD --; then git stash; fi")
        # Move to correct branch if necessary
        commands.append(
            f"if [[ $(git rev-parse --abbrev-ref HEAD) != {branch} ]]; then git checkout {branch}; fi"
        )

        # Update files from master copies
        commands.append("rm -f .github/workflows/deb*.yml || true")
        commands.append(f"cp {workflowDir}/* .github/workflows/")

        # Commit
        commands.append("git add --all")
        commands.append(f"git commit -m 'Updated {branch} workflow files'")
        commands.append("git push")

        self.runner.run_commands(tuple(commands))

    def help_update_workflow_files(self):
        click.echo("update workflow files. Shorthand: u.")

    def do_exit(self, userInputStr):
        click.echo("Bye")
        return True

    def help_exit(self):
        click.echo("exit the application. Shorthand: x q Ctrl-D.")

    def default(self, userInputStr):
        if userInputStr == "x" or userInputStr == "q":
            return self.do_exit(userInputStr)

        inputFields = userInputStr.split(" ")
        if inputFields[0] == "u":
            return self.do_update_workflow_files(userInputStr)

        return self.runner.run_command(userInputStr)

    do_EOF = do_exit
    help_EOF = help_exit


@dataclass
class ScriptRunConditions:
    repo_str_match: tuple
    bash: tuple
    file: tuple
    no_file: tuple


@dataclass
class ScriptRunOpts:
    dry_run: bool
    strict: bool
    debug: bool
    parallel: bool
    conditions: ScriptRunConditions


class ExecutableScript(object):
    def create(self, commands, opts):
        handle, self.path = tempfile.mkstemp(text=True)
        atexit.register(self.cleanup)

        with os.fdopen(handle, "w") as f:

            f.write("#!/bin/bash\n")
            if opts.strict:
                f.write("set -euo pipefail\n")
            if opts.debug:
                f.write("set -x\n")
            f.write(f"source {pathlib.Path(__file__).parent.absolute()}/lib.bash\n")

            def add_exit_on_condition_failure(
                array, condition_prefix="!", condition_suffix=""
            ):
                for elem in array:
                    f.write(
                        f"if {condition_prefix}{elem}{condition_suffix}; then exit; fi\n"
                    )

            add_exit_on_condition_failure(
                opts.conditions.repo_str_match,
                condition_prefix="[[ $(pwd) != *\"",
                condition_suffix="\"* ]]",
            )
            add_exit_on_condition_failure(opts.conditions.bash)
            add_exit_on_condition_failure(
                opts.conditions.file,
                condition_prefix="! compgen -G ",
                condition_suffix=" >/dev/null",
            )
            add_exit_on_condition_failure(
                opts.conditions.no_file,
                condition_prefix="compgen -G ",
                condition_suffix=" >/dev/null",
            )

            for command in commands:
                f.write(command + "\n")

        os.chmod(self.path, 0o755)

    def cleanup(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class ScriptRunner:
    def __init__(self, opts):
        self.opts = opts
        self.script = ExecutableScript()

    def run_command(self, command):
        return self.run_commands((command,))

    def run_commands(self, commands):
        self.script.create(commands, self.opts)

        click.echo(f"{color.BOLD}{color.UNDERLINE}Script contents:{color.END}")
        with open(self.script.path, "r") as f:
            click.echo(f.read())

        if self.opts.dry_run:
            return

        args = ["meta", "exec", self.script.path]
        if self.opts.parallel:
            args.append("--parallel")

        subprocess.run(args, cwd="..")
