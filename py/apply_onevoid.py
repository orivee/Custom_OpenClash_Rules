#!/usr/bin/env python3
"""从本地上游标准模板生成含 OneVoid、Samsung 定制的个人模板。"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cfg" / "Custom_Clash.ini"
OUTPUT = ROOT / "custom" / "onevoid" / "Custom_Clash.ini"
GROUP_NAME = "🌌 OneVoid"
CANDIDATES = (
    "🚀 手动选择",
    "♻️ 自动选择",
    "🇭🇰 香港节点",
    "🇺🇸 美国节点",
    "🇯🇵 日本节点",
    "🇸🇬 新加坡节点",
    "🇼🇸 台湾节点",
    "🇰🇷 韩国节点",
    "🎯 全球直连",
)
SAMSUNG_GROUP_NAME = "📱 Samsung"
SAMSUNG_URL = (
    "https://raw.githubusercontent.com/Keviin560/Shunt_Rules/"
    "main/rule/Mihomo/Samsung.mrs"
)
SAMSUNG_RULE = f"ruleset={SAMSUNG_GROUP_NAME},clash-domain:{SAMSUNG_URL},86400"
SAMSUNG_CANDIDATES = (
    "♻️ 自动选择",
    "🎯 全球直连",
    *(name for name in CANDIDATES if name not in {"♻️ 自动选择", "🎯 全球直连"}),
)
RULES = (
    "ruleset=🎯 全球直连,[]DOMAIN,mail.onevoid.me",
    "ruleset=🌌 OneVoid,[]DOMAIN-SUFFIX,onevoid.me",
    SAMSUNG_RULE,
)
BEGIN = "; BEGIN personal additions"
END = "; END personal additions"
GROUP = "custom_proxy_group=" + GROUP_NAME + "`select`" + "`".join(
    "[]" + name for name in CANDIDATES
) + "`.*"
SAMSUNG_GROUP = "custom_proxy_group=" + SAMSUNG_GROUP_NAME + "`select`" + "`".join(
    "[]" + name for name in SAMSUNG_CANDIDATES
) + "`.*"
BLOCK = "\n".join((
    BEGIN,
    "; mail.onevoid.me 优先直连，其余 onevoid.me 域名使用 OneVoid 策略组",
    *RULES[:2],
    "; Samsung 域名使用独立策略组，远程规则每 24 小时更新",
    SAMSUNG_RULE,
    GROUP,
    SAMSUNG_GROUP,
    END,
))
SECTION = re.compile(r"(?m)^[ \t]*\[([^\]\r\n]+)\][ \t]*(?:\r?\n|$)")


def render(source: str) -> str:
    """校验上游依赖，只插入个人区块，保留其余内容和规则顺序。"""
    sections = list(SECTION.finditer(source))
    custom = [match for match in sections if match.group(1) == "custom"]
    if len(custom) != 1:
        raise ValueError(f"需要唯一的 [custom] 段，实际为 {len(custom)} 个")
    section = custom[0]
    section_end = next(
        (match.start() for match in sections if match.start() > section.start()),
        len(source),
    )
    body = source[section.end():section_end]
    lines = [line.strip() for line in body.splitlines()]
    group_names = [
        line.removeprefix("custom_proxy_group=").split("`", 1)[0]
        for line in lines if line.startswith("custom_proxy_group=")
    ]
    missing = sorted(set(CANDIDATES) - set(group_names))
    if missing:
        raise ValueError("上游缺少所需策略组：" + ", ".join(missing))
    duplicates = sorted(name for name, count in Counter(group_names).items() if count > 1)
    if duplicates:
        raise ValueError("上游策略组名称重复：" + ", ".join(duplicates))
    if not any(line.startswith("ruleset=") for line in lines):
        raise ValueError("上游 [custom] 段缺少 ruleset 指令")
    markers = (BEGIN, END, "; BEGIN OneVoid additions", "; END OneVoid additions")
    if any(marker in source for marker in markers) or {GROUP_NAME, SAMSUNG_GROUP_NAME} & set(group_names):
        raise ValueError("输入已含个人定制，应读取未经定制的上游模板")
    for domain in ("onevoid.me", "samsung"):
        if any(line.startswith("ruleset=") and domain in line.casefold() for line in lines):
            raise ValueError(f"上游已有 {domain} 规则，需要人工核对优先级")

    newline = "\r\n" if section.group(0).endswith("\r\n") else "\n"
    prefix = source[:section.end()]
    if not prefix.endswith("\n"):
        prefix += newline
    return prefix + BLOCK.replace("\n", newline) + newline + source[section.end():]


def write_atomically(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
        temporary_path.chmod(0o644)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只检查，不写入文件")
    args = parser.parse_args(argv)
    try:
        # 保留换行及 BOM，避免改写从上游继承的内容。
        source = SOURCE.read_bytes().decode("utf-8")
        if source.startswith("\ufeff"):
            expected = ("\ufeff" + render(source[1:])).encode("utf-8")
        else:
            expected = render(source).encode("utf-8")
        if args.check:
            if not OUTPUT.exists() or OUTPUT.read_bytes() != expected:
                print("个人模板缺失或已过期，请运行 python py/apply_onevoid.py", file=sys.stderr)
                return 1
            print("个人模板与当前上游输入一致")
        elif OUTPUT.exists() and OUTPUT.read_bytes() == expected:
            print(f"无需更新：{OUTPUT.relative_to(ROOT)}")
        else:
            write_atomically(OUTPUT, expected)
            print(f"已生成：{OUTPUT.relative_to(ROOT)}")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"个人模板生成失败：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
