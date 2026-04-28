# Claude Desktop API 切换器

一个极简的 Windows 脚本，用来在 **Claude Desktop** 里切换国内第三方
API —— DeepSeek、Kimi、MiniMax、智谱 GLM、阿里 Qwen，避免每次都
打开 Configure 面板重新粘 endpoint、key 和模型列表。

两个 `.bat` 双击入口，纯 Python 标准库，零依赖。

[English README](README.md)

---

## 工作原理

Claude Desktop 的 **Developer → Configure third-party inference →
Apply locally** 实际写入 Windows 注册表：

```
HKCU\SOFTWARE\Policies\Claude
```

本脚本写的是同一组键（`inferenceProvider`、`inferenceGatewayBaseUrl`、
`inferenceGatewayApiKey`、`inferenceGatewayAuthScheme`、
`inferenceGatewayHeaders`、`inferenceModels`、
`isClaudeCodeForDesktopEnabled`），所以从终端切换和在 GUI 里点 Apply
locally 是完全等价的。

API Key 只存在本地的 `models.json` 里（已 gitignore，不会上传）。
各厂商的 base URL、认证方式、模型列表来自 `presets.json`。

---

## 前置条件

- Windows
- Python 3，且 `python` 在 `PATH` 里
- Claude Desktop 已开启**开发者模式**
  *（Help → Troubleshooting → Enable Developer Mode）*

## 安装

```cmd
git clone https://github.com/Adversit/min_c_desktop_switch_en.git
cd min_c_desktop_switch_en
```

不需要装任何依赖。

## 使用

**添加 API Key** —— 双击 `add.bat`：

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

**切换当前 provider** —— 双击 `switch.bat`：

```
[1] 智谱 GLM            sk-xxx...y8k2

请选择 [1-1]: 1
[OK] 已切换到 智谱 GLM
>>> 请完全退出并重新打开 Claude Desktop，配置才会生效 <<<
```

切换之后，**完全退出 Claude Desktop**（托盘图标右键 → Exit，不是
关闭窗口），然后重新打开。Claude Desktop 只在启动时读一次注册表，
重启后新模型才会出现在应用内的模型选择器里。

---

## 已支持的厂商

| 厂商      | Base URL                                        | 默认模型                                              |
|-----------|-------------------------------------------------|-------------------------------------------------------|
| DeepSeek  | `https://api.deepseek.com/anthropic`            | `deepseek-v4-pro`、`deepseek-v4-flash`                |
| Kimi      | `https://api.moonshot.cn/anthropic`             | `kimi-k2.6`                                           |
| MiniMax   | `https://api.minimaxi.com/anthropic`            | `MiniMax-M2`                                          |
| 智谱 GLM  | `https://open.bigmodel.cn/api/anthropic`        | `glm-5.1`、`glm-4.7`                                  |
| Qwen      | `https://dashscope.aliyuncs.com/apps/anthropic` | `qwen3.6-plus`、`qwen3.6-flash`、`qwen3.6-max-preview` |

需要添加新厂商，直接在 `presets.json` 里追加一项即可。

---

## 文件结构

```
claude_api_switch.py    主脚本（仅依赖标准库的 winreg）
presets.json            内置 base URL / 认证方式 / 模型列表
switch.bat              双击切换 provider
add.bat                 双击添加 API Key
models.json             你保存的 Key（自动生成，不上传）
```

---

## 致谢

Provider 预设结构（URL、模型列表、DeepSeek 的 `x-api-key: {apiKey}`
额外请求头）参考自
[lonr-6/cc-desktop-switch](https://github.com/lonr-6/cc-desktop-switch)
—— 那是一个功能更完整的同类 GUI 工具。
