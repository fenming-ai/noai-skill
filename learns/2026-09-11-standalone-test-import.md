---
date: 2026-09-11
updated: 2026-09-11
tags: [lang/python, domain/skill]
severity: minor
status: fixed
related: []
---

# 测试发现不能依赖环境里的同名包

## 现象
在独立目录运行 unittest discover 并指定顶层目录时报测试目录不可导入。

## 复现
缺少 tests/__init__.py 时运行 `python3 -m unittest discover -s tests -t .`。

## 根因
测试以 tests.check_text 导入包内模块，目录却没有明确的包标识，测试发现与环境中的同名包存在歧义。

## 影响
别人克隆后不能可靠运行 README 中的验证命令。

## 缓解
在公开包加入 tests/__init__.py，不依赖外部 PYTHONPATH。

## 修复方向
从独立目录运行测试，并以隔离模式从任意工作目录执行扫描器。当前本地测试已通过。
