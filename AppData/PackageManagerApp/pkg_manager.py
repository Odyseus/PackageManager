#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Module with utility functions and classes.

Attributes
----------
generic_summary : str
    Summary template displayed when installing/removing packages.
install_summary : str
    Summary template displayed when installing packages.
remove_summary : str
    Summary template displayed when removing packages.
root_folder : str
    The main folder containing the application. All commands must be executed from this location
    without exceptions.
"""
import os
import subprocess

from runpy import run_path

root_folder = os.path.realpath(os.path.abspath(os.path.join(
    os.path.normpath(os.getcwd()))))


generic_summary = """Summary:
{details}

More details can be found on the log file:
{log_path}
"""

install_summary = """
Of the {pkgs_list} packages that you are trying to install.

- {non_existent} packages are NOT available on the software sources.
- {installed} packages are already installed.
- {errors} errors were raised trying to gather the displayed information.

{pkgs_to_handle} packages were chosen to be installed.
"""

remove_summary = """
Of the {pkgs_list} packages that you are trying to remove.

- {not_installed} packages are NOT installed.
- {errors} errors were raised trying to gather the displayed information.

{pkgs_to_handle} packages were chosen to be removed.
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
    interface : TYPE
        Description
    logger : object
        See <class :any:`LogSystem`>.
    non_existent_pkgs : list
        Storage for packages that DOES NOT exist in the software sources.
    not_installed_pkgs : list
        Storage for packages that ARE NOT installed in the system.
    packages : list
        Description
    pkgs_to_handle : list
        List of packages that will be actually processed depending on "action".
    """

    def __init__(self, interface="", pkgs_list_relative=[], pkgs_list_absolute=[], logger=None):
        """
        Parameters
        ----------
        interface : str, optional
            Description
        pkgs_list_relative : list, optional
            Description
        pkgs_list_absolute : list, optional
            Description
        logger : object
            See <class :any:`LogSystem`>.
        """
        super(PackageManager, self).__init__()
        self.logger = logger

        self.packages = []
        self.interface = None
        self.errors = []
        self.non_existent_pkgs = []
        self.existent_pkgs = []
        self.not_installed_pkgs = []
        self.installed_pkgs = []

        self.interface = run_path(os.path.join(root_folder,
                                               "UserData",
                                               "interfaces",
                                               interface + ".py"))["commands"]

        # pkgs_list_relative deduplication. docopt workaround.
        for pkgs_list in list(set(pkgs_list_relative)):
            try:
                self.packages += list(run_path(os.path.join(root_folder,
                                                            "UserData",
                                                            "packages_lists",
                                                            pkgs_list + ".py"))["packages"])
            except Exception as err:
                self.logger.warning(err)
                continue

        # pkgs_list_absolute deduplication. docopt workaround.
        for pkgs_list in list(set(pkgs_list_absolute)):
            try:
                self.packages += list(run_path(os.path.abspath(pkgs_list))["packages"])
            except Exception as err:
                self.logger.warning(err)
                continue

        # Deduplicate packages.
        self.packages = list(set(self.packages))

    def install_packages(self):
        """Summary
        """
        self.check_packages("install")
        self.display_initial_report("install")

    def remove_packages(self):
        """Summary
        """
        self.check_packages("remove")
        self.display_initial_report("remove")

    def check_packages(self, action):
        """Summary

        Parameters
        ----------
        action : TYPE
            Description
        """
        if action == "install":
            # If non-existent, do not try to install.
            def b(p):
                """Filter package by its existence on the software repositories.

                Parameters
                ----------
                p : str
                    Package name.

                Returns
                -------
                bool
                    Package exists in repositories.
                """
                return self.check_package(p, "exists")

            pkgs_to_handle = list(filter(b, self.packages))

            # If installed, do not try to install.
            def a(p):
                """Filter packages by its installed status.

                Parameters
                ----------
                p : str
                    Package name.

                Returns
                -------
                bool
                    Package is not installed.
                """
                return not self.check_package(p, "installed")

            self.pkgs_to_handle = list(filter(a, pkgs_to_handle))

        elif action == "remove":
            # If not installed, do not try to uninstall.
            def c(p):
                """Filter packages by its installed status.

                Parameters
                ----------
                p : str
                    Package name.

                Returns
                -------
                bool
                    Package is installed.
                """
                return self.check_package(p, "installed")

            self.pkgs_to_handle = list(filter(c, self.packages))

    def check_package(self, pkg, check):
        """Summary

        Parameters
        ----------
        pkg : TYPE
            Description
        check : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        check_passed = True

        try:
            subprocess.check_call(self.interface[check]["cmd"].format(package=pkg),
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.STDOUT,
                                  shell=True)
        except subprocess.CalledProcessError:
            check_passed = False

        if check_passed:
            if check == "installed":
                self.installed_pkgs.append(pkg)
            elif check == "exists":
                self.existent_pkgs.append(pkg)
        else:
            if check == "installed":
                self.not_installed_pkgs.append(pkg)
            elif check == "exists":
                self.non_existent_pkgs.append(pkg)

        return check_passed

    def display_initial_report(self, action):
        """Display summary.

        Parameters
        ----------
        action : TYPE
            Description
        """
        summary = generic_summary.format(
            details=install_summary if action == "install" else remove_summary,
            log_path=self.logger.get_log_path())

        self.log_details("Packages processed:", self.packages)
        self.log_details("Packages non existent on software sources:", self.non_existent_pkgs)
        self.log_details("Packages available on software sources", self.existent_pkgs)
        self.log_details("Packages NOT installed:", self.not_installed_pkgs)
        self.log_details("Packages installed:", self.installed_pkgs)
        self.log_details("Errors raised while gathering package information:", self.errors)

        getattr(self.logger, "warning" if len(self.errors) > 0 else "info")(summary.format(
            pkgs_list=len(self.packages),
            non_existent=len(self.non_existent_pkgs),
            existent=len(self.existent_pkgs),
            not_installed=len(self.not_installed_pkgs),
            installed=len(self.installed_pkgs),
            errors=len(self.errors),
            pkgs_to_handle=len(self.pkgs_to_handle)
        ))

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
        self.logger.info(msg + "\n" + "\n".join(sorted(plist)), term=False)


if __name__ == "__main__":
    pass
