#/usr/bin/env bash

_completions()
{
    COMP_WORDS+=("--run")

    COMPREPLY=($(compgen -W "$(ls settings | sed -e 's/.json//g')" -- "${COMP_WORDS[2]}"))
}

complete -F _completions pytornado
