#!/bin/bash

set -ex


show_help() {
    echo """
    Showing help
    """
}


# Run
case "$1" in
    start)
        flask start
    ;;
    *)
        show_help
    ;;
esac
