"""验证独立定制的优先级、上游隔离和失败时的输出保护。"""

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("apply_onevoid", ROOT / "py" / "apply_onevoid.py")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class ApplyOneVoidTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = module.SOURCE.read_bytes().decode("utf-8")

    def test_rules_precede_upstream_and_preserve_every_source_byte(self):
        result = module.render(self.source)
        original_rules = [line for line in self.source.splitlines() if line.startswith("ruleset=")]
        rules = [line for line in result.splitlines() if line.startswith("ruleset=")]
        self.assertEqual(rules, list(module.RULES) + original_rules)
        self.assertEqual(result.count(module.GROUP), 1)
        self.assertEqual(result.count(module.SAMSUNG_GROUP), 1)
        self.assertEqual(result.replace(module.BLOCK + "\n", "", 1), self.source)

    def test_samsung_remote_domain_provider_and_policy_defaults(self):
        result = module.render(self.source)
        rules = [line for line in result.splitlines() if line.startswith("ruleset=")]
        self.assertEqual(rules[:3], [
            "ruleset=🎯 全球直连,[]DOMAIN,mail.onevoid.me",
            "ruleset=🌌 OneVoid,[]DOMAIN-SUFFIX,onevoid.me",
            "ruleset=📱 Samsung,clash-domain:https://raw.githubusercontent.com/"
            "Keviin560/Shunt_Rules/main/rule/Mihomo/Samsung.mrs,86400",
        ])
        groups = {
            fields[0].removeprefix("custom_proxy_group="): fields[1:]
            for line in result.splitlines() if line.startswith("custom_proxy_group=")
            for fields in [line.split("`")]
        }
        samsung = groups["📱 Samsung"]
        self.assertEqual(samsung[:2], ["select", "[]♻️ 自动选择"])
        self.assertEqual(groups["🌌 OneVoid"][:2], ["select", "[]🚀 手动选择"])
        self.assertEqual(samsung.count("[]🎯 全球直连"), 1)
        self.assertEqual(set(samsung[1:]), set(groups["🌌 OneVoid"][1:]))
        self.assertEqual(len(samsung[1:]), len(set(samsung[1:])))

    def test_preserves_crlf_and_other_sections(self):
        source = self.source.replace("\n", "\r\n") + "[other]\r\nkey=value\r\n"
        result = module.render(source)
        self.assertEqual(result.replace(module.BLOCK.replace("\n", "\r\n") + "\r\n", "", 1), source)

    def test_rejects_missing_or_repeated_custom_section(self):
        for source in (self.source.replace("[custom]", "[renamed]"), self.source + "[custom]\n"):
            with self.subTest(source=source[:20]), self.assertRaisesRegex(ValueError, "唯一"):
                module.render(source)

    def test_groups_in_other_sections_do_not_satisfy_dependencies(self):
        group = "custom_proxy_group=" + module.CANDIDATES[0]
        source = "\n".join(line for line in self.source.splitlines() if not line.startswith(group))
        source += "\n[other]\n" + group + "`select`[]DIRECT\n"
        with self.assertRaisesRegex(ValueError, "缺少所需策略组"):
            module.render(source)

    def test_rejects_collisions_and_duplicate_groups(self):
        for addition in (
            "ruleset=other,[]DOMAIN-SUFFIX,onevoid.me",
            "custom_proxy_group=🌌 OneVoid`select`[]DIRECT",
            "custom_proxy_group=📱 Samsung`select`[]DIRECT",
            "custom_proxy_group=🎯 全球直连`select`[]DIRECT",
            "ruleset=other,[]GEOSITE,samsung",
            "ruleset=other,clash-domain:https://example.invalid/Samsung.mrs,86400",
            "; BEGIN OneVoid additions",
            module.BEGIN,
        ):
            with self.subTest(addition=addition), self.assertRaises(ValueError):
                module.render(self.source + "\n" + addition + "\n")

    def test_cli_generation_check_and_failures_preserve_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "cfg" / "Custom_Clash.ini"
            source.parent.mkdir()
            original = ("\ufeff" + self.source).encode("utf-8")
            source.write_bytes(original)
            output = root / "custom" / "onevoid" / "Custom_Clash.ini"
            with patch.multiple(module, ROOT=root, SOURCE=source, OUTPUT=output), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(module.main(["--check"]), 1)
                self.assertFalse(output.exists())
                self.assertEqual(module.main([]), 0)
                generated = output.read_bytes()
                self.assertTrue(generated.startswith(b"\xef\xbb\xbf"))
                modified = output.stat().st_mtime_ns
                self.assertEqual(module.main([]), 0)
                self.assertEqual(output.stat().st_mtime_ns, modified)
                self.assertEqual(module.main(["--check"]), 0)
                self.assertEqual(source.read_bytes(), original)
                output.write_bytes(b"stale output")
                self.assertEqual(module.main(["--check"]), 1)
                self.assertEqual(output.read_bytes(), b"stale output")
                output.write_bytes(generated)
                source.write_text("[renamed]\n", encoding="utf-8")
                self.assertEqual(module.main([]), 1)
                self.assertEqual(output.read_bytes(), generated)
                source.unlink()
                self.assertEqual(module.main([]), 1)
                self.assertEqual(output.read_bytes(), generated)


if __name__ == "__main__":
    unittest.main()
