#!/usr/bin/env bash

set -e

function make_config {
    mkdir -p $HOME/.config/oo_bin
    touch $HOME/.config/oo_bin/tunnels.conf
}

function install {
    VERSION=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases/latest | grep tag_name | grep -Eo '[0-9]\.[0-9]\.[0-9]')
    curl -LJO https://github.com/outsideopen/oo-bin-py/releases/download/${VERSION}/oo_bin-${VERSION}-py3-none-any.whl

    pip3 install ./"oo_bin-${VERSION}-py3-none-any.whl"
    rm oo_bin-${VERSION}-py3-none-any.whl
}

function bash_add_local_bin_to_path {
    echo ''

    if cat $HOME/.bashrc | grep -q 'PATH=$PATH:$HOME/.local/bin'
    then
        echo '`$HOME/.local/bin` is already added to your path. Nothing to be done'
    else
        echo 'Adding `PATH=$PATH:$HOME/.local/bin` to ~/.bashrc' 
        export PATH=$PATH:$HOME/.local/bin
        echo 'PATH=$PATH:$HOME/.local/bin' >> $HOME/.bashrc
    fi
}

function bash_add_argscomplete {
    echo ''

    if cat $HOME/.bashrc | grep -q 'source $HOME/.bash_completion/python-argcomplete'
    then
        echo '`python-argcomplete` is already sourced in your bashrc. Nothing to be done'
    else
        # Activate command line completion
        mkdir -p $HOME/.bash_completion
        activate-global-python-argcomplete --dest $HOME/.bash_completion

        echo 'Sourcing `python-argcomplete` in ~/.bashrc' 
        # Temporarily add
        source $HOME/.bash_completion/python-argcomplete
        # Permanently add
        echo 'source $HOME/.bash_completion/python-argcomplete' >> $HOME/.bashrc
    fi
}

make_config
install
bash_add_local_bin_to_path
bash_add_argscomplete
