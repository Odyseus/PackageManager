#!/bin/bash

# It would have been impossible to create this without the following post on Stack Exchange!!!
# https://unix.stackexchange.com/a/55622

type "{executable_name}" &> /dev/null &&
_decide_nospace_{current_date}(){
    if [[ ${1} == "--"*"=" ]] ; then
        type "compopt" &> /dev/null && compopt -o nospace
    fi
} &&
_get_packages_lists_{current_date}(){
    echo $(cd {full_path_to_app_folder}; ./app.py print_packages_lists)
} &&
_get_interfaces_{current_date}(){
    echo $(cd {full_path_to_app_folder}; ./app.py print_interfaces)
} &&
__package_manager_cli_{current_date}(){
    local cur prev cmd packages_lists interfaces
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    prev_to_prev="${COMP_WORDS[COMP_CWORD-2]}"

    case $prev in
        "--list-relative"|"-l")
            packages_lists=( $(_get_packages_lists_{current_date}) )

            if [[ $prev == "--list-relative" ]]; then
                COMPREPLY=( $( compgen -W "${packages_lists[*]}") )
            else
                COMPREPLY=( $( compgen -W "${packages_lists[*]}" -- ${cur}) )
            fi

            return 0
            ;;
        "--interface"|"-i")
            interfaces=( $(_get_interfaces_{current_date}) )

            if [[ $prev == "--interface" ]]; then
                COMPREPLY=( $( compgen -W "${interfaces[*]}") )
            else
                COMPREPLY=( $( compgen -W "${interfaces[*]}" -- ${cur}) )
            fi

            return 0
            ;;
    esac

    # Handle --xxxxx=value
    if [[ ${prev} == "=" ]] ; then
        case $prev_to_prev in
            "--list-relative")
                packages_lists=( $(_get_packages_lists_{current_date}) )
                COMPREPLY=( $( compgen -W "${packages_lists[*]}" -- ${cur}) )
                return 0
                ;;
            "--interface")
                interfaces=( $(_get_interfaces_{current_date}) )
                COMPREPLY=( $( compgen -W "${interfaces[*]}" -- ${cur}) )
                return 0
                ;;
        esac

        return 0
    fi

    # Completion of commands and "first level options.
    if [[ $COMP_CWORD == 1 ]]; then
        COMPREPLY=( $(compgen -W "install remove generate -h --help --manual --version" -- "${cur}") )
        return 0
    fi

    # Completion of options and sub-commands.
    cmd="${COMP_WORDS[1]}"

    case $cmd in
    "install"|"remove")
        COMPREPLY=( $(compgen -W "-r --report -l --list-relative= -L --list-absolute= \
-i --interface= --ignore-exists-check --ignore-installed-check" -- "${cur}") )
        _decide_nospace_{current_date} ${COMPREPLY[0]}
        ;;
    "generate")
        COMPREPLY=( $(compgen -W "system_executable" -- "${cur}") )
        ;;
    esac
} &&
complete -F __package_manager_cli_{current_date} {executable_name}
