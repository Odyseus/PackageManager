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
    app.py (install | remove) (-i <file> | --interface=<file>)
           (-l <file>... | --list-relative=<file>...
           | -L <path>... | --list-absolute=<path>...)
           [-l <file>... | --list-relative=<file>...
           | -L <path>... | --list-absolute=<path>...]
           [--ignore-exists-filter]
           [--ignore-installed-filter]
           [-r | --report]
    app.py generate system_executable

Options:

-h, --help
    Show this screen.

--manual
    Show this application manual page.

--version
    Show application version.

-i <file>, --interface=<file>
    File name (no extension) of an existent file in
    UserData/interfaces/<file>.py that contains the commads that will actually
    be used to handle packages.

-l <file>, --list-relative=<file>
    File name (no extension) of an existent file in
    UserData/packages_lists/<file>.py that contains a list of packages and that
    will be used with the install/remove commands.

-L <path>, --list-absolute=<path>
    Full path to a file containing the list of packages that will be used
    with the install/remove commands.

--ignore-exists-filter
    Ignore the check for package existence.

--ignore-installed-filter
    Ignore the check for package installed.

-r, --report
    Just show an initial report, do not start the install/remove process.

Sub-commands for the `generate` command:
    system_executable    Create an executable for this application on the system
                         PATH to be able to run it from anywhere.

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
        See :any:`pkg_manager.PackageManager`.
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
        self._cli_header_blacklist = [self.a["--manual"]]

        super().__init__(__appname__, "UserData/logs")

        if self.a["--manual"]:
            self.action = self.display_manual_page
        elif self.a["generate"]:
            if self.a["system_executable"]:
                self.logger.info("System executable generation...")
                self.action = self.system_executable_generation
        elif any([self.a["install"], self.a["remove"]]):
            from . import pkg_manager

            self.package_manager = pkg_manager.PackageManager(
                interface=self.a["--interface"],
                pkgs_list_relative=self.a["--list-relative"],
                pkgs_list_absolute=self.a["--list-absolute"],
                logger=self.logger
            )

            if self.a["install"]:
                self.action = self.install_packages
            elif self.a["remove"]:
                self.action = self.remove_packages

    def run(self):
        """Execute the assigned action stored in self.action if any.
        """
        if self.action is not None:
            self.action()
            sys.exit(0)

    def install_packages(self):
        """See :any:`pkg_manager.PackageManager.install_packages`.
        """
        self.package_manager.install_packages()

    def remove_packages(self):
        """See :any:`pkg_manager.PackageManager.remove_packages`.
        """
        self.package_manager.remove_packages()

    # def manage_pkgs(self):
    #     """Perform package removal/installation.

    #     Raises
    #     ------
    #     SystemExit
    #         Description

    #     Deleted Parameters
    #     ------------------
    #     action : str
    #         "install" or "remove".

    #     No Longer Raises
    #     ----------------
    #     common_utils.CustomRuntimeError
    #         Raise if list of packages doesn't exists.
    #     """
    #     # Deduplicate packages list.
    #     self.pkgs_list = list(set(self.pkgs_list))

    #     if not self.pkgs_list:
    #         self.logger.warning("Package list non existent!")
    #         raise SystemExit()

    #     print(self.pkgs_list)

    #     from . import pkg_manager

    #     pkg_mngr = pkg_manager.PackageManager(**self.data,
    #                                           logger=self.logger)
    #     # pkg_mngr = pkg_manager.PackageManager(self.pkgs_list,
    #     #                                       self.interface,
    #     #                                       action,
    #     #                                       logger=self.logger)
    #     # pkg_mngr.display_initial_report()

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
