#!/usr/bin/env python3
import os
from pathlib import Path
import re
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/earayu/codex-capacity-hook/stable/capacity_x.py"
START = "# >>> codex-capacity-x >>>"
END = "# <<< codex-capacity-x <<<"
BLOCK = f'''{START}
codex() {{
  command python3 "$HOME/.codex/capacity-x/capacity_x.py" "$@"
}}
{END}'''


def source_bytes():
    local = Path(__file__).resolve().with_name("capacity_x.py")
    if local.is_file():
        return local.read_bytes()
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as response:
        return response.read()


def shell_rc():
    name = Path(os.environ.get("SHELL", "")).name
    if name == "zsh":
        return Path.home() / ".zshrc"
    if name == "bash":
        return Path.home() / ".bashrc"
    raise SystemExit("Unsupported login shell. Use zsh or bash, then rerun install.py.")


def main():
    target_dir = Path.home() / ".codex" / "capacity-x"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "capacity_x.py").write_bytes(source_bytes())

    rc = shell_rc()
    previous = rc.read_text() if rc.exists() else ""
    pattern = re.compile(rf"\n?{re.escape(START)}.*?{re.escape(END)}\n?", re.DOTALL)
    retained = pattern.sub("", previous).rstrip()
    rc.write_text((retained + "\n\n" if retained else "") + BLOCK + "\n")

    print(f"Installed {target_dir / 'capacity_x.py'}")
    print(f"Updated {rc}")
    print(f"Run: source {rc}")
    print("Then use codex normally. A capacity error opens a pre-filled X draft; you choose whether to post.")


if __name__ == "__main__":
    main()
