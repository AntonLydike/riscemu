import setuptools

import riscemu

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="riscemu",
    version=riscemu.__version__,
    author=riscemu.__author__,
    author_email="pip@antonlydike.de",
    description="RISC-V userspace and machine mode emulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antonlydike/riscemu",
    project_urls={
        "Bug Tracker": "https://github.com/AntonLydike/riscemu/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=[
        "riscemu",
        "riscemu.decoder",
        "riscemu.instructions",
        "riscemu.IO",
        "riscemu.priv",
        "riscemu.types",
    ],
    package_data={
        "riscemu": ["libc/*.s", "py.typed"],
    },
    scripts=["riscemu/tools/riscemu"],
    python_requires=">=3.8",
    install_requires=["pyelftools~=0.27"],
)
