#!/usr/bin/env python3
import fcntl
import os
import pty
import select
import shutil
import signal
import subprocess
import sys
import termios
import time
import tty
import urllib.parse
import webbrowser

ERROR = b"Selected model is at capacity. Please try a different model."
TEXT = ERROR.decode() + "\n\n@tibo @openai"
POST_URL = "https://x.com/intent/post?" + urllib.parse.urlencode({"text": TEXT})


class CapacityDetector:
    def __init__(self):
        self.tail = b""
        self.last_open = float("-inf")

    def feed(self, data):
        data = self.tail + data
        now = time.monotonic()
        if ERROR in data and now - self.last_open >= 2.0:
            self.last_open = now
            try:
                if not webbrowser.open(POST_URL):
                    print(f"Open this URL to post: {POST_URL}", file=sys.stderr)
            except Exception as exc:
                print(f"Could not open X ({exc}). URL: {POST_URL}", file=sys.stderr)
        self.tail = data[-(len(ERROR) - 1):]


def run_with_pipe(command, detector):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        data = os.read(process.stdout.fileno(), 4096)
        if not data:
            break
        detector.feed(data)
        os.write(sys.stdout.fileno(), data)
    return process.wait()


def run_with_pty(command, detector):
    pid, master_fd = pty.fork()
    if pid == 0:
        os.execvp(command[0], command)

    def sync_window_size():
        try:
            size = fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b"\0" * 8)
            fcntl.ioctl(master_fd, termios.TIOCSWINSZ, size)
        except OSError:
            pass

    sync_window_size()
    previous_handler = signal.signal(signal.SIGWINCH, lambda *_: sync_window_size())
    mode = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
    fds = [master_fd, sys.stdin.fileno()]
    try:
        while fds:
            readable, _, _ = select.select(fds, [], [])
            if master_fd in readable:
                try:
                    data = os.read(master_fd, 4096)
                except OSError:
                    break
                if not data:
                    break
                detector.feed(data)
                os.write(sys.stdout.fileno(), data)
            if sys.stdin.fileno() in readable:
                data = os.read(sys.stdin.fileno(), 1024)
                if data:
                    os.write(master_fd, data)
                else:
                    fds.remove(sys.stdin.fileno())
    finally:
        signal.signal(signal.SIGWINCH, previous_handler)
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSAFLUSH, mode)
        os.close(master_fd)
    return os.waitstatus_to_exitcode(os.waitpid(pid, 0)[1])


def main():
    if shutil.which("codex") is None:
        print("codex: command not found", file=sys.stderr)
        return 127
    command = ["codex", *sys.argv[1:]]
    detector = CapacityDetector()
    if os.isatty(sys.stdin.fileno()) and os.isatty(sys.stdout.fileno()):
        return run_with_pty(command, detector)
    return run_with_pipe(command, detector)


if __name__ == "__main__":
    sys.exit(main())
