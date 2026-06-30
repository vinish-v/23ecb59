# Logging Middleware

A reusable Python package that sends structured log entries (stack, level, package, message) to the remote evaluation server.

## Installation
From the root of the workspace, run:
```bash
pip install -e ./logging-middleware
```

## Usage
```python
from logging_middleware import Log

Log(stack="backend", level="info", package="db", message="Connection established")
```
