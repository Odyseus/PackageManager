#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Main command line application.

Attributes
----------
docopt_doc : str
    Used to store/define the docstring that will be passed to docopt as the "doc" argument.
root_folder : str
    The main folder containing the application. All commands must be executed from this location
    without exceptions.
"""

import os
import sys

from . import app_utils
from .__init__ import __appdescription__
from .__init__ import __appname__
from .__init__ import __status__
from .__init__ import __version__
from .python_utils import cli_utils

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))

docopt_doc = """{appname} {version} ({status})

{appdescription}

Usage:
    app.py (-h | --help | --manual | --version)
    app.py (install | remove)
           (-i <file> | --interface=<file>)
           (-l <file>... | --list-relative=<file>...
           | -L <path>... | --list-absolute=<path>...)
           [-l <file>... | --list-relative=<file>...
           | -L <path>... | --list-absolute=<path>...]
           [--ignore-exists-check]
           [--ignore-installed-check]
    app.py generate system_executable
    app.py (print_packages_lists | print_interfaces)

Options:

-h, --help
    Show this screen.

--manual
    Show this application manual page.

--version
    Show application version.

-i <file>, --interface=<file>
    File name (no extension) of an existent file in
    **UserData/interfaces/<file>.py** that contains the commands that will
    actually be used to handle packages.

-l <file>, --list-relative=<file>
    File name (no extension) of an existent file in
    **UserData/packages_lists/<file>.py** that contains a list of packages and
    that will be used with the **install**/**remove** commands.

-L <path>, --list-absolute=<path>
    Full path to a file containing the list of packages that will be used
    with the **install**/**remove** commands.

--ignore-exists-check
    Ignore the check for package existence.

--ignore-installed-check
    Ignore the check for package installed.

""".format(appname=__appname__,
           appdescription=__appdescription__,
           version=__version__,
           status=__status__)


class CommandLineInterface(cli_utils.CommandLineInterfaceSuper):
    """Command line interface.

    It handles the arguments parsed by the docopt module.

    Attributes
    ----------
    a : dict
        Where docopt_args is stored.
    action : method
        Set the method that will be executed when calling CommandLineTool.run().
    package_manager : class
        See :any:`app_utils.PackageManager`.
    """
    action = None
    package_manager = None

    def __init__(self, docopt_args):
        """
        Parameters
        ----------
        docopt_args : dict
            The dictionary of arguments as returned by docopt parser.
        """
        self.a = docopt_args
        self._cli_header_blacklist = [
            self.a["--manual"],
            self.a["print_packages_lists"],
            self.a["print_interfaces"]
        ]
        self._inhibit_logger_list = self._cli_header_blacklist

        super().__init__(__appname__)

        if self.a["--manual"]:
            self.action = self.display_manual_page
        elif self.a["print_packages_lists"]:
            self.action = self.print_packages_lists
        elif self.a["print_interfaces"]:
            self.action = self.print_interfaces
        elif self.a["generate"]:
            if self.a["system_executable"]:
                self.logger.info("**System executable generation...**")
                self.action = self.system_executable_generation
        elif any([self.a["install"], self.a["remove"]]):
            self.package_manager = app_utils.PackageManager(
                interface=self.a["--interface"],
                # De-duplication. docopt workaround.
                pkgs_list_relative=list(set(self.a["--list-relative"])),
                # De-duplication. docopt workaround.
                pkgs_list_absolute=list(set(self.a["--list-absolute"])),
                ignore_exists_check=self.a["--ignore-exists-check"],
                ignore_installed_check=self.a["--ignore-installed-check"],
                logger=self.logger
            )

            self.action = self.manage_packages

    def run(self):
        """Execute the assigned action stored in self.action if any.
        """
        if self.action is not None:
            self.action()
            self.print_log_file()
            sys.exit(0)

    def print_packages_lists(self):
        """See :any:`app_utils.print_config_files_list`.
        """
        app_utils.print_config_files_list("packages_lists")

    def print_interfaces(self):
        """See :any:`app_utils.print_config_files_list`.
        """
        app_utils.print_config_files_list("interfaces")

    def manage_packages(self):
        """See :any:`app_utils.PackageManager.manage_packages`.
        """
        self.package_manager.manage_packages(
            "install" if self.a["install"] else "remove" if self.a["remove"] else None
        )

    def system_executable_generation(self):
        """See :any:`cli_utils.CommandLineInterfaceSuper._system_executable_generation`.
        """
        self._system_executable_generation(
            exec_name="package-manager-cli",
            app_root_folder=root_folder,
            sys_exec_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "system_executable"),
            bash_completions_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "bash_completions.bash"),
            logger=self.logger
        )

    def display_manual_page(self):
        """See :any:`cli_utils.CommandLineInterfaceSuper._display_manual_page`.
        """
        self._display_manual_page(os.path.join(root_folder, "AppData", "data", "man", "app.py.1"))


def main():
    """Initialize command line interface.
    """
    cli_utils.run_cli(flag_file=".package-manager.flag",
                      docopt_doc=docopt_doc,
                      app_name=__appname__,
                      app_version=__version__,
                      app_status=__status__,
                      cli_class=CommandLineInterface)


if __name__ == "__main__":
    pass
