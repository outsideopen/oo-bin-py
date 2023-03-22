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
(**TODO:** Make tunnels.conf available for secure download by OO employees)

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

Run the following command to install the script as your current user. It can also be used to update to the latest version. 

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/outsideopen/oo-bin-py/HEAD/install.sh)"
```