## Logging Middleware

Reusable remote logging middleware

### Installation
Use `pip` to install the `logging_middleware` package from the project directory:
### Usage
Import `Log` from the `logging_middleware` package into your Python application:

```python
from logging_middleware import Log as send_remote_log

send_remote_log(stack="backend", level="info", package="my_module", message="Hello, world!")
```

Replace `stack`, `level`, `package`, and `message` with the appropriate values for your application.
