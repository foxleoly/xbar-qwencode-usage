# xbar Qwen Code & OpenCode Token Usage

A [xbar](https://github.com/matryer/xbar) plugin that displays daily token usage statistics for [Qwen Code](https://github.com/QwenLM/qwen-code) and [OpenCode](https://github.com/opencode-ai/opencode) in your macOS menu bar.

## Features

- Display token usage for both Qwen Code and OpenCode
- Real-time statistics: Total, Input, Output, Cache, Thoughts/Reasoning
- 7-day and 30-day rolling totals
- Current model name from settings
- Auto-refresh every minute
- Color-coded output for easy reading

## Prerequisites

**xbar must be installed first!** Download from [xbarapp.com](https://xbarapp.com) or install via Homebrew:

```bash
brew install --cask xbar
```

After installation, launch xbar and follow the setup instructions.

## Installation

### Automatic Installation (Recommended)

Run this one-liner in your terminal:

```bash
curl -sSL https://raw.githubusercontent.com/foxleoly/xbar-qwencode-usage/master/install.sh | bash
```

### Manual Installation

1. Make sure [xbar](https://github.com/matryer/xbar) is installed and running.

2. Download the plugin:
   ```bash
   curl -o ~/Library/Application\ Support/xbar/plugins/opencode-usage.1m.py \
     https://raw.githubusercontent.com/foxleoly/xbar-qwencode-usage/master/opencode-usage.1m.py
   chmod +x ~/Library/Application\ Support/xbar/plugins/opencode-usage.1m.py
   ```

3. Refresh xbar to load the new plugin.

### Using Git

```bash
git clone https://github.com/foxleoly/xbar-qwencode-usage.git
cd xbar-qwencode-usage
cp opencode-usage.1m.py ~/Library/Application\ Support/xbar/plugins/
chmod +x ~/Library/Application\ Support/xbar/plugins/opencode-usage.1m.py
```

## Requirements

- **[xbar](https://xbarapp.com)** - Required! This plugin runs inside xbar.
- macOS (xbar is macOS only)
- Python 3.x (usually pre-installed on macOS)

> ⚠️ **Note**: This plugin will not work without xbar. Make sure xbar is installed and running before installing this plugin.

## Data Sources

This plugin reads token usage data from the following locations:

| Tool | Data Path | Description |
|------|-----------|-------------|
| Qwen Code | `~/.qwen/projects/*/chats/*.jsonl` | JSONL log files |
| OpenCode | `~/.local/share/opencode/opencode.db` | SQLite database |

> 📝 **Note**: Qwen Code and OpenCode are NOT required dependencies. The plugin will simply show "No data" or hide the section if the corresponding data source doesn't exist.

## Configuration

The plugin reads model configuration from `~/.qwen/settings.json` to display friendly model names.

Example `settings.json`:
```json
{
  "model": {
    "name": "glm-5"
  },
  "modelProviders": {
    "openai": [
      {
        "id": "glm-5",
        "name": "[Bailian Coding Plan] glm-5"
      }
    ]
  }
}
```

## Output Example

```
OC 1.2M / QC 24.3M
---
Qwen Code
--Total: 24.3M
--Input: 24.2M
--Output: 155.9K
--Cache: 21.6M
--Thoughts: 27.9K
--7-Day: 24.3M
--30-Day: 24.3M
--Model: [Bailian Coding Plan] glm-5
---
OpenCode
--Total: 1.2M
--Input: 343.8K
--Output: 16.0K
--Cache: 860.1K
--Reasoning: 4.8K
--7-Day: 53.0M
--30-Day: 53.0M
--Model: [Bailian Coding Plan] glm-5
---
Updated: 20:06:28
```

## Customization

### Refresh Interval

Change the filename suffix to adjust refresh rate:
- `opencode-usage.1m.py` - every 1 minute
- `opencode-usage.5m.py` - every 5 minutes
- `opencode-usage.1h.py` - every 1 hour

### Colors

Edit the `color=` parameters in the script to customize colors. Supported formats:
- Named colors: `red`, `green`, `blue`
- Hex colors: `#00bcd4`, `#81d4fa`

## Uninstallation

```bash
rm ~/Library/Application\ Support/xbar/plugins/opencode-usage.1m.py
```

## License

MIT License