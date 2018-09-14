#!/bin/bash

# It would have been impossible to create this without the following post on Stack Exchange!!!
# https://unix.stackexchange.com/a/55622

_have {executable_name} &&
_decide_nospace(){
    if [[ ${1} == "--"*"=" ]] ; then
        compopt -o nospace
    fi
} &&
__package_manager_app_{current_date}(){
    local cur prev cmd pkgs_lists_dir pkgs_lists interfaces_dir interfaces
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    pkgs_lists_dir="{full_path_to_app_folder}/UserData/packages_lists"
    # List the files in a specific directory.
    pkgs_lists=("${pkgs_lists_dir}/"*.py)
    # Get the file names only.
    pkgs_lists=(${pkgs_lists[@]##*/})
    # Remove the extension names.
    pkgs_lists=(${pkgs_lists[@]%.*})

    interfaces_dir="{full_path_to_app_folder}/UserData/interfaces"
    # List the files in a specific directory.
    interfaces=("${interfaces_dir}/"*.py)
    # Get the file names only.
    interfaces=(${interfaces[@]##*/})
    # Remove the extension names.
    interfaces=(${interfaces[@]%.*})

    case $prev in
        --list-relative)
            COMPREPLY=( $( compgen -W "${pkgs_lists[*]}") )
            return 0
            ;;
        -l)
            COMPREPLY=( $( compgen -W "${pkgs_lists[*]}" -- ${cur}) )
            return 0
            ;;
        --interface)
            COMPREPLY=( $( compgen -W "${interfaces[*]}") )
            return 0
            ;;
        -i)
            COMPREPLY=( $( compgen -W "${interfaces[*]}" -- ${cur}) )
            return 0
            ;;
    esac

    # Handle --xxxxxx=
    if [[ ${prev} == "--"* && ${cur} == "=" ]] ; then
        compopt -o filenames
        COMPREPLY=(*)
        return 0
    fi

    # Handle --xxxxx=path
    if [[ ${prev} == "=" ]] ; then
        # Unescape space
        cur=${cur//\\ / }
        # Expand tilder to $HOME
        [[ ${cur} == "~/"* ]] && cur=${cur/\~/$HOME}
        # Show completion if path exist (and escape spaces)
        compopt -o filenames
        local files=("${cur}"*)
        [[ -e ${files[0]} ]] && COMPREPLY=( "${files[@]// /\ }" )
        return 0
    fi

    # Completion of commands and "first level options.
    if [[ $COMP_CWORD == 1 ]]; then
        COMPREPLY=( $(compgen -W "install remove generate -h --help --version" -- "${cur}") )
        return 0
    fi

    # Completion of options and sub-commands.
    cmd="${COMP_WORDS[1]}"

    case $cmd in
    "install"|"remove")
        COMPREPLY=( $(compgen -W "-r --report -l --list-relative= -L --list-absolute= \
-i --interface=" -- "${cur}") )
        _decide_nospace ${COMPREPLY[0]}
        ;;
    "generate")
        COMPREPLY=( $(compgen -W "system_executable" -- "${cur}") )
        ;;
    esac
} &&
complete -F __package_manager_app_{current_date} {executable_name}
