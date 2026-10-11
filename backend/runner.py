"""Bounded subprocess streaming, adapted from omaSearch bounded.py (MIT).

Uses nonblocking stdin as well as output so a child cannot evade the deadline
by refusing to consume a large prompt. Raw stderr never reaches the UI.
"""
import os
import selectors
import signal
import subprocess
import time


def stream_process(argv, input_data, cancel, *, timeout=120, max_bytes=1048576,
                   cwd=None, env=None, include_stderr=False):
    if cancel.is_set():
        return
    if len(input_data) > max_bytes:
        raise ValueError('Request too large')
    proc = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True, cwd=cwd, env=env)
    deadline = time.monotonic() + timeout
    counts = {proc.stdout: 0, proc.stderr: 0}
    offset = 0
    try:
        with selectors.DefaultSelector() as selector:
            for stream in (proc.stdin, proc.stdout, proc.stderr):
                os.set_blocking(stream.fileno(), False)
            selector.register(proc.stdout, selectors.EVENT_READ)
            selector.register(proc.stderr, selectors.EVENT_READ)
            if input_data:
                selector.register(proc.stdin, selectors.EVENT_WRITE)
            else:
                proc.stdin.close()
            while selector.get_map() or proc.poll() is None:
                if cancel.is_set():
                    return
                if time.monotonic() >= deadline:
                    raise TimeoutError('Provider timed out')
                for key, _ in selector.select(min(.05, max(0, deadline-time.monotonic()))):
                    stream = key.fileobj
                    if stream is proc.stdin:
                        try:
                            offset += os.write(stream.fileno(), input_data[offset:offset+4096])
                        except BrokenPipeError:
                            offset = len(input_data)
                        if offset == len(input_data):
                            selector.unregister(stream)
                            stream.close()
                        continue
                    chunk = os.read(stream.fileno(), 65536)
                    if not chunk:
                        selector.unregister(stream)
                        continue
                    counts[stream] += len(chunk)
                    if counts[stream] > max_bytes:
                        raise ValueError('Provider output exceeded limit')
                    if (stream is proc.stdout or include_stderr) and not cancel.is_set():
                        yield chunk
            if proc.returncode != 0:
                raise RuntimeError('Provider failed; check its sign-in and configuration')
    finally:
        # A leader may exit while descendants still hold pipes; kill the entire
        # original session group even when poll() says the leader has exited.
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=.2)
        except subprocess.TimeoutExpired:
            pass
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=2)
        for stream in (proc.stdin, proc.stdout, proc.stderr):
            stream.close()
