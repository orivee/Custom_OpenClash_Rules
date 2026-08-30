#!/usr/bin/env python3
"""Synchronize the upstream Clash template and add OneVoid policy entries."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


UPSTREAM_URL = (
    "https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/"
    "main/cfg/Custom_Clash.ini"
)
ONEVOID_BEGIN = "; BEGIN OneVoid additions"
ONEVOID_END = "; END OneVoid additions"
ONEVOID_BLOCK = """; BEGIN OneVoid additions

; mail.onevoid.me 强制直连
ruleset=🎯 全球直连,[]DOMAIN,mail.onevoid.me

; 其他 onevoid.me 域名进入自定义策略组
ruleset=🌌 OneVoid,[]DOMAIN-SUFFIX,onevoid.me

custom_proxy_group=🌌 OneVoid`select`[]🚀 手动选择`[]♻️ 自动选择`[]🇭🇰 香港节点`[]🇺🇸 美国节点`[]🇯🇵 日本节点`[]🇸🇬 新加坡节点`[]🇼🇸 台湾节点`[]🇰🇷 韩国节点`[]🎯 全球直连`.*

; END OneVoid additions"""
REQUIRED_GROUPS = frozenset(
    {
        "🎯 全球直连",
        "🚀 手动选择",
        "♻️ 自动选择",
        "🇭🇰 香港节点",
        "🇺🇸 美国节点",
        "🇯🇵 日本节点",
        "🇸🇬 新加坡节点",
        "🇼🇸 台湾节点",
        "🇰🇷 韩国节点",
    }
)


def fetch_upstream(url: str = UPSTREAM_URL) -> str:
    request = Request(
        url,
        headers={
            "Accept": "text/plain",
            "User-Agent": "Custom_OpenClash_Rules-OneVoid-Sync/1.0",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8-sig")
    except (HTTPError, URLError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"failed to fetch upstream template: {url}: {exc}") from exc


def _remove_previous_block(text: str) -> str:
    pattern = re.compile(
        rf"(?ms)^{re.escape(ONEVOID_BEGIN)}\n.*?^{re.escape(ONEVOID_END)}\n?"
    )
    return pattern.sub("", text)


def _group_names(text: str) -> set[str]:
    return {
        line.split("`", 1)[0].removeprefix("custom_proxy_group=")
        for line in text.splitlines()
        if line.startswith("custom_proxy_group=")
    }


def validate_merged_config(text: str) -> None:
    custom_sections = re.findall(r"(?m)^\[custom\]\s*$", text)
    if len(custom_sections) != 1:
        raise ValueError(f"expected exactly one [custom] section, got {len(custom_sections)}")

    if text.count(ONEVOID_BEGIN) != 1 or text.count(ONEVOID_END) != 1:
        raise ValueError("OneVoid marker block is missing or duplicated")

    missing_groups = sorted(REQUIRED_GROUPS - _group_names(text))
    if missing_groups:
        raise ValueError(f"upstream policy groups are missing: {missing_groups}")

    exact_rule = "ruleset=🎯 全球直连,[]DOMAIN,mail.onevoid.me"
    suffix_rule = "ruleset=🌌 OneVoid,[]DOMAIN-SUFFIX,onevoid.me"
    if text.count(exact_rule) != 1 or text.count(suffix_rule) != 1:
        raise ValueError("OneVoid rules are missing or duplicated")
    if text.index(exact_rule) > text.index(suffix_rule):
        raise ValueError("mail.onevoid.me rule must precede the onevoid.me suffix rule")


def merge_upstream_config(upstream_text: str) -> str:
    text = upstream_text.replace("\r\n", "\n").replace("\r", "\n")
    text = _remove_previous_block(text)
    section_matches = list(re.finditer(r"(?m)^\[custom\]\s*$", text))
    if len(section_matches) != 1:
        raise ValueError(f"expected exactly one [custom] section, got {len(section_matches)}")

    section_end = section_matches[0].end()
    merged = (
        text[:section_end]
        + "\n"
        + ONEVOID_BLOCK
        + "\n"
        + text[section_end:].lstrip("\n")
    )
    merged = merged.rstrip() + "\n"
    validate_merged_config(merged)
    return merged


def write_atomically(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as temporary:
        temporary.write(content)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream-url", default=UPSTREAM_URL)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "cfg" / "Custom_Clash.ini",
    )
    parser.add_argument("--check", action="store_true", help="check the tracked output")
    args = parser.parse_args()

    expected = merge_upstream_config(fetch_upstream(args.upstream_url))
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != expected:
            print(f"outdated synchronized template: {args.output}")
            return 1
        print("synchronized Clash template is current")
        return 0

    write_atomically(args.output, expected)
    print(f"synchronized {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
