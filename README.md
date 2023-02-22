# vscvm

A VSCode version manager.

## Install

Install `vsc` via pip:

```console
pip install vscvm
```

Add the following to your `.bashrc` file:

```bash
export PATH=$HOME/.vscvm:$PATH
if [ ! -e "/tmp/vscvm_check_update" ]; then
  vscvm_check_update
fi
```

and that's it!

### Disabling update checks

If you don't want an update check to run periodically, you only need to add this one line to your `.bashrc`:

```bash
export PATH=$HOME/.vscvm:$PATH
```

## Usage

```console
$ vsc list
v1.59 - July 2021
v1.58 - June 2021
v1.57 - May 2021
v1.56 - April 2021
v1.55 - March 2021

$ vsc install latest
Downloading v1.59 - July 2021...
Successfully installed v1.59!

$ code --version
1.59.0
```

## Commands

- `list`:

  ```console
  $ vsc list -n 3
  v1.59 - July 2021      [Active]
  v1.58 - June 2021      [Installed]
  v1.57 - May 2021
  ```

  ```console
  $ vsc list --installed
  v1.59 - July 2021      [Active]
  v1.58 - June 2021      [Installed]
  ```

  ```console
  $ vsc list --active
  v1.59 - July 2021      [Active]
  ```

- `install`:

  ```console
  $ vsc install latest
  Downloading v1.59 - July 2021...
  ```

  ```console
  $ vsc install v1.57
  Downloading v1.57 - May 2021...
  ```

  ```console
  $ vsc install 1.42
  Downloading v1.42 - January 2020...
  ```

- `uninstall`:

  ```console
  $ vsc list --active
  v1.59 - July 2021      [Active]
  $ vsc uninstall
  Uninstalled v1.59.
  ```

  ```console
  $ vsc uninstall 1.56
  Uninstalled v1.56.
  ```

- `cleanup`:

  ```console
  $ vsc list -n3
  v1.59 - July 2021      [Active]
  v1.58 - June 2021      [Installed]
  v1.57 - May 2021       [Installed]

  $ vsc cleanup
  Uninstalled v1.58.
  Uninstalled v1.57.
  ```

## Troubleshooting

- `vsc: command not found`

  If you installed `vscvm` via pip, but the terminal says vsc is not a recognized command,
  that means that you probably don't have `~/.local/bin` in your `PATH`.

  Add the following line into your `.bashrc` file:

  ```bash
  PATH=$PATH:$HOME/.local/bin
  ```

  then restart your terminal, and it should start working.
