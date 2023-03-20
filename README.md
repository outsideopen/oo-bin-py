# Outside Open Bin scripts
Outside Open Bin scripts

# Dependencies

## Build time dependencies

- Python `>= 3.7`
- Pip

## Runtime dependencies

- ssh
- Autossh

# Configuration

(TODO!!!!)
You need an SSH configuration, and matching `tunnels.conf`

# Installation

## TL;DR

(TODO!!!!)
Run `install.sh` 

## Manual installation

```bash
mkdir $HOME/.config/oo_bin

# Manually copy your tunnels.conf file into $HOME/.config/oo_bin

# Download the latest release (`oo_bin-x.x.x-py3-none-any.whl`) from https://github.com/outsideopen/oo-bin-py/releases/tag
# Once the repo is made public, we can replace this step with a curl command
pip3 install oo_bin-x.x.x-py3-none-any.whl

# If you get a warning that $HOME/.local/bin is not in the path, fix it by adding it to the path
export PATH=$PATH:$HOME/.local/bin
echo PATH=$PATH:$HOME/.local/bin > $HOME/.bashrc

# Activate command line completion
sudo activate-global-python-argcomplete
```


