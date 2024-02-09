import secrets

def seed_python(seed):
    """This function seeds the Python random number generator with the provided seed.
    Parameters:
        - seed (int): The seed to be used for the random number generator.
    Returns:
        - None: This function does not return any value.
    Processing Logic:
        - Uses the secrets module to seed the random number generator.
        - The seed must be an integer.
        - The same seed will always produce the same sequence of random numbers.
        - If no seed is provided, the random number generator will use a system-provided seed."""
    

    secrets.SystemRandom().seed(seed)


def seed_torch(seed):
    """Sets the seed for generating random numbers in PyTorch.
    Parameters:
        - seed (int): The seed to set for generating random numbers.
    Returns:
        - None: Does not return anything.
    Processing Logic:
        - Imports the PyTorch library.
        - Sets the seed for generating random numbers.
        - Only use this function if you want to generate reproducible results."""
    
    import torch

    torch.manual_seed(seed)


def seed_numpy(seed):
    """This function seeds the numpy random number generator with the given seed.
    Parameters:
        - seed (int): The seed to use for the numpy random number generator.
    Returns:
        - None: This function does not return anything.
    Processing Logic:
        - Imports the numpy.random module.
        - Seeds the numpy random number generator.
        - Uses the given seed to seed the generator."""
    
    import numpy.random

    numpy.random.seed(seed)


def seed_numba(seed):
    """"""
    
    import numpy as np, numba

    @numba.njit
    def seed_numba_(seed_):
        np.random.seed(seed_)

    seed_numba_(seed)


def get_seed(config, what):
    """"Returns a random seed based on the given configuration and input. If no specific seed is provided, it uses a default seed and adds an md5 hash of the input to ensure uniqueness. The returned seed is a 32-bit integer.
    Parameters:
        - config (dict): A dictionary containing configuration settings.
        - what (str): A string representing the input for the random seed.
    Returns:
        - int: A 32-bit integer representing the random seed.
    Processing Logic:
        - Uses the given configuration to retrieve a specific seed if available.
        - If no specific seed is provided, uses a default seed.
        - Adds an md5 hash of the input to the default seed to ensure uniqueness.
        - The returned seed is a 32-bit integer.""""
    
    seed = config.get(f"random_seed.{what}")
    if seed < 0 and config.get(f"random_seed.default") >= 0:
        import hashlib

        # we add an md5 hash to the default seed so that different PRNGs get a
        # different seed
        seed = (
            config.get(f"random_seed.default")
            + int(hashlib.md5(what.encode()).hexdigest(), 16)
        ) % 0xFFFF  # stay 32-bit

    return seed


def seed_from_config(config):
    """"""
    
    seed = get_seed(config, "python")
    if seed > -1:
        seed_python(seed)

    seed = get_seed(config, "torch")
    if seed > -1:
        seed_torch(seed)

    seed = get_seed(config, "numpy")
    if seed > -1:
        seed_numpy(seed)

    seed = get_seed(config, "numba")
    if seed > -1:
        seed_numba(seed)


def seed_all(default_seed, python=-1, torch=-1, numpy=-1, numba=-1):
    """"""
    
    from kgbench import Config

    config = Config()
    config.set("random_seed.default", default_seed)
    config.set("random_seed.python", python)
    config.set("random_seed.torch", torch)
    config.set("random_seed.numpy", numpy)
    config.set("random_seed.numba", numba)
    seed_from_config(config)
