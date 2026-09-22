from loguru import logger
from jax import extend
import os
import sys


def log_device():
    device = extend.backend.get_backend().platform

    assert device in ["cpu", "gpu", "tpu", "mps"], logger.error(
        f"Unknown device: {device}"
    )

    logger.info(f"XLA DEVICE: {device}")


def setup_backend():
    if sys.platform != "darwin":
        logger.info(
            "The `mps` backend is only supported on macOS. Skipping setup to use the default JAX backend."
        )
        return
    else:
        logger.info("Setting up JAX to use the `mps` backend.")
        os.environ["JAX_PLATFORMS"] = "mps"
        logger.success("JAX Platform set to use the `mps` backend.")


if __name__ == "__main__":
    log_device()
