#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module with utility functions and classes.

Attributes
----------
root_folder : str
    The main folder containing the application. All commands must be executed from this location
    without exceptions.
"""
import os
import subprocess

from runpy import run_path

from .python_utils import cmd_utils
from .python_utils import exceptions
from .python_utils import file_utils
from .python_utils import json_schema_utils
from .python_utils import prompts
from .python_utils.ansi_colors import Ansi
from .python_utils.tqdm import tqdm
from .schemas import interface_schema
from .schemas import packages_schema

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))

_paths_map = {
    "packages_lists": os.path.join(root_folder, "UserData", "packages_lists"),
    "interfaces": os.path.join(root_folder, "UserData", "interfaces")
}

_summary = """**Summary:**
Of the {pkgs_list} packages that you are trying to remove.

{non_existent}{existent}{not_installed}{installed}
- {errors} errors were raised trying to gather the displayed information.

{pkgs_to_handle} packages were chosen to be removed.

More details can be found on the log file:
{log_file}
"""


class PackageManager():
    """Package manager class.

    Attributes
    ----------
    errors : list
        Errors storage.
    existent_pkgs : list
        Storage for packages that exist in the software sources.
    installed_pkgs : list
        Storage for packages that are installed in the system.
    interface : dict
        The commands definitions to manages packages.
    logger : LogSystem
        The logger.
    non_existent_pkgs : list
        Storage for packages that DOES NOT exist in the software sources.
    not_installed_pkgs : list
        Storage for packages that ARE NOT installed in the system.
    packages : list
        The list of packages that hasn't been checked yet.
    pkgs_to_handle : list
        List of packages that will be actually processed depending on an action
        (``install`` or ``remove``).
    """
    _actions = [
        "exists",
        "installed",
        "install",
        "remove",
    ]

    def __init__(self, interface="", pkgs_list_relative=[], pkgs_list_absolute=[],
                 ignore_exists_check=False, ignore_installed_check=False, logger=None):
        """
        Parameters
        ----------
        interface : dict
            The commands definitions to manages packages.
        pkgs_list_relative : list, optional
            List of names of file that can be found inside **UserData/packages_lists**.
        pkgs_list_absolute : list, optional
            List of absolute paths to files containing a packages list.
        logger : LogSystem
            The logger.
        """
        super().__init__()
        self._ignore_exists_check = ignore_exists_check
        self._ignore_installed_check = ignore_installed_check
        self.logger = logger

        self.packages = []
        self.interface = None
        self.errors = []
        self.non_existent_pkgs = []
        self.existent_pkgs = []
        self.not_installed_pkgs = []
        self.installed_pkgs = []

        interface_path = os.path.join(root_folder,
                                      "UserData",
                                      "interfaces",
                                      interface + ".py")
        self.interface = run_path(interface_path)["interface"]

        self._validate(self.interface, interface_schema, interface_path, "interface")

        for pkgs_list in pkgs_list_relative:
            try:
                pkgs_path = os.path.join(
                    root_folder,
                    "UserData",
                    "packages_lists",
                    pkgs_list + ".py")
                pkgs_list = run_path(pkgs_path)["packages"]
                self._validate(pkgs_list, packages_schema, pkgs_path, "packages")

                self.packages.extend(pkgs_list)
            except Exception as err:
                self.errors.append(str(err))
                continue

        for pkgs_list in pkgs_list_absolute:
            try:
                pkgs_path = os.path.abspath(file_utils.expand_path(pkgs_list))
                pkgs_list = run_path(pkgs_path)["packages"]
                self._validate(pkgs_list, packages_schema, pkgs_path, "packages")

                self.packages.extend(pkgs_list)
            except Exception as err:
                self.errors.append(str(err))
                continue

        # De-duplicate packages.
        self.packages = list(set(self.packages))

        for a in self._actions:
            self._set_command(a)

    def _validate(self, pkgs_list, schema, file_path, schema_key):
        if json_schema_utils.JSONSCHEMA_INSTALLED:
            json_schema_utils.validate(
                pkgs_list, schema,
                error_message_extra_info="\n".join([
                    "File: %s" % file_path,
                    "Data key: %s" % schema_key
                ]),
                logger=self.logger)

    def _set_command(self, action):
        """Set command for action.

        Parameters
        ----------
        action : str
            The action to perform.

        Returns
        -------
        None
            Halt execution.
        """
        cmd = cmd_utils.which(self.interface[action].get("cmd", ""))
        cmd_args = self.interface[action].get("cmd_args", [])

        if not cmd:
            return

        cmd_args.insert(0, cmd)

        elevator = cmd_utils.which(self.interface[action].get("elevator", ""))
        elevator_args = self.interface[action].get("elevator_args", [])

        if elevator:
            elevator_args.insert(0, elevator)
            setattr(self, action + "_cmd", elevator_args + cmd_args)
        else:
            setattr(self, action + "_cmd", cmd_args)

    def _perform_final_action(self, action):
        """Perform file action.

        Parameters
        ----------
        action : str
            The action to perform.
        """
        cmd = getattr(self, action + "_cmd") + self.pkgs_to_handle

        if action == "install":
            action_verb = "Installing..."
            action_noun = "installation"
        elif action == "remove":
            action_verb = "Removing..."
            action_noun = "removal"

        if len(self.pkgs_to_handle) > 0:
            self.logger.info("**Command that will be executed:**\n%s" % " ".join(cmd))

            if prompts.confirm(prompt=Ansi.MAGENTA("**Proceed with package %s?**") % action_noun,
                               response=False):
                self.logger.info(action_verb)
                cmd_utils.run_cmd(cmd,
                                  stdout=None,
                                  stderr=None)
            else:
                self.logger.info("**%s canceled**" % action_noun.capitalize())
        else:
            self.logger.info("**No packages to handle**")

    def _filter_packages(self, action):
        """Filter packages.

        Parameters
        ----------
        action : str
            The action to perform.
        """
        self.pkgs_to_handle = self.packages[:]

        if self._ignore_exists_check:
            self.logger.warning("Check for package existence ignored")
        else:
            # If non-existent, do not try to install.
            self.pkgs_to_handle = list(
                filter(lambda p: self._check_package(p, "exists"),
                       tqdm(self.pkgs_to_handle, desc="Filtering non existent packages...", unit="pkgs"))
            )

        if self._ignore_installed_check:
            self.logger.warning("Check for package installed state ignored")
        else:
            # If installed, do not try to install.
            self.pkgs_to_handle = list(
                filter(lambda p: (not self._check_package(p, "installed")),
                       tqdm(self.pkgs_to_handle, desc="Filtering installed packages...", unit="pkgs"))
            )

    def _check_package(self, pkg, action):
        """Check package existence/installed state.

        Parameters
        ----------
        pkg : str
            The name of a package.
        action : str
            The action to perform.

        Returns
        -------
        bool
            If the check passed.

        Raises
        ------
        exceptions.KeyboardInterruption
            Halt execution.
        """
        check_passed = True

        try:
            cmd_utils.run_cmd(getattr(self, action + "_cmd") + [pkg],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.STDOUT,
                              check=True)
        except subprocess.CalledProcessError as err:
            self.errors.append(str(err))
            check_passed = False
        except KeyboardInterrupt:
            raise exceptions.KeyboardInterruption()

        if action == "installed":
            self.installed_pkgs.append(pkg) if check_passed else self.not_installed_pkgs.append(pkg)
        elif action == "exists":
            self.existent_pkgs.append(pkg) if check_passed else self.non_existent_pkgs.append(pkg)

        return check_passed

    def _display_initial_report(self, action):
        """Display initial report.

        Parameters
        ----------
        action : str
            The action to perform.
        """
        self.log_details("Packages processed:", self.packages)

        if self._ignore_exists_check:
            non_existent = ""
            existent = ""
            self.log_details("Check for package existence ignored", [])
        else:
            non_existent = "- {} packages are NOT available on the software sources.\n".format(
                len(self.non_existent_pkgs))
            existent = "- {} packages are available on the software sources.\n".format(
                len(self.existent_pkgs))

            self.log_details("Packages non existent on software sources:", self.non_existent_pkgs)
            self.log_details("Packages available on software sources", self.existent_pkgs)

        if self._ignore_installed_check:
            not_installed = ""
            installed = ""
            self.log_details("Check for package installed state ignored", [])
        else:
            not_installed = "- {} packages are NOT installed.\n".format(
                len(self.not_installed_pkgs))
            installed = "- {} packages are already installed.\n".format(
                len(self.installed_pkgs))

            self.log_details("Packages NOT installed:", self.not_installed_pkgs)
            self.log_details("Packages installed:", self.installed_pkgs)

        self.log_details("Errors raised while gathering package information:", self.errors)

        getattr(self.logger, "warning" if len(self.errors) > 0 else "info")(_summary.format(
            pkgs_list=len(self.packages),
            non_existent=non_existent,
            existent=existent,
            not_installed=not_installed,
            installed=installed,
            errors=len(self.errors),
            pkgs_to_handle=len(self.pkgs_to_handle),
            log_file=self.logger.get_log_file()
        ))

    def manage_packages(self, action):
        """Manage packages.

        Parameters
        ----------
        action : str
            The action to perform.
        """
        if action:
            self._filter_packages(action)
            self._display_initial_report(action)
            self._perform_final_action(action)

    def log_details(self, msg, plist):
        """Log lists of packages.

        Log complete the lists of packages sorted, one per line, and do not display them in terminal.

        Parameters
        ----------
        msg : str
            Message
        plist : list
            Package list.
        """
        self.logger.info(msg + "\n" + ("\n".join(sorted(plist)) if plist else "None"), term=False)


def print_config_files_list(file_type):
    """Print config files list.

    Used to print to standard output the list of configuration files (either "packages_lists" or
    "interfaces" configuration files). The output is used only by the Bash completions script.

    Parameters
    ----------
    file_type : str
        One of "packages_lists" or "interfaces".
    """
    # FUTURE:
    # Use context manager with os.scandir().
    list_of_files = [entry.name for entry in os.scandir(_paths_map[file_type]) if
                     entry.is_file(follow_symlinks=False)]

    for f in list_of_files:
        name, ext = os.path.splitext(f)

        if ext == ".py":
            print(name)


if __name__ == "__main__":
    pass
