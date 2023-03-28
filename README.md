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

## SSH

You need an SSH configuration, and matching `tunnels.conf`

## Firefox

Set up Tunnels profile in Firefox:
    - Open Firefox and enter `about:profiles` in the URL bar
    - Create a new profile called "Tunnels"
    - Close/re-open Firefox with the Tunnels profile
        - Preferences -> General -> Network Settings -> Manual proxy configuration
            -  SOCKS HOST: localhost
            -  Port: 2080
            -  SOCKS v5: check


# Installation

Run the following command to install the script as your current user. It can also be used to update to the latest version. 

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/outsideopen/oo-bin-py/HEAD/install.sh)"
```
