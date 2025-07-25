# 问题和修改方向

本文按照“模块-问题-建议”的格式列出，覆盖功能、鲁棒性、可维护性、可扩展性与性能五个维度。每条都给出最小改动示例或思路。

---

## converter.py

- (小)问题：`_sanitize_special_chars` 把 `|` 直接换成 `\vert`加空格，但若 `|` 已在 `\left|...\right|` 中就会破坏。  
建议：先判断是否在 `\left…\right` 或 `\lvert…\rvert` 语境中再替换。  
- 问题：连续空行合并逻辑复杂、易错。  
建议：用 `textwrap.dedent` + `re.sub('\n{3,}', '\n\n', …)` 即可，把“引用层级”留给 Markdown 渲染器处理，降低复杂度。  
- (小)问题：类名 `MathJax_Converter` 违反 PEP 8（大写下划线）。  
建议：`MathJaxConverter`。  

---

## file_processor.py

- 问题：`extract_title_from_md` 只用正则，无法应对标题前有空格或 `#` 不在行首的情况。  
建议：用 `markdown-it-py` 解析 AST，或至少 `re.search(r'^\s*#\s+(.+?)\s*$', …, re.M)`。
- 问题：PDF 复制时若 `../assets/pdf/posts` 与目标盘符不同，`shutil.copy2` 可能抛 `SameFileError`。  
建议：`if src.resolve() == dst.resolve(): pass`。  
- (小)问题：`_generate_filename` 直接把标题中的中文、空格、符号全部替换为 `-`，可读性差且可能冲突。  
建议：用 `python-slugify` 库做 slug，保留 Unicode。  
- 问题：文件写入使用 `'w'` 模式，在 Windows + 非 UTF-8 终端下易乱码。  
建议：显式 `encoding='utf-8-sig'` 或在 `open` 时加 `newline=''` 避免 `\r\r\n`。  
- (小)问题：YAML 头里的 `toc: {beginning: True}` 对 Jekyll/Hexo 并不通用，做成可配置。  
建议：把 `toc` 放进 `metadata.get('toc', {...})`。  

---

## gui.py

- 问题(已修复)：标签输入框仅支持英文逗号，中文逗号、空格会被当成标签一部分。  
建议：

```python
tags = re.split(r'[,\s，]+', self.edit_tags.text())
tags = [t.strip() for t in tags if t.strip()]
```

- 问题：`show_error` 弹窗阻塞主线程，若处理大文件用户会误以为程序卡死。  
建议：

> - 在主线程用 `QApplication.processEvents()` 或  
> - 把 `process_file` 放到 `QThread` 里。

- 问题：输出目录的持久化路径在 Windows 上可能含反斜杠，导致日志显示难看。  
建议：保存时用 `str(Path(dir))` 统一 `/`。  
- 问题：`MainWindow` 继承 `QMainWindow` 却未使用任何主窗口特性（菜单栏、工具栏、停靠窗口）。  
建议：如无扩展计划，可改继承 `QWidget` 减少开销（很明显有扩展计划）。

---

## config.py（小问题）

- 问题：路径使用 Windows 原始字符串 `r'../assets/pdf/posts/'`，在 Linux 上没问题，但 `Path` 对象可跨平台。  
建议：

```python
from pathlib import Path
pdf_storage_dir = Path(__file__).parent.parent / 'assets' / 'pdf' / 'posts'
```

- 问题：`standard_output_style` 的键是 snake_case，但 MathJax 配置通常用 camelCase；命名不一致易混淆。  
建议：

```python
MATH_OUTPUT_STYLE = {
    'inline': '$$',
    'blockBegin': '$$',
    'blockEnd': '$$\n'
    }
```

---

## main.py

- 问题：异常直接 `show_error(str(e))`，会把完整 traceback 暴露给用户。  
建议：

```python
import traceback
self.window.show_error("处理失败：\n" + traceback.format_exc())
```

- 问题：程序入口 `MainApplication().run()` 不返回退出码，CI/CD 无法捕获失败。  
建议：

```python
sys.exit(MainApplication().run())
```  

---

## 测试

- 问题：`test_manual.py` 用临时目录但 PDF 复制到真实 `../assets/pdf/posts`，测试后留下垃圾文件。  
建议：

> – 在临时目录内 mock 掉 `pdf_storage_dir`，或  
> – 用 `monkeypatch.setattr(file_processor.Path, 'resolve', lambda p: tmp_path)`。

- 问题：无单元测试覆盖 `converter.py` 的边界场景。  
建议：添加 pytest 用例，如：

> – 嵌套公式、转义美元、中文括号。
> – 空行合并保留引用层级。

---

## 打包 / 依赖

- `requirements.txt`目前缺失：

```text
PyQt5
pyyaml
python-slugify
markdown-it-py   # 可选
```

- 使用 `setuptools` 写一个 `pyproject.toml`，入口脚本改为 `python -m md_pdf_poster`。

---

## 性能

- 大文件（>1 MB Markdown）时，正则反复替换可能慢。  
建议：一次性读入后，用 `re.sub` 的 `count=1` 或 `re.finditer` + 手动切片，减少回溯。  

---

## 小结  

- 先修“鲁棒性”与“可维护性”的坑（正则、路径、异常）。  
- 再补“可扩展性”（YAML 配置、线程化、slug 化）。  
- 最后加“自动化测试”，避免后续改动回退。
