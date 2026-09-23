import unittest
from pathlib import Path


SKILL_TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


class VoiceContractTest(unittest.TestCase):
    def test_voice_baseline_runs_before_generation_and_review(self) -> None:
        baseline = SKILL_TEXT.index("### 步骤 1.5 · 原文语感基线")
        generation = SKILL_TEXT.index("### 步骤 3 · 生成")
        review = SKILL_TEXT.index("### 步骤 5 · 理解层检测 + 产出")
        self.assertLess(baseline, generation)
        self.assertLess(baseline, review)

    def test_voice_card_covers_article_voice_dimensions(self) -> None:
        for field in (
            "文章类型：",
            "叙述距离：",
            "情绪温度：",
            "节奏特征：",
            "用词特征：",
            "结构推进：",
            "声音保护点：",
        ):
            self.assertIn(field, SKILL_TEXT)

    def test_boundary_and_regression_guards_are_explicit(self) -> None:
        for guard in (
            "基线不足",
            "按段建立局部基线",
            "不得进入检测或改写",
            "同味回读：通过/未通过",
            "发生偏移并回退：N 处",
        ):
            self.assertIn(guard, SKILL_TEXT)

    def test_upstream_voice_contract_has_priority_over_inference(self) -> None:
        for guard in (
            "同名 `.curve.json`",
            "已有契约优先于临时推断",
            "approvedLanguage",
            "不得改写",
        ):
            self.assertIn(guard, SKILL_TEXT)

    def test_optional_zhuque_report_is_an_attention_map_not_a_verdict(self) -> None:
        for guard in (
            "zhuque-report/v1",
            "document.visible_sha256",
            "independently_scored=false",
            "不证明作者身份、原创性或平台限流原因",
            "不主动调用外部检测服务",
        ):
            self.assertIn(guard, SKILL_TEXT)

    def test_document_patterns_are_grouped_before_local_candidates(self) -> None:
        whole = SKILL_TEXT.index("先跑全文模式")
        local = SKILL_TEXT.index("段落与句子检视")
        persona = (Path(__file__).parents[1] / "references/editor-persona.md").read_text(encoding="utf-8")
        self.assertLess(whole, local)
        self.assertIn("语感卡 → 外部风险报告状态（如有）→ 全文模式 → 局部候选", SKILL_TEXT)
        self.assertIn("不把同一模式下的每个自然段分别改写", SKILL_TEXT)
        self.assertIn("可以识别并合并过度对称、短段过密等全文模式", persona)
        self.assertNotIn("不改结构（那是内容 skill 的事", persona)


if __name__ == "__main__":
    unittest.main()
