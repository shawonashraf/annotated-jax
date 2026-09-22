# annotated-jax

> Deep Learning examples using the Jax ecosystem of libraries

## env setup

> [!IMPORTANT]
> Ensure that you've `uv` installed.

```bash
uv sync
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
