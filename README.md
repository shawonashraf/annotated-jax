# annotated-jax

> Deep Learning examples using the Jax ecosystem of libraries

## env setup

> [!IMPORTANT]
> Ensure that you've `uv` installed.

The base install is CPU-only. Accelerator backends live in separate uv dependency groups; pick the one that matches your hardware. The groups are mutually exclusive, and `uv sync` removes whichever backend you had before, so switching is just another `uv sync --group <backend>`.

| backend | command | notes |
|---|---|---|
| cpu | `uv sync` | works everywhere |
| nvidia cuda | `uv sync --group cuda` | linux only; cuda and cudnn come bundled as pip wheels, you only need the nvidia driver |
| amd rocm | `uv sync --group rocm` | linux x86_64 only; expects a system-wide ROCm 7 install, the plugin does not bundle it |
| apple mps | `uv sync --group mps` | macos on apple silicon |

Then activate the environment:

```bash
source .venv/bin/activate
```

Selecting a group on the wrong platform is a no-op, e.g. `--group cuda` on macos installs nothing extra and jax falls back to cpu.

> [!TIP]
> You can also use the provided devcontainer configuration.
> ```bash
> devcontainer up --workspace-folder .
> ```

## jupyter lab

```bash
# inside the project root
uv run jupyter lab
```

## running on nvidia gpus with cuda

After `uv sync --group cuda`, jax picks the gpu automatically. Verify with:

```bash
uv run utils/device.py
```

which should log `XLA DEVICE: gpu`.

## running on amd gpus with rocm

Install ROCm 7 first (see the [ROCm install guide](https://rocm.docs.amd.com/)), then `uv sync --group rocm`. The `rocm` group uses jax's `rocm7-local` extra, which links against the system ROCm libraries rather than shipping its own. Verify the same way as cuda; the device also reports as `gpu`.

## running on apple silicon with mps support

`jax-metal` has long been unmaintained and the subsequent updates to the `jax` project have made it incompatible. This project uses a community developed extension called `jax-mps`, installed via the `mps` group.

```bash
uv sync --group mps
```

`jax-mps` does not register itself as the default backend, so set `JAX_PLATFORMS=mps` when running a script:

```bash
JAX_PLATFORMS=mps uv run utils/device.py
```

Inside jupyter notebooks, either set the env var before starting the kernel or call `setup_backend()` from `utils/device.py` before importing anything that initialises jax. The `mps` backend is still experimental upstream, so not every jax op is supported yet.
