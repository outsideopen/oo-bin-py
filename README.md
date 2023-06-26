# Outside Open Bin scripts
Outside Open Bin scripts that work across Linux, Mac and Windows Subsystem for Linux 

# Dependencies

## Build time dependencies

- Python `>= 3.7`
- Pip

## Runtime dependencies

- ssh
- Autossh

## RDP

We support the following Remote desktop clients

- [mstsc](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/mstsc) (Windows)
- [Microsoft Remote Desktop](https://apps.apple.com/app/microsoft-remote-desktop/id1295203466?mt=12) (Mac)<sup>*</sup>
- [Rdesktop](http://www.rdesktop.org/) (Linux)

## Vnc

- [RealVNC](https://www.realvnc.com/en/connect/download/viewer/windows/) (Windows)<sup>*</sup>
- Built in VNC Viewer (Mac)

<sup>*</sup> Opens the app, but does not launch the correct profile

# Configuration

## SSH

You need an SSH configuration, and matching `tunnels.toml`
Remember to back up your private SSH keys ;)

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

  - Enter Y to enable config updates
  ```Enable remote tunnels config update? (Y/N): y```
   - Enter username and password for the config URL
   ```username: github```
    ```password: [enter password of the online config file location]```
  - Enter Y to enable automated daily updates
  ```Automatically check for updates, once a day? (Y/N): y```
  - This can be done manually at any time by running:
    ```oo tunnels --update```

## Install a Pre-release version

Sometimes we want to test a release before we make it publicly available. You can install the latest pre-release version by running

```bash
curl -O https://raw.githubusercontent.com/outsideopen/oo-bin-py/HEAD/install.sh; bash install.sh --prerelease; rm install.sh
```
