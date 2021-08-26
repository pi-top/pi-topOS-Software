"""Command-line interface for working with pi-topOS software repositories."""
import atexit
import os
import pathlib
import subprocess
import tempfile
from cmd import Cmd
from dataclasses import dataclass

import click
from pyfiglet import Figlet


class InteractivePrompt(Cmd):
    prompt = "pt-os-meta-exec> "
    intro = "Type the command you would like to run against your currently filtered meta repos."

    def __init__(self, runner):
        super(InteractivePrompt, self).__init__()
        self.runner = runner

    def do_exec(self, inp):
        self.runner.run_commands((inp,))

    def help_exec(self):
        click.echo("execute a command.")

    def do_exit(self, inp):
        click.echo("Bye")
        return True

    def help_exit(self):
        click.echo("exit the application. Shorthand: x q Ctrl-D.")

    def default(self, inp):
        if inp == "x" or inp == "q":
            return self.do_exit(inp)
        return self.do_exec(inp)

    do_EOF = do_exit
    help_EOF = help_exit


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


@dataclass
class ScriptRunConditions:
    bash: tuple
    file: tuple
    no_file: tuple


@dataclass
class ScriptRunOpts:
    dry_run: bool
    debug: bool
    parallel: bool
    conditions: ScriptRunConditions


class ExecutableScript(object):
    def create(self, commands, opts, debug=False):
        handle, self.path = tempfile.mkstemp(text=True)
        atexit.register(self.cleanup)

        with os.fdopen(handle, "w") as f:

            f.write("#!/bin/bash -e\n")
            if debug:
                f.write("set -x\n")
            f.write(f"source {pathlib.Path(__file__).parent.absolute()}/lib.bash\n")

            def add_exit_on_condition_failure(
                array, type_str, condition_prefix="!", condition_suffix=""
            ):
                for elem in array:
                    f.write(
                        f"if {condition_prefix} {elem} {condition_suffix}; then exit; fi\n"
                    )

            add_exit_on_condition_failure(opts.conditions.bash, "bash condition")
            add_exit_on_condition_failure(
                opts.conditions.file,
                "file condition",
                condition_prefix="! compgen -G",
                condition_suffix=">/dev/null",
            )
            add_exit_on_condition_failure(
                opts.conditions.no_file,
                "no file condition",
                condition_prefix="compgen -G",
                condition_suffix=">/dev/null",
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

    def run_commands(self, commands):
        self.script.create(commands, self.opts)

        if self.opts.debug or self.opts.dry_run:
            click.echo(f"{color.BOLD}{color.UNDERLINE}Script contents:{color.END}")
            with open(self.script.path, "r") as f:
                click.echo(f.read())

        if self.opts.dry_run:
            return

        args = ["meta", "exec", self.script.path]
        if self.opts.parallel:
            args.append("--parallel")

        subprocess.run(args, cwd="..")


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
@click.option("--dry-run/--no-dry-run")
@click.option("--debug/--no-debug")
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
def main(
    dry_run,
    debug,
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
        bash_conditions, file_conditions, no_file_conditions
    )

    opts = ScriptRunOpts(dry_run, debug, parallel, conditions)

    runner = ScriptRunner(opts)

    if len(command) == 0:
        InteractivePrompt(runner).cmdloop()
    else:
        runner.run_commands(command)


if __name__ == "__main__":
    main(prog_name="pt-os-meta-exec")  # pragma: no cover
