import sys
import threading
import time
import unittest
from backend.runner import stream_process


class RunnerTests(unittest.TestCase):
    def run_python(self, code, **kwargs):
        return stream_process([sys.executable, '-c', code], b'Synthetic', threading.Event(), **kwargs)

    def test_streams_output_without_revealing_stderr(self):
        self.assertEqual(b''.join(self.run_python('import sys; print(sys.stdin.read()); print("private", file=sys.stderr)')), b'Synthetic\n')

    def test_deadline_even_when_child_does_not_read_input(self):
        start = time.monotonic()
        with self.assertRaises(TimeoutError):
            list(stream_process([sys.executable, '-c', 'import time; time.sleep(20)'], b'x' * 1000000, threading.Event(), timeout=.1))
        self.assertLess(time.monotonic() - start, 2)

    def test_rejects_overflow_and_nonzero_exit(self):
        with self.assertRaises(ValueError):
            list(self.run_python('print("x" * 10000)', max_bytes=50))
        with self.assertRaises(RuntimeError):
            list(self.run_python('raise SystemExit(3)'))

    def test_cancel_before_launch(self):
        cancel = threading.Event()
        cancel.set()
        self.assertEqual(list(stream_process(['/does/not/exist'], b'', cancel)), [])

    def test_cancel_stops_stream(self):
        cancel = threading.Event()
        stream = stream_process([sys.executable, '-u', '-c', 'import time; print("ready"); time.sleep(20)'], b'', cancel)
        self.assertEqual(next(stream), b'ready\n')
        cancel.set()
        start = time.monotonic()
        self.assertEqual(list(stream), [])
        self.assertLess(time.monotonic() - start, 2)
