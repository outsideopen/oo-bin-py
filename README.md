# Outside Open Bin scripts
Outside Open Bin scripts that work across Linux, Mac and Windows Subsystem for Linux 

# Dependencies

## Build time dependencies

- Python `>= 3.7`
- Pip

## Runtime dependencies

- ssh
- Autossh

# Configuration

(TODO!!!! Have tunnels.conf available for secure download by OO employees)
You need an SSH configuration, and matching `tunnels.conf`

## Firefox

Create a new profile called "Tunnels"
- Open Firefox with the Tunnels profile:
  - Enter about:config -> accept -> find browser.ssl_override_behavior and change its value from 2 to 1.
  - Preferences -> General -> Network Settings -> Manual proxy configuration

      SOCKS HOST: localhost

      Port: 2080

      SOCKS v5: check




# Installation

## TL;DR

(TODO!!!!)
Run `install.sh` 

## Manual installation

```bash
mkdir $HOME/.config/oo_bin

# Manually copy your tunnels.conf file into $HOME/.config/oo_bin

# Download the latest release (`oo_bin-x.x.x-py3-none-any.whl`) 
# from https://github.com/outsideopen/oo-bin-py/releases/
# Once the repo is made public, we can replace this step with a curl command
pip3 install ./oo_bin-x.x.x-py3-none-any.whl

# You may get a warning that $HOME/.local/bin is not in the path, fix it by adding to the path
# Temporarily add
export PATH=$PATH:$HOME/.local/bin
# Permanently add
echo 'PATH=$PATH:$HOME/.local/bin' >> $HOME/.bashrc

# Activate command line completion
mkdir $HOME/.bash_completion
activate-global-python-argcomplete --dest $HOME/.bash_completion
echo 'source $HOME/.bash_completion/python-argcomplete' >> $HOME/.bashrc
```


