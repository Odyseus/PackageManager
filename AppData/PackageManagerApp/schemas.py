#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Schemas for JSON data validation.

Attributes
----------
interface_schema : dict
    JSON schema.
packages_schema : dict
    JSON schema.
"""
_interface_common_props = {
    "cmd": {
        "type": "string",
        "description": "Name or path to a command."
    },
    "cmd_args": {
        "type": "array",
        "description": "List of arguments to pass to the 'cmd' command.",
        "items": {
            "type": "string"
        }
    },
    "elevator": {
        "type": "string",
        "description": "Name or path to a command (normally sudo)."
    },
    "elevator_args": {
        "type": "array",
        "description": "List of arguments to pass to the 'elevator' command.",
        "items": {
            "type": "string"
        }
    }
}

interface_schema = {
    "description": "Schema to validate the 'interface' property inside a UserData/interfaces/<file_name>.py file.",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "exists",
        "installed",
        "install",
        "remove"
    ],
    "properties": {
        "exists": {
            "type": "object",
            "description": "Command definition for checking if a package exist.",
            "additionalProperties": False,
            "properties": _interface_common_props
        },
        "installed": {
            "type": "object",
            "description": "Command definition for checking if a package i installed.",
            "additionalProperties": False,
            "properties": _interface_common_props
        },
        "install": {
            "type": "object",
            "description": "Command definition for installing a list of packages.",
            "additionalProperties": False,
            "properties": _interface_common_props
        },
        "remove": {
            "type": "object",
            "description": "Command definition for removing a list of packages.",
            "additionalProperties": False,
            "properties": _interface_common_props
        }
    }
}

packages_schema = {
    "description": "Schema to validate the 'packages' property inside a UserData/packages_lists/<file_name>.py file.",
    "type": "array",
    "additionalItems": True,
    "items": {
        "type": "string"
    }
}


if __name__ == "__main__":
    pass
