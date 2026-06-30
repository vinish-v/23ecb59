try:
    # pyrefly: ignore [missing-import]
    from logging_middleware import Log as send_remote_log  
except ImportError:
    def send_remote_log(stack, level, package, message):
        pass

def log_info(pkg: str, msg: str):
    print(f"INFO: [{pkg}] {msg}")
    send_remote_log(stack="backend", level="info", package=pkg, message=msg)

def log_error(pkg: str, msg: str):
    print(f"ERROR: [{pkg}] {msg}")
    send_remote_log(stack="backend", level="error", package=pkg, message=msg)

def log_warn(pkg: str, msg: str):
    print(f"WARN: [{pkg}] {msg}")
    send_remote_log(stack="backend", level="warn", package=pkg, message=msg)

def log_debug(pkg: str, msg: str):
    print(f"DEBUG: [{pkg}] {msg}")
    send_remote_log(stack="backend", level="debug", package=pkg, message=msg)
