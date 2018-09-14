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

from .__init__ import __appname__, __appdescription__, __version__, __status__
from .python_utils import exceptions, log_system, shell_utils, file_utils
from .python_utils.docopt import docopt

if sys.version_info < (3, 5):
    raise exceptions.WrongPythonVersion()

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))

# Store the "docopt" document in a variable to SHUT THE HELL UP Sphinx.
docopt_doc = """{__appname__} {__version__} {__status__}

{__appdescription__}

Usage:
    app.py (install | remove) (-i <file> | --interface=<file>)
           (-l <file>... | --list-relative=<file>...
           | -L <path>... | --list-absolute=<path>...)
           [-l <file>... | --list-relative=<file>...
           | -L <path>... | --list-absolute=<path>...]
           [--ignore-exists-filter]
           [--ignore-installed-filter]
           [-r | --report]
    app.py generate system_executable
    app.py (-h | --help | --version)

Options:

-h, --help
    Show this screen.

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

""".format(__appname__=__appname__,
           __appdescription__=__appdescription__,
           __version__=__version__,
           __status__=__status__)


class CommandLineTool():
    """Command line tool.

    It handles the arguments parsed by the docopt module.

    Attributes
    ----------
    action : method
        Set the method that will be executed when calling CommandLineTool.run().
    logger : object
        See <class :any:`LogSystem`>.
    package_manager : TYPE
        Description

    Deleted Attributes
    ------------------
    interface : TYPE
        Description
    pkgs_list : list
        The list of packages to remove/install.
    """

    def __init__(self, args):
        """
        Parameters
        ----------
        args : dict
            The dictionary of arguments as returned by docopt parser.
        """
        super(CommandLineTool, self).__init__()
        self.action = None
        self.package_manager = None
        logs_storage_dir = "UserData/logs"
        log_file = log_system.get_log_file(storage_dir=logs_storage_dir,
                                           prefix="CLI")
        file_utils.remove_surplus_files(logs_storage_dir, "CLI*")
        self.logger = log_system.LogSystem(filename=log_file,
                                           verbose=True)

        self.logger.info(shell_utils.get_cli_header(__appname__), date=False)
        print("")

        if args["generate"]:
            if args["system_executable"]:
                self.logger.info("System executable generation...")
                self.action = self.system_executable_generation

        if any([args["install"], args["remove"]]):
            from . import pkg_manager

            self.package_manager = pkg_manager.PackageManager(
                interface=args["--interface"],
                pkgs_list_relative=args["--list-relative"],
                pkgs_list_absolute=args["--list-absolute"],
                logger=self.logger
            )

            if args["install"]:
                self.action = self.install_packages
            elif args["remove"]:
                self.action = self.remove_packages

    def run(self):
        """
        """
        if self.action is not None:
            self.action()
            sys.exit(0)

    def install_packages(self):
        """Summary
        """
        self.package_manager.install_packages()

    def remove_packages(self):
        """Summary
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
        """See :any:`template_utils.system_executable_generation`
        """
        from .python_utils import template_utils

        template_utils.system_executable_generation(
            exec_name="package-manager-cli",
            app_root_folder=root_folder,
            sys_exec_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "system_executable"),
            bash_completions_template_path=os.path.join(
                root_folder, "AppData", "data", "templates", "bash_completions.bash"),
            logger=self.logger
        )


def main():
    """Initialize main command line interface.

    Raises
    ------
    exceptions.BadExecutionLocation
        Do not allow to run any command if the "flag" file isn't
        found where it should be. See :any:`exceptions.BadExecutionLocation`.
    """
    if not os.path.exists(".package-manager.flag"):
        raise exceptions.BadExecutionLocation()

    arguments = docopt(docopt_doc, version="%s %s %s" % (__appname__, __version__, __status__))
    # print(arguments)
    cli = CommandLineTool(arguments)
    cli.run()


if __name__ == "__main__":
    pass
