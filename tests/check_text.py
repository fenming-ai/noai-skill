#!/usr/bin/env python3
"""AI 味道词 + 双引号频率 + 半角标点检测（noai-skill 独立版）。

用法:
  python3 tests/check_text.py article.md          # 扫描报告
  python3 tests/check_text.py article.md --strict  # 命中即退出码 1

退出码:
  0 = 全过(无 AI 味道词, 双引号 ≤6 或 ≤10警告, 无中文紧邻半角标点)
  1 = 任一检测命中(--strict 时), 或文件/词表加载失败(fail-closed)

四类检测:
1. AI 味道词: 从 references/anti-examples.md text 段
   解析反例词（- 原句：「词」格式），扫正文是否命中
2. 双引号频率: 全角"" + 半角"，≤6通过 / 7-10警告 / >10拦截
3. 功能性直角引号: 独立示例、短标签、同行多组和局部聚集
4. 半角标点: 中文紧邻的半角逗号,/分号; = 翻译腔AI味

fail-closed: 文件不存在/解析失败/词表为空 → 退出码 1 + stderr 报错
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def load_ai_words(anti_examples_path: Path) -> list[str]:
    """从 anti-examples.md text 段解析 AI 味道词。

    humanizer-zh.md 是模式参考文档（24 种 before/after 例子），词散在段落里不在表格中，
    脚本不做机械扫描——那是理解层读的，不是硬门扫的。
    anti-examples.md 的 text 段有结构化的反例词（- 原句：「词」格式），做硬门扫描。

    fail-closed: 文件不存在/解析为空 → stderr 报错 + sys.exit(1)。
    """
    words = []

    if not anti_examples_path.exists():
        print(f"❌ anti-examples.md 不存在: {anti_examples_path}", file=sys.stderr)
        sys.exit(1)

    try:
        t = anti_examples_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        print("❌ 规则文件不可读或不是 UTF-8 文本", file=sys.stderr)
        sys.exit(1)
    # 定位 ## text 到下一个二级标题（## xxx）之间，不匹配三级标题（### xxx）
    m = re.search(r"^## text\s+媒介.*?(?=^## [a-z]|\Z)", t, re.S | re.M)
    if not m:
        print("❌ anti-examples.md 中未找到 ## text 段", file=sys.stderr)
        sys.exit(1)

    block = m.group(0)
    # 两遍扫描：先收集有"检测词"的反例标题，再提取词
    # 有检测词的反例：只取检测词，跳过其原句
    # 无检测词的反例：从原句 fallback（≤10字的词级反例）
    entries = block.split("### ")[1:]  # 按反例条目拆分
    for entry in entries:
        # 检查是否有检测词
        dm = re.search(r"检测词[：:]\s*(.+?)\s*$", entry, re.M)
        if dm:
            raw = dm.group(1).strip()
            raw = re.sub(r"[（(].*?[)）]", "", raw).strip()
            for w in raw.split("/"):
                w = w.strip()
                if w and w not in words:
                    words.append(w)
        else:
            # fallback：原句字段（只取 ≤10 字的词级反例）
            om = re.search(r"原句[：:]\s*[「「]?(.+?)[」」]?\s*$", entry, re.M)
            if om:
                raw = om.group(1).strip()
                if len(raw) <= 10:
                    raw = re.sub(r"[（(].*?[)）]", "", raw).strip()
                    for w in raw.split("/"):
                        w = w.strip()
                        if w and w not in words:
                            words.append(w)

    # fail-closed: 词表为空 = 加载失败
    if not words:
        print("❌ 词表为空——anti-examples.md text 段解析无结果（文件结构变更或格式不匹配）", file=sys.stderr)
        sys.exit(1)

    return words


def extract_body(text: str) -> str:
    """提取正文: ### 正文 到 ### 配图建议, 排除代码块/注释/标题/批注。"""
    m = re.search(r"### 正文\s*\n(.*?)### 配图建议", text, re.S)
    body = m.group(1) if m else text
    body = re.sub(r"```[\s\S]*?```", "", body)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    body = re.sub(r"^#{1,6}\s.*$", "", body, flags=re.M)
    body = re.sub(r"^---+$", "", body, flags=re.M)
    body = re.sub(r"\s*//\s.*$", "", body, flags=re.M)
    return body


def check_ai_words(body: str, words: list[str]) -> list[dict]:
    """扫正文命中哪些 AI 味道词。"""
    hits = []
    for i, line in enumerate(body.split("\n"), 1):
        for w in words:
            if w and w in line:
                hits.append({"word": w, "line": i, "content": line.strip()[:80]})
    return hits


def check_quotes(body: str) -> int:
    """数正文双引号（全角"" + 半角"），不含直角引号「」。

    直角引号「」可能承担正常引用职责，
    不计入检测。只查全角""和半角"。
    """
    return len(re.findall(r'["\u201c\u201d]', body))


CORNER_PAIR = re.compile(r"「[^「」\n]+」")
CORNER_STANDALONE = re.compile(r"^\s*(?:[*_~]{1,2})?「[^「」\n]+」[。！？]?(?:[*_~]{1,2})?\s*$")
CORNER_LABEL = re.compile(r"(?:那句|这个词|所谓|叫作|称为)\s*「[^「」\n]{1,12}」")


def check_corner_quote_roles(body: str) -> list[dict]:
    """发现直角引号的高风险用法；不按全文总量误伤合理行内原话。"""
    prose: list[tuple[int, str, int]] = []
    hits: list[dict] = []
    for line_no, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "!", ">")) or stripped == "---":
            continue
        count = len(CORNER_PAIR.findall(stripped))
        prose.append((line_no, stripped, count))
        if CORNER_STANDALONE.fullmatch(stripped):
            hits.append({"kind": "独立示例套引号", "line": line_no, "content": stripped[:100]})
        if CORNER_LABEL.search(stripped):
            hits.append({"kind": "短标签被当引用", "line": line_no, "content": stripped[:100]})
        if count >= 2:
            hits.append({"kind": "同行引号成簇", "line": line_no, "content": stripped[:100]})

    clusters: list[dict] = []
    for index in range(max(0, len(prose) - 4)):
        window = prose[index:index + 5]
        total = sum(item[2] for item in window)
        if total < 4:
            continue
        candidate = {"start": window[0][0], "end": window[-1][0], "total": total,
                     "content": "｜".join(item[1] for item in window if item[2])[:100]}
        if clusters and candidate["start"] <= clusters[-1]["end"]:
            current = clusters[-1]
            current["end"] = max(current["end"], candidate["end"])
            if candidate["total"] > current["total"]:
                current.update(total=candidate["total"], content=candidate["content"])
        else:
            clusters.append(candidate)
    hits.extend({"kind": f"局部引号密集（窗口峰值{item['total']}组）", "line": item["start"],
                 "content": item["content"]} for item in clusters)
    return sorted(hits, key=lambda item: (item["line"], item["kind"]))


def check_half_width(body: str) -> list[dict]:
    """扫半角逗号/分号(紧邻中文=翻译腔AI味)。

    半角句号.因小数点/版本号易误伤, 不检测。
    只判标点任一侧紧邻中文字符的命中(放过纯英文列表/URL)。
    """
    hits = []
    pat = re.compile(r"(?<=[\u4e00-\u9fff])[,;]|[,;](?=[\u4e00-\u9fff])")
    for i, line in enumerate(body.split("\n"), 1):
        for m in pat.finditer(line):
            hits.append({"punct": m.group(0), "line": i, "content": line.strip()[:80]})
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="AI 味道词 + 双引号频率 + 半角标点检测")
    ap.add_argument("file", help="要检测的 markdown 文件")
    ap.add_argument("--strict", action="store_true", help="命中即退出码 1")
    args = ap.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"❌ 文件不存在: {path}", file=sys.stderr)
        return 1

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        print("❌ 输入文件不可读或不是 UTF-8 文本", file=sys.stderr)
        return 1
    body = extract_body(text)

    # 加载词表（fail-closed: 失败直接退出）
    base = Path(__file__).resolve().parent.parent
    anti_examples = base / "references" / "anti-examples.md"
    words = load_ai_words(anti_examples)

    # 1. AI 味道词
    ai_hits = check_ai_words(body, words)

    # 2. 双引号（分级：≤6通过 / 7-10警告 / >10拦截）
    quote_count = check_quotes(body)
    quote_pass = 6
    quote_warn = 10

    # 3. 功能性直角引号
    corner_hits = check_corner_quote_roles(body)

    # 4. 半角标点(中文紧邻)
    half_hits = check_half_width(body)

    print(f"═══ AI 味道检测 ═══")
    print(f"文件: {path.name}  词表来源: anti-examples.md(text段) ({len(words)} 词)")
    if ai_hits:
        print(f"  ✗ 命中 {len(ai_hits)} 处 AI 味道词:")
        for h in ai_hits:
            print(f"    [{h['word']}] L{h['line']}: {h['content']}")
    else:
        print(f"  ✓ 未命中 AI 味道词")

    print(f"\n═══ 双引号频率检测 ═══")
    if quote_count > quote_warn:
        print(f"  ✗ 双引号 {quote_count} 次, 超 {quote_warn} 上限")
    elif quote_count > quote_pass:
        print(f"  ⚠ 双引号 {quote_count} 次, 超 {quote_pass} 但 ≤{quote_warn}（警告不拦截）")
    else:
        print(f"  ✓ 双引号 {quote_count} 次 ≤ {quote_pass}")

    print(f"\n═══ 功能性直角引号检测 ═══")
    if corner_hits:
        print(f"  ✗ 命中 {len(corner_hits)} 处高风险用法:")
        for hit in corner_hits:
            print(f"    [{hit['kind']}] L{hit['line']}: {hit['content']}")
    else:
        print("  ✓ 未命中独立示例、短标签或局部引号聚集")

    print(f"\n═══ 半角标点检测(翻译腔) ═══")
    if half_hits:
        print(f"  ✗ 命中 {len(half_hits)} 处中文紧邻半角逗号/分号:")
        for h in half_hits[:10]:
            print(f"    [{h['punct']}] L{h['line']}: {h['content']}")
        if len(half_hits) > 10:
            print(f"    ...(共 {len(half_hits)} 处, 仅显示前 10)")
    else:
        print(f"  ✓ 未命中中文紧邻半角标点")

    fail = bool(ai_hits) or quote_count > quote_warn or bool(corner_hits) or bool(half_hits)
    print(f"\n{'❌ 不通过' if fail else '✅ 通过'}")
    return 1 if (fail and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
