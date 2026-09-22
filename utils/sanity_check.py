import jax
from loguru import logger
from utils.device import setup_backend, log_device


def main():
    setup_backend()
    log_device()
    
    logger.info("Generating PRNGKey")
    key = jax.random.PRNGKey(0)
    logger.info("Splitting PRNGKey")
    key, _ = jax.random.split(key, 10)
    logger.success("All Good!")


if __name__ == "__main__":
    main()
