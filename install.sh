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
				sudo apt-get -y update && sudo apt-get install -y autossh
			fi
			if ! which pip3; then
				sudo apt-get -y update && sudo apt-get install -y python3-pip
			fi
			if ! which whois; then
				sudo apt-get -y update && sudo apt-get install -y whois
			fi
			if ! which jq; then
				sudo apt-get -y update && sudo apt-get install -y jq
			fi
		else
			echo "We could not automatically install the dependencies on your system. Please install ssh and autossh manually."
		fi
	elif [[ $(uname -s) =~ "Darwin" ]]; then
		if which brew 2>/dev/null; then
			if ! which autossh; then
				brew install autossh
			fi
			if [ "$(which python3)" != "/usr/local/bin/python3" ]; then
				brew install python
			fi
			if ! which whois; then
				brew install whois
			fi
			if ! which jq; then
				brew install jq
			fi
		else
			echo "Could not find Homebrew (https://brew.sh/). Install Homebrew, or, manually install autossh."
		fi
	fi

}

function install {
	if ls ~/.local/share/oo_bin/*.pkl >/dev/null 2>&1; then
		echo ""
		echo "The application cannot be updated while tunnels are running. Please stop all tunnels and try again:"
		echo ""
		echo "oo tunnels stop"
		echo "oo --update"
		exit 1
	fi

	if [ $PRERELEASE ]; then
		FILENAME=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases | jq -r 'map(select(.prerelease)) | .[0].assets[0].name')
		DOWNLOAD_URL=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases | jq -r 'map(select(.prerelease)) | .[0].assets[0].browser_download_url')
	else
		FILENAME=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases/latest | jq -r '.assets[0].name')
		DOWNLOAD_URL=$(curl -L https://api.github.com/repos/outsideopen/oo-bin-py/releases/latest | jq -r '.assets[0].browser_download_url')
	fi

	curl -LJO $DOWNLOAD_URL
	pip3 install --force-reinstall ./"$FILENAME"
	rm "$FILENAME"
}

function add_tunnels_config_download {
	if ! grep -s -q "\[tunnels\.update\]" $HOME/.config/oo_bin/config.toml; then
		read -p "Enable remote tunnels config update? (Y/N): " CONFIRM
		case $CONFIRM in
		[yY]*) CONFIRM=true ;;
		*) return ;;
		esac

		AUTH_FAIL=1

		while [ $AUTH_FAIL != 0 ]; do

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

			set +e
			(curl --fail -u "${USERNAME}:${PASSWORD}" https://outsideopen.com/api/oo_bin/ >/dev/null 2>&1)
			AUTH_FAIL=$?
			set -e

			if [ $AUTH_FAIL != 0 ]; then
				echo ""
				echo "We could not contact the update server. Please check your network connection, and make sure you have the correct credentials, before trying again."
			fi

		done

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

function add_ssh_config {
	if cat $HOME/.ssh/config | grep -q 'include ~/.config/oo_bin/ssh_config'; then
		echo '~/.config/oo_bin/ssh_config is already included in ~/.ssh/config. Nothing to be done'
	else
		echo 'Adding `include ~/.config/oo_bin/ssh_config` to ~/.ssh/config'
		echo 'include ~/.config/oo_bin/ssh_config' >>$HOME/.ssh/config
	fi

}

for i in "$@"; do
	case $i in
	--prerelease)
		PRERELEASE=true
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
install
echo ''
echo 'Config Auto Update'
echo '******************'
add_tunnels_config_download
# We need to update here, or the completions may fail
oo --update
echo ''
echo 'Configure Ssh'
echo '*************'
add_ssh_config
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
