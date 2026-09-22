# annotated-jax

> Deep Learning examples using the Jax ecosystem of libraries

## env setup

> [!IMPORTANT]
> Ensure that you've `uv` installed.

The base install is CPU-only. Pick the dependency group that matches your accelerator; the groups are mutually exclusive.

```bash
uv sync                # cpu only
uv sync --group cuda   # nvidia gpu, linux (bundles the cuda wheels)
uv sync --group rocm   # amd gpu, linux (expects a system rocm 7 install)
uv sync --group mps    # apple silicon, macos
source .venv/bin/activate
```

> [!TIP]
> You can also use the provided devcontainer configuration.
> ```bash
> devcontainer up --workspace-folder .
> ```



## jupyter lab

```bash
# inside the project root
jupyter lab
```

## running on apple silicon with mps support

`jax-metal` has long been unmaintained and the subsequent updates to the `jax` project have made it incompatible. This project uses a community developed extension called `jax-mps`. To run a script with mps support, set the env var `JAX_PLATFORMS=mps`. Example:

```bash
JAX_PLATFORMS=mps uv run utils/device.py
```

Inside jupyter notebooks as well, set the env var. 
