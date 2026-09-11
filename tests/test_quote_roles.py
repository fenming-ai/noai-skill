import unittest

from tests.check_text import check_corner_quote_roles, extract_body


class QuoteRoleTest(unittest.TestCase):
    def test_detects_high_risk_corner_quote_roles(self) -> None:
        body = """「帮我写一封邮件。」
最后那句「先复述」，很重要。
「简洁一点」「高级一点」，这些话都得猜。
不要说「太长」，要说「六百字以内」。
普通正文。
"""
        kinds = {item["kind"].split("（")[0] for item in check_corner_quote_roles(body)}
        self.assertEqual(kinds, {"独立示例套引号", "短标签被当引用", "同行引号成簇", "局部引号密集"})

    def test_allows_direct_quote_and_ignores_prompt_code(self) -> None:
        text = """不要说 `别太长`，要说 `控制在600字以内`。
我不会只问一句「你觉得我该怎么办」。
```prompt
「代码原文」「不参与检查」
```
"""
        self.assertEqual(check_corner_quote_roles(extract_body(text)), [])

    def test_empty_text_passes(self) -> None:
        self.assertEqual(check_corner_quote_roles(""), [])


if __name__ == "__main__":
    unittest.main()
