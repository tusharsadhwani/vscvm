# vscvm

A VSCode version manager.

## Install

Add the following to your `.bashrc` file:

Install `vsc` via pip:

```console
pip install vscvm
```

```bash
export PATH=$HOME/.vscvm:$PATH
```

and that's it!

## Usage

```console
$ vsc list
v1.59 - July 2021
v1.58 - June 2021
v1.57 - May 2021
v1.56 - April 2021
v1.55 - March 2021

$ vsc list -n 3
v1.59 - July 2021
v1.58 - June 2021
v1.57 - May 2021

$ vsc install latest
Downloading 1.59...
Successfully installed 1.59!

$ code --version
1.59.0
```
