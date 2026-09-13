#!/usr/bin/env python3
"""生成固定上下文评测快照；不调用模型、不读取评测案例。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

CORE = ['SKILL.md', 'references/editor-persona.md', 'references/human-voice.md', 'samples/prose-pairs.md']


def snapshot(root, out, includes=()):
    root, out = Path(root).resolve(), Path(out).resolve()
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True, stderr=subprocess.PIPE).strip()
    if Path(git('rev-parse', '--show-toplevel')).resolve() != root:
        raise ValueError('root 必须是 noai 仓库根目录')
    if git('status', '--porcelain'):
        raise ValueError('工作树未提交，先固定规则版本')
    commit = git('rev-parse', 'HEAD')
    if out.exists() or out.is_relative_to(root):
        raise ValueError('输出须为仓库外的新目录，禁止覆盖')
    names = list(dict.fromkeys(CORE + list(includes)))
    contents = {}
    for name in names:
        p = root / name
        if Path(name).is_absolute() or '..' in Path(name).parts or not p.resolve().is_relative_to(root) or p.is_symlink():
            raise ValueError('快照路径越界或为符号链接')
        if name != 'SKILL.md' and (Path(name).parts[0] not in ('references', 'samples') or p.suffix != '.md'):
            raise ValueError('仅允许入口及明确选择的参考/示例 Markdown')
        git('ls-files', '--error-unmatch', name)
        raw = p.read_bytes()
        committed = subprocess.check_output(['git', '-C', str(root), 'show', commit + ':' + name], stderr=subprocess.PIPE)
        if raw != committed:
            raise ValueError('读取期间规则发生变化，重新固定版本')
        if not raw.strip():
            raise ValueError('规则文件为空')
        raw.decode('utf-8')
        contents[name] = raw
    combined = '\n\n'.join('# 文件：' + name + '\n\n' + raw.decode('utf-8') for name, raw in contents.items()).encode()
    if git('rev-parse', 'HEAD') != commit or git('status', '--porcelain'):
        raise ValueError('快照期间版本发生变化')
    manifest = {'schema': 'noai-eval-snapshot/v1', 'skill_commit': commit, 'mode': 'fixed-context',
                'files': {n: hashlib.sha256(b).hexdigest() for n, b in contents.items()},
                'skill_sha256': hashlib.sha256(combined).hexdigest(),
                'not_included': sorted(str(p.relative_to(root)) for folder in ('references', 'samples') for p in (root / folder).rglob('*.md') if str(p.relative_to(root)) not in contents)}
    out.parent.mkdir(parents=True, exist_ok=True)
    # 占用目标目录，防止并发或重复运行覆写已有快照。
    out.mkdir()
    try:
        for name, raw in contents.items():
            p = out / 'files' / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
        (out / 'skill.md').write_bytes(combined)
        (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
        for name, h in manifest['files'].items():
            if hashlib.sha256((out / 'files' / name).read_bytes()).hexdigest() != h:
                raise ValueError('快照读回校验失败')
        if hashlib.sha256((out / 'skill.md').read_bytes()).hexdigest() != manifest['skill_sha256']:
            raise ValueError('组合规则读回校验失败')
    except Exception:
        shutil.rmtree(out)
        raise
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--include', action='append', default=[])
    args = parser.parse_args()
    try:
        m = snapshot(Path(__file__).resolve().parents[1], args.out, args.include)
        print(json.dumps({'ok': True, 'skill_commit': m['skill_commit'], 'files': len(m['files']), 'model_run': False}))
    except (OSError, ValueError, subprocess.CalledProcessError) as e:
        parser.exit(1, '快照失败：' + (str(e) if not isinstance(e, subprocess.CalledProcessError) else 'Git 版本或文件未追踪') + '\n')
