# Claude Desktop API Switcher

A minimal Windows script to flip **Claude Desktop** between Chinese third-party
providers — DeepSeek, Kimi, MiniMax, Zhipu GLM, Alibaba Qwen — without re-typing
the endpoint, key, and model list in the Configure UI every time.

Two `.bat` shortcuts. No dependencies beyond Python 3 stdlib.

---

## How it works

Claude Desktop's **Developer → Configure third-party inference → Apply locally**
writes to the Windows registry under:

```
HKCU\SOFTWARE\Policies\Claude
```

This script writes the same keys (`inferenceProvider`, `inferenceGatewayBaseUrl`,
`inferenceGatewayApiKey`, `inferenceGatewayAuthScheme`, `inferenceGatewayHeaders`,
`inferenceModels`, `isClaudeCodeForDesktopEnabled`), so applying a config from
the terminal is identical to pressing Apply locally in the GUI.

API keys are stored only locally in `models.json` (gitignored). The base URL,
auth scheme, and model list for each provider come from `presets.json`.

---

## Requirements

- Windows
- Python 3 on `PATH`
- Claude Desktop with **developer mode** enabled
  *(Help → Troubleshooting → Enable Developer Mode)*

## Setup

```cmd
git clone https://github.com/Adversit/min_c_desktop_switch_en.git
cd min_c_desktop_switch_en
```

That's it. No install step.

## Usage

**Add an API key** — double-click `add.bat`:

```
[1] DeepSeek
[2] Kimi (月之暗面)
[3] MiniMax
[4] 智谱 GLM
[5] 通义千问 Qwen

请选择厂商 [1-5]: 4
请粘贴 智谱 GLM 的 API Key: ****
[OK] 已保存到 models.json
```

**Switch active provider** — double-click `switch.bat`:

```
[1] 智谱 GLM            sk-xxx...y8k2

请选择 [1-1]: 1
[OK] 已切换到 智谱 GLM
>>> 请完全退出并重新打开 Claude Desktop，配置才会生效 <<<
```

After switching, **fully quit Claude Desktop** (tray icon → Exit, not just close
the window) and reopen it. Claude Desktop reads the policy at startup; the new
models will appear in the in-app model picker.

---

## Supported providers

| Provider | Base URL                                       | Default models                                       |
|----------|------------------------------------------------|------------------------------------------------------|
| DeepSeek | `https://api.deepseek.com/anthropic`           | `deepseek-v4-pro`, `deepseek-v4-flash`               |
| Kimi     | `https://api.moonshot.cn/anthropic`            | `kimi-k2.6`                                          |
| MiniMax  | `https://api.minimaxi.com/anthropic`           | `MiniMax-M2`                                         |
| GLM      | `https://open.bigmodel.cn/api/anthropic`       | `glm-5.1`, `glm-4.7`                                 |
| Qwen     | `https://dashscope.aliyuncs.com/apps/anthropic`| `qwen3.6-plus`, `qwen3.6-flash`, `qwen3.6-max-preview` |

To add a new provider, append an entry to `presets.json`.

---

## File layout

```
claude_api_switch.py    main script (stdlib only, uses winreg)
presets.json            built-in base URL / auth / model defaults
switch.bat              double-click to switch provider
add.bat                 double-click to add an API key
models.json             your saved keys (auto-created, gitignored)
```

---

## Credit

Provider preset structure (URLs, model lists, the `x-api-key: {apiKey}` extra
header for DeepSeek) is taken from
[lonr-6/cc-desktop-switch](https://github.com/lonr-6/cc-desktop-switch),
which is a more full-featured GUI for the same use case.
