import os
import sys

def daemonize():
    """Detach from terminal and run in background (UNIX only)"""
    if os.fork() > 0:
        sys.exit()  # parent exits
    os.setsid()     # start new session
    if os.fork() > 0:
        sys.exit()  # second parent exits

    sys.stdout.flush()
    sys.stderr.flush()
    
    # Redirect standard file descriptors to /dev/null
    with open(os.devnull, 'rb', 0) as dev_null_read, \
         open(os.devnull, 'wb', 0) as dev_null_write:
        os.dup2(dev_null_read.fileno(), sys.stdin.fileno())
        os.dup2(dev_null_write.fileno(), sys.stdout.fileno())
        os.dup2(dev_null_write.fileno(), sys.stderr.fileno())
