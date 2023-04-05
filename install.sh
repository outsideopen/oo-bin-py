#!/usr/bin/env bash

set -e

function make_config {
    mkdir -p "$HOME/.config/oo_bin"
}

function install_dependencies {
    # Case for WSL and Ubuntu linux
    if [[ $(uname -s) =~ "Linux" ]]; then
        if which apt-get 2>/dev/null; then
            if ! which autossh; then
                apt-get install -y ssh autossh
            fi
        else
            echo "We could not automatically install the dependencies on your system. Please install ssh and autossh manually."
        fi
    elif [[ $(uname -s) =~ "Darwin" ]]; then
        if which brew 2>/dev/null; then
            if ! which autossh; then
                brew install autossh
            fi
        else
            echo "Could not find Homebrew (https://brew.sh/). Install Homebrew, or, manually install autossh."
        fi
    fi

}

function install {
    VERSION=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases/latest | grep tag_name | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+')
    curl -LJO https://github.com/outsideopen/oo-bin-py/releases/download/${VERSION}/oo_bin-${VERSION}-py3-none-any.whl

    pip3 install ./"oo_bin-${VERSION}-py3-none-any.whl"
    rm oo_bin-${VERSION}-py3-none-any.whl
}

function bash_add_local_bin_to_path {
    echo ''

    if cat $HOME/.bashrc | grep -q 'PATH=$PATH:$HOME/.local/bin'; then
        echo '`$HOME/.local/bin` is already added to your path. Nothing to be done'
    else
        echo 'Adding `PATH=$PATH:$HOME/.local/bin` to ~/.bashrc'
        export PATH=$PATH:$HOME/.local/bin
        echo 'PATH=$PATH:$HOME/.local/bin' >>$HOME/.bashrc
    fi
}

function add_tunnels_config_download {
    if ! grep -s -q "\[tunnels\.update\]" $HOME/.config/oo_bin/config.toml; then
        read -p "Enable remote tunnels config update? (Y/N): " CONFIRM
        case $CONFIRM in
            [yY]*) CONFIRM=true ;;
            *) return ;;
        esac

        read -p "url: [https://outsideopen.com/oo_bin/tunnels.toml] " URL
        URL=${URL:-https://outsideopen.com/oo_bin/tunnels.toml}
        read -r -p "username: " USERNAME
        read -r -s -p "password: " PASSWORD
        echo ""
        read -p "Automatically check for updates, once a day? (Y/N): " AUTO
        case $AUTO in
            [yY]*) AUTO="true" ;;
            *) AUTO="false" ;;
        esac

        {
            echo '[tunnels.update]'
            echo "url = '${URL}'"
            echo "username = '${USERNAME}'"
            echo "password = '${PASSWORD}'"
            echo "auto_update = ${AUTO}"
        } >>"$HOME/.config/oo_bin/config.toml"
    fi
}

function bash_add_completions {
    echo ''

    if cat $HOME/.bashrc | grep -q 'source $HOME/.config/oo_bin/oo-complete.bash'; then
        echo '`.config/oo_bin/oo-complete.bash` is already sourced in your bashrc. Nothing to be done'
    else
        # Activate command line completion
        _OO_COMPLETE=bash_source oo > ~/.config/oo_bin/oo-complete.bash

        echo 'Sourcing `~/.config/oo_bin/oo-complete.bash` in ~/.bashrc'
        # Temporarily add
        source $HOME/.config/oo_bin/oo-complete.bash
        # Permanently add
        echo 'source $HOME/.config/oo_bin/oo-complete.bash' >>$HOME/.bashrc
    fi
}

function convert_tunnels_conf {
    OLD_CONFIG=$HOME/.config/oo_bin/tunnels.conf
    NEW_CONFIG=$HOME/.config/oo_bin/tunnels.toml

    if [ -f "$OLD_CONFIG" ]; then
        while IFS=',' read -r NAME JUMP_HOST URLS || [ -n "$line" ]; do
            if [ "$NAME" == "Location" ]; then continue; fi
            echo "[${NAME}]" >>$NEW_CONFIG
            echo "jump_host = '${JUMP_HOST}'" >>$NEW_CONFIG

            echo "${JUMP_HOST}"
            FIRST=true
            URL_STRING="["
            for URL in ${URLS//$'\r'/}; do
                if [ "$FIRST" = true ]; then
                    URL_STRING="$URL_STRING'${URL}'"
                    FIRST=false
                else
                    URL_STRING="$URL_STRING, '${URL}'"
                fi
            done
            URL_STRING="$URL_STRING]"

            echo "urls = ${URL_STRING}" >>$NEW_CONFIG
            echo "" >>$NEW_CONFIG
        done <$OLD_CONFIG

        echo "converted $OLD_CONFIG to $NEW_CONFIG"
        mv $OLD_CONFIG $OLD_CONFIG.bak
        echo "renamed $OLD_CONFIG to $OLD_CONFIG.bak"
    fi
}

make_config
install_dependencies
install
add_tunnels_config_download
bash_add_local_bin_to_path
bash_add_completions
convert_tunnels_conf
