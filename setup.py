from setuptools import setup

setup(
    name="kgbench",
    version="0.1",
    description="A KGE toolbox featured with AutoML",
    url="https://github.com/AutoML-Research/KGBench",
    author="Lin Li",
    author_email="lli18@mails.tsinghua.edu.cn",
    packages=["kgbench"],
    install_requires=[
        "numpy==1.19.*",
        "torch==1.13.1",
        "pyyaml",
        "pandas",
        "argparse",
        "path",
        # please check correct behaviour when updating ax platform version!!
        "ax-platform==0.1.19", "botorch==0.4.0", "gpytorch==1.4.2",
        "sqlalchemy",
        "torchviz",
        # LibKGE uses numba typed-dicts which is part of the experimental numba API
        # see http://numba.pydata.org/numba-doc/0.50.1/reference/pysupported.html
        "numba==0.50.*",
        "networkx==2.6.3",
        "ogb==1.3.3",
        "setproctitle==1.2.2",
    ],
    # Ax 0.1.10 requires python 3.7. Numba does not yet support for Python 3.9:
    # https://github.com/numba/numba/issues/6345
    python_requires=">=3.7,<3.9",
    zip_safe=False,
    entry_points={"console_scripts": ["kgbench = kgbench.cli:main",],},
)
