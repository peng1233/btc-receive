import os
import zipfile
from datetime import datetime, timezone

BTC_ADDRESS = "bc1p26d9hh7fahfxe40pv394mewq7fazzaqwt427t59j2mcszpvhd0wql4682h"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(REPO_ROOT, "dist")

TEMPLATES = [
    {
        "slug": "batch-rename",
        "title": "批量文件重命名工具（离线）",
        "py": r'''"""批量文件重命名工具（离线）

功能：
- 选择一个文件夹
- 预览：按规则生成新文件名（不执行）
- 执行：按预览结果重命名

规则：
- 可选前缀/后缀
- 可选序号（001,002...）

注意：本工具不会上传任何文件。\n
用法：python main.py
"""

import os
import sys


def list_files(folder):
    items = []
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        if os.path.isfile(p):
            items.append(name)
    items.sort()
    return items


def build_plan(files, prefix, suffix, with_index):
    plan = []
    width = max(3, len(str(len(files))))
    for i, name in enumerate(files, 1):
        base, ext = os.path.splitext(name)
        idx = (str(i).zfill(width) + "_") if with_index else ""
        new_name = f"{prefix}{idx}{base}{suffix}{ext}"
        plan.append((name, new_name))
    return plan


def main():
    print("批量文件重命名工具（离线）")
    folder = input("请输入文件夹路径：").strip().strip('"')
    if not folder or not os.path.isdir(folder):
        print("路径无效。")
        sys.exit(1)

    prefix = input("前缀（可空）：").strip()
    suffix = input("后缀（可空）：").strip()
    with_index = input("是否加序号？(y/n)：").strip().lower().startswith("y")

    files = list_files(folder)
    if not files:
        print("文件夹内没有文件。")
        return

    plan = build_plan(files, prefix, suffix, with_index)
    print("\n预览（前10条）：")
    for a, b in plan[:10]:
        print(f"{a} -> {b}")

    ok = input("\n确认执行重命名？(y/n)：").strip().lower().startswith("y")
    if not ok:
        print("已取消。")
        return

    # 执行（先检查冲突）
    targets = [b for _, b in plan]
    if len(set(targets)) != len(targets):
        print("目标文件名存在重复，已取消。")
        return

    for old, new in plan:
        os.rename(os.path.join(folder, old), os.path.join(folder, new))

    print("完成。")


if __name__ == "__main__":
    main()
''',
    },
    {
        "slug": "csv-dedup",
        "title": "CSV 去重清洗工具（离线）",
        "py": r'''"""CSV 去重清洗工具（离线）

功能：
- 读取 CSV
- 按指定列去重（或整行去重）
- 输出新 CSV

用法：python main.py
"""

import csv
import sys


def main():
    print("CSV 去重清洗工具（离线）")
    in_path = input("输入CSV路径：").strip().strip('"')
    out_path = input("输出CSV路径：").strip().strip('"')
    col = input("去重列名（留空=整行去重）：").strip()

    try:
        with open(in_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            fieldnames = reader.fieldnames or []
    except Exception as e:
        print("读取失败：", e)
        sys.exit(1)

    seen = set()
    out_rows = []
    for r in rows:
        if col:
            key = r.get(col, "")
        else:
            key = tuple((k, r.get(k, "")) for k in fieldnames)
        if key in seen:
            continue
        seen.add(key)
        out_rows.append(r)

    try:
        with open(out_path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(out_rows)
    except Exception as e:
        print("写入失败：", e)
        sys.exit(1)

    print(f"完成：{len(rows)} -> {len(out_rows)} 行")


if __name__ == "__main__":
    main()
''',
    },
]


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def make_zip(zip_path, folder):
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for fn in files:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, folder)
                z.write(full, rel)


def main():
    os.makedirs(DIST_DIR, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    idx = int(datetime.now(timezone.utc).strftime("%j")) % len(TEMPLATES)
    t = TEMPLATES[idx]

    out_dir = os.path.join(DIST_DIR, f"tool-{today}-{t['slug']}")
    if os.path.exists(out_dir):
        # clean
        for root, dirs, files in os.walk(out_dir, topdown=False):
            for f in files:
                os.remove(os.path.join(root, f))
            for d in dirs:
                os.rmdir(os.path.join(root, d))

    os.makedirs(out_dir, exist_ok=True)

    readme = f"""# {t['title']}

这是一个离线小工具（无需联网）。

## 使用方法

1. 解压 zip
2. Windows 电脑安装 Python 3（如果你已经装了就跳过）
3. 双击运行或命令行运行：

```bash
python main.py
```

## BTC 打赏

如果这个工具帮到你，欢迎 BTC 打赏：

`{BTC_ADDRESS}`
"""

    write_file(os.path.join(out_dir, "main.py"), t["py"])
    write_file(os.path.join(out_dir, "README.md"), readme)

    zip_path = os.path.join(DIST_DIR, f"{t['slug']}-{today}.zip")
    make_zip(zip_path, out_dir)

    print(zip_path)


if __name__ == "__main__":
    main()
