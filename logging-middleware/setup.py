from setuptools import setup

setup(
    name="logging_middleware",
    version="1.0.0",
    packages=["logging_middleware"],
    package_dir={"logging_middleware": "."},
    description="Reusable Remote Logging Middleware for Campus Evaluation Application",
    author="vinish v",
    install_requires=[
        "requests>=2.31.0"
    ]
)
