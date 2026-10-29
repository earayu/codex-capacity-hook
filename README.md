# codex-capacity-hook

A tiny Codex CLI wrapper that watches terminal output for:

```text
Selected model is at capacity. Please try a different model.
```

When the message appears, it opens an X draft containing the message and `@tibo @openai`. **You decide whether to click Post.** It does not auto-post, use X API credentials, or send your Codex session anywhere.

## Requirements

- macOS, Linux, or WSL
- Python 3.9+
- Codex CLI
- zsh or bash

## Install

```bash
tmp="$(mktemp -d)" && \
  git clone --depth 1 https://github.com/earayu/codex-capacity-hook.git "$tmp/repo" && \
  python3 "$tmp/repo/install.py"
```

The installer prints the shell file to source. For zsh, this is usually:

```bash
source ~/.zshrc
```

For bash:

```bash
source ~/.bashrc
```

Restarting the terminal works too. Then run `codex` as usual.

The installer only writes `~/.codex/capacity-x/capacity_x.py` and a marked `codex()` function in your zsh or bash startup file. Existing startup content is preserved, and rerunning the installer does not duplicate the function.

## Prompt for your agent

```text
Clone https://github.com/earayu/codex-capacity-hook into a temporary directory. Inspect install.py and capacity_x.py, then run python3 install.py. Only change ~/.codex/capacity-x and the marked codex-capacity-x block in my zsh or bash startup file. Print the source command I need to activate it; do not post anything to X.
```

## How it works

The shell function runs Codex through `capacity_x.py`. In an interactive terminal, the script allocates a pseudo-terminal so the Codex interface keeps working. It scans the output, preserves the original output and exit status, and opens this X Web Intent after a match:

```text
Selected model is at capacity. Please try a different model.

@tibo @openai
```

Repeated screen redraws within two seconds produce only one draft. Native Windows shells are not supported; use WSL.
