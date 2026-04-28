"""Claude Desktop 第三方 API 切换脚本。

将选中的 provider 写入 HKCU\\SOFTWARE\\Policies\\Claude，
等同于 Claude Desktop 的 Developer -> Configure third-party inference -> Apply locally。
仅支持 Windows。
"""

import json
import sys
import winreg
from pathlib import Path

ROOT = Path(__file__).parent
PRESETS_FILE = ROOT / "presets.json"
MODELS_FILE = ROOT / "models.json"
REG_PATH = r"SOFTWARE\Policies\Claude"


def load_presets() -> dict:
    return json.loads(PRESETS_FILE.read_text(encoding="utf-8"))


def load_models() -> dict:
    if not MODELS_FILE.exists():
        return {}
    try:
        return json.loads(MODELS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_models(data: dict) -> None:
    MODELS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def mask(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 12:
        return key[:2] + "..." + key[-2:]
    return key[:6] + "..." + key[-4:]


def model_name_list(models: list) -> list:
    out = []
    for m in models:
        out.append(m if isinstance(m, str) else m.get("name", ""))
    return [n for n in out if n]


def serialize_headers(extra_headers: dict, api_key: str) -> str:
    if not extra_headers:
        return "[]"
    items = []
    for name, value in extra_headers.items():
        v = str(value).replace("{apiKey}", api_key) if "{apiKey}" in str(value) else str(value)
        items.append(f"{name}: {v}")
    return json.dumps(items, ensure_ascii=False, separators=(",", ":"))


def serialize_models(models: list) -> str:
    items = []
    for m in models:
        if isinstance(m, str):
            items.append({"name": m, "displayName": m})
        else:
            items.append({k: v for k, v in m.items() if v is not None})
    return json.dumps(items, ensure_ascii=False, separators=(",", ":"))


def write_registry(preset: dict, api_key: str) -> None:
    headers_json = serialize_headers(preset.get("extraHeaders") or {}, api_key)
    models_json = serialize_models(preset.get("models") or [])
    auth_scheme = preset.get("authScheme") or "bearer"

    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
    try:
        values = [
            ("inferenceProvider", winreg.REG_SZ, "gateway"),
            ("inferenceGatewayBaseUrl", winreg.REG_SZ, preset["baseUrl"]),
            ("inferenceGatewayApiKey", winreg.REG_SZ, api_key),
            ("inferenceGatewayAuthScheme", winreg.REG_SZ, auth_scheme),
            ("inferenceGatewayHeaders", winreg.REG_SZ, headers_json),
            ("inferenceModels", winreg.REG_SZ, models_json),
            ("isClaudeCodeForDesktopEnabled", winreg.REG_DWORD, 1),
            ("ccds_managed", winreg.REG_SZ, "true"),
        ]
        for name, type_, value in values:
            winreg.SetValueEx(key, name, 0, type_, value)
    finally:
        winreg.CloseKey(key)


def prompt_choice(prompt: str, n: int) -> int | None:
    raw = input(prompt).strip()
    if not raw:
        return None
    try:
        idx = int(raw) - 1
    except ValueError:
        return None
    if idx < 0 or idx >= n:
        return None
    return idx


def cmd_switch() -> None:
    presets = load_presets()
    models = load_models()

    saved = [(pid, presets[pid]) for pid in presets if pid in models]
    print()
    print("=" * 50)
    print("  切换 Claude Desktop API")
    print("=" * 50)
    print()

    if not saved:
        print("  还没有保存任何配置。")
        print("  请先运行 add.bat 添加 API Key。")
        return

    for i, (pid, preset) in enumerate(saved, 1):
        api_key = models[pid].get("apiKey", "")
        print(f"  [{i}] {preset['name']:<20}  {mask(api_key)}")
    print()

    idx = prompt_choice(f"请选择 [1-{len(saved)}]: ", len(saved))
    if idx is None:
        print("\n[!] 无效选择，已取消。")
        return

    pid, preset = saved[idx]
    api_key = models[pid]["apiKey"]
    write_registry(preset, api_key)

    print()
    print(f"  [OK] 已切换到 {preset['name']}")
    print(f"       Endpoint : {preset['baseUrl']}")
    print(f"       Models   : {', '.join(model_name_list(preset['models']))}")
    print()
    print("  >>> 请完全退出并重新打开 Claude Desktop，配置才会生效 <<<")


def cmd_add() -> None:
    presets = load_presets()
    models = load_models()
    plist = list(presets.items())

    print()
    print("=" * 50)
    print("  添加 Claude Desktop API 配置")
    print("=" * 50)
    print()
    for i, (pid, preset) in enumerate(plist, 1):
        marker = "  (已配置)" if pid in models else ""
        print(f"  [{i}] {preset['name']}{marker}")
    print()

    idx = prompt_choice(f"请选择厂商 [1-{len(plist)}]: ", len(plist))
    if idx is None:
        print("\n[!] 无效选择，已取消。")
        return

    pid, preset = plist[idx]

    if pid in models:
        old = models[pid].get("apiKey", "")
        print(f"\n  该厂商已有配置: {mask(old)}")
        confirm = input("  是否覆盖? [y/N]: ").strip().lower()
        if confirm != "y":
            print("\n[!] 已取消。")
            return

    print()
    print(f"  Base URL : {preset['baseUrl']}")
    print(f"  Auth     : {preset.get('authScheme', 'bearer')}")
    print(f"  Models   : {', '.join(model_name_list(preset['models']))}")
    print()
    api_key = input(f"请粘贴 {preset['name']} 的 API Key: ").strip()
    if not api_key:
        print("\n[!] API Key 不能为空，已取消。")
        return

    models[pid] = {"apiKey": api_key}
    save_models(models)

    print()
    print(f"  [OK] 已保存到 {MODELS_FILE.name}")
    print("       运行 switch.bat 即可切换到该配置。")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "switch"
    try:
        if cmd == "switch":
            cmd_switch()
        elif cmd == "add":
            cmd_add()
        else:
            print(f"未知命令: {cmd}")
            print("用法: python claude_api_switch.py [switch|add]")
    except KeyboardInterrupt:
        print("\n\n[!] 已取消。")


if __name__ == "__main__":
    main()
