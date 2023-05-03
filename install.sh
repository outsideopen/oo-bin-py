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
                sudo apt-get -y update && sudo apt-get install -y ssh autossh python3-pip whois
            fi
        else
            echo "We could not automatically install the dependencies on your system. Please install ssh and autossh manually."
        fi
    elif [[ $(uname -s) =~ "Darwin" ]]; then
        if which brew 2>/dev/null; then
            if ! which autossh; then
                brew install autossh
            fi
            if ! which whois; then
                brew whois
            fi
            if [ "$(which python3)" != "/usr/local/bin/python3" ]; then
                brew install python
            fi
        else
            echo "Could not find Homebrew (https://brew.sh/). Install Homebrew, or, manually install autossh."
        fi
    fi

}

function install {
    if [ -v $1 ]; then
        VERSION=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases/latest | grep tag_name | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+')
    else
        VERSION=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases | jq -r 'map(select(.prerelease)) | first | .tag_name')
        if [ $VERSION == "null" ]; then
            echo "No Prerelease is available."
            exit 1
        fi
    fi
    curl -LJO https://github.com/outsideopen/oo-bin-py/releases/download/${VERSION}/oo_bin-${VERSION}-py3-none-any.whl

    pip3 install --force-reinstall ./"oo_bin-${VERSION}-py3-none-any.whl"
    rm oo_bin-${VERSION}-py3-none-any.whl
}

function add_tunnels_config_download {
    if ! grep -s -q "\[tunnels\.update\]" $HOME/.config/oo_bin/config.toml; then
        read -p "Enable remote tunnels config update? (Y/N): " CONFIRM
        case $CONFIRM in
            [yY]*) CONFIRM=true ;;
            *) return ;;
        esac

        read -p "url: [https://outsideopen.com/oo_bin] " URL
        URL=${URL:-https://outsideopen.com/oo_bin}
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

function bash_version_check {
    VERSION=$(bash --version | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    MAJOR_VERSION=$(echo $VERSION | sed -E 's/([0-9]+)\.[0-9]+\.[0-9]+/\1/')

    if [ "${MAJOR_VERSION}" -lt "4" ]; then
        echo "Command line completions requires Bash v4+"
        echo "The completions will not be installed, please consider updating bash, and running this script again."
        return 1
    fi
    return 0
}

function bash_add_local_bin_to_path {
    if cat $HOME/.bashrc | grep -q 'PATH=$PATH:$HOME/.local/bin'; then
        echo '`$HOME/.local/bin` is already added to your path. Nothing to be done'
    else
        echo 'Adding `PATH=$PATH:$HOME/.local/bin` to ~/.bashrc'
        export PATH=$PATH:$HOME/.local/bin
        echo 'PATH=$PATH:$HOME/.local/bin' >>$HOME/.bashrc
    fi
}

function bash_add_completions {
    _OO_COMPLETE=bash_source oo >$HOME/.config/oo_bin/oo-complete.bash

    if cat $HOME/.bashrc | grep -q 'source $HOME/.config/oo_bin/oo-complete.bash'; then
        echo '`~/.config/oo_bin/oo-complete.bash` is already sourced in your bashrc. Nothing to be done'
    else
        echo 'Adding `source ~/.config/oo_bin/oo-complete.bash` to ~/.bashrc'
        echo 'source $HOME/.config/oo_bin/oo-complete.bash' >>$HOME/.bashrc
    fi
}

function zsh_add_completions {
    _OO_COMPLETE=zsh_source oo >$HOME/.config/oo_bin/oo-complete.zsh

    if cat $HOME/.zshrc | grep -q 'source $HOME/.config/oo_bin/oo-complete.zsh'; then
        echo '`~/.config/oo_bin/oo-complete.zsh` is already sourced in your zshhrc. Nothing to be done'
    else
        echo 'Adding `source ~/.config/oo_bin/oo-complete.zsh` to ~/.zshrc'
        echo 'autoload -Uz compinit && compinit' >>$HOME/.zshrc
        echo 'source $HOME/.config/oo_bin/oo-complete.zsh' >>$HOME/.zshrc
    fi
}

function fish_add_completions {
    if test -f $HOME/.config/fish/completions/oo.fish; then
        echo '`~/.config/fish/completions/oo.fish` already exists. Nothing to be done'
    else
        _OO_COMPLETE=fish_source oo >$HOME/.config/fish/completions/oo.fish
        echo 'Created/Updated ~/.config/fish/completions/oo.fish'
    fi
}

for i in "$@"; do
    case $i in
        --prerelease)
            PRERELEASE=YES
            ;;
        *)
            # unknown option
            ;;
    esac
done

make_config
echo 'Install Dependencies'
echo '********************'
install_dependencies
echo ''
echo 'Add ~/.local/bin to the path'
echo '****************************'
bash_add_local_bin_to_path
echo ''
echo 'Install Bin Scripts'
echo '*******************'
install $PRERELEASE
echo ''
echo 'Config Auto Update'
echo '******************'
add_tunnels_config_download
# We need to update here, or the completions may fail
oo tunnels --update
echo ''
echo 'Configure Completions'
echo '*********************'
# We check the bash version, because Mac still has an old version of Bash by default
if bash_version_check; then
    bash_add_completions
fi

if which zsh &>/dev/null; then
    zsh_add_completions
fi

if which fish &>/dev/null; then
    fish_add_completions
fi

echo ''
echo "If your .baschrc/.zshrc was modified, you may need to restart your terminal for the changes to take effect."
