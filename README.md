# noai-skill

[English](README.md) · [简体中文](README.zh-CN.md)

**Reduce formulaic AI writing without erasing the writer.**

A Chinese-first editing skill for AI assistants that can read local files. It looks for formulaic expression, checks whether an edit has a real benefit, and preserves facts, qualifications, and the original voice. It can also review technical documents, interface copy, diagram labels, and code comments.

**Shortcut:** `noai: text or file path` rewrites the supplied material; `noai 检查: material` reviews only. A bare `noai` asks for material when none is clear.

## What makes it useful

- **Voice before edits:** identify the original tone, rhythm, perspective, and protected passages.
- **Signals are not verdicts:** a repeated phrase or a balanced sentence is a candidate for review, not an automatic deletion.
- **Preserve meaning both ways:** check for lost information and unsupported additions after rewriting.
- **Learn when to leave it alone:** examples include useful edits and rejected edits that would flatten the author's voice.
- **Keep the source:** file-based rewriting creates a new file plus a readable HTML comparison.

## Quick start

```bash
git clone https://github.com/fenming-ai/noai-skill.git
cd noai-skill
```

Ask your assistant to read the cloned `SKILL.md` and follow it for your text. Keep the complete folder: the entry point loads its references and examples as needed. This package does not install or call an AI model, and does not need another writing skill.

**Review only:**

```text
Read noai-skill/SKILL.md. Review article.md for formulaic expression.
Give me candidate issues and reasons; do not edit the file.
```

**Rewrite:**

```text
Read noai-skill/SKILL.md. Rewrite article.md to reduce formulaic expression.
Preserve all facts, conditions, and the original tone. Do not invent experiences.
Keep the source unchanged and save the revised text and HTML comparison separately.
```

Use paths relative to your assistant's workspace. Instructions and examples are primarily Chinese; English-language results have not been separately evaluated.

## Workflow and outputs

Read the source → establish voice and editing boundaries → find candidates → decide whether to change → verify meaning and voice.

Review mode returns a voice card and a report; zero issues is valid. File rewrite mode produces `<stem>-noai.<ext>` and `<stem>-noai-diff.html`, using the bundled `assets/diff-template.html`. Existing voice contracts are optional; their absence does not block normal use. Feedback is not uploaded anywhere by this package. Ask the assistant before saving private feedback into a shared skill folder.

## Optional text checks

Python 3.10+ is needed only for the optional scanner and local tests. The scanner flags selected wording, punctuation, and quote patterns; it does not rewrite text or determine whether AI wrote it.

```bash
python3 tests/check_text.py examples/input.md
python3 tests/check_text.py examples/input.md --strict
python3 -m unittest discover -s tests -t .
```

Report mode returns 0 for completed scans even when candidates are found. `--strict` returns 1 for flagged patterns. Missing or unreadable input and missing or malformed rule files return 1. Empty text is allowed. HTML input should be converted to body text first.

## Scope and limits

This is an editing workflow, not an AI detector, model, or benchmark result. It does not promise detector evasion or consistently better writing. Good results depend on the model and the source material. Keep useful structure, accurate technical terms, and intentional neutrality; do not add facts or personality to satisfy a style checklist.

Local tests cover scanner behavior and some instruction contracts. Teaching examples and a small cold-read exercise do not establish cross-model reliability. No private sessions or external evaluation dataset are bundled. See [evidence boundaries](references/evidence.md).


## Chinese medium- and long-form evaluation

Six original synthetic long texts and one 653-character medium-length development sample; six Skills plus plain rewriting. **gpt-6-astra / medium** for generation and model review.

| Method | Overall · 7 cases | Long · 6 cases | Medium · 1 case |
|---|---:|---:|---:|
| noai | 99.46 | 100.00 | 96.25 |
| Humanizer | 98.93 | 98.75 | 100.00 |
| shuorenhua | 98.84 | 99.27 | 96.25 |
| sepia | 98.21 | 98.33 | 97.50 |
| Plain rewriting (no Skill) | 97.95 | 98.02 | 97.50 |
| Humanizer-zh | 97.50 | 97.50 | 97.50 |
| Stop Slop | 96.88 | 96.35 | 100.00 |

Scores weight each case equally: `(long mean × 6 + medium score) / 7`. This is a descriptive aggregation across batches: long-form outputs have two blind ratings each; the medium case reuses five completed outputs and ratings, with the two missing methods evaluated separately under the same rubric. It is not a simultaneous rerun or independent holdout validation. Small score differences do not establish statistical significance or broad superiority.

[Report and methodology (Chinese)](docs/evaluations/mixed-length/README.md) · [Download HTML comparison](docs/evaluations/mixed-length/comparison.html) · [Rating data](docs/evaluations/mixed-length/results.json) · [Recompute](docs/evaluations/mixed-length/recompute.py)

All original synthetic long-form texts and rewrites are public. The medium sample is published as source location, hashes, and scores because text redistribution permission has not been confirmed. [Long-form details](docs/evaluations/long-form/README.md) remain available. High long-form scores primarily reflect preservation and editing restraint, not measured net improvement over unedited originals.

## Chinese rewriting evaluation

Six development samples, five methods, one output per sample and method. Generation and independent blind model review were both configured as **gpt-6-astra / medium**.

| Method | Mean / 100 |
|---|---:|
| Humanizer | 96.25 |
| Stop Slop | 96.25 |
| Plain rewriting (no Skill) | 95.83 |
| noai | 95.83 |
| Humanizer-zh | 94.17 |

noai tied plain rewriting in this run. These small-sample scores do not establish a statistically significant advantage or cross-model reliability.

[Evaluation report and methodology (Chinese)](docs/evaluations/chinese-rewrite/README.md) · [Download HTML report](docs/evaluations/chinese-rewrite/comparison.html) · [Results data](docs/evaluations/chinese-rewrite/results.json)

Full source texts and rewrites are not redistributed because dataset redistribution permission has not been confirmed. The report provides numerical results, source locators, and hashes.

## License and attribution

MIT for original package content. Third-party material retains its notices: see [LICENSE](LICENSE), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), and `licenses/`.
