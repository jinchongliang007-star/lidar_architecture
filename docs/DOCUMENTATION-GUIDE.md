# 教材文档生成指南

本文档介绍如何编辑 Markdown 教材文件并将其转换为 PDF 格式。

## 目录结构

```
docs/
├── textbook/
│   ├── lidar-teaching-material.md    # Markdown 源文件（主文件）
│   ├── lidar-teaching-material.html  # 生成的 HTML 文件
│   └── lidar-teaching-material.pdf   # 生成的 PDF 文件
├── images/
│   ├── main-interface.png            # 截图文件
│   ├── lidar-model-side.png
│   └── ...
└── DOCUMENTATION-GUIDE.md            # 本文档
```

## 第一步：编辑 Markdown 文件

### 源文件位置

教材的主文件是 `docs/textbook/lidar-teaching-material.md`

### Markdown 基本语法

```markdown
# 一级标题

## 二级标题

### 三级标题

**粗体文本**
*斜体文本*

- 无序列表项 1
- 无序列表项 2

1. 有序列表项 1
2. 有序列表项 2

[链接文字](URL)

![图片描述](图片路径)

| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 内容1 | 内容2 | 内容3 |

`行内代码`

```python
# 代码块
def hello():
    print("Hello, World!")
```
```

### 引用图片

图片使用相对路径引用：

```markdown
![主界面](../images/main-interface.png)
```

- `../images/` 表示从 `textbook/` 目录返回到上级 `docs/` 目录，再进入 `images/` 目录

## 第二步：生成 HTML 文件

### 使用转换脚本

项目提供了 `convert_to_html.py` 脚本用于将 Markdown 转换为 HTML：

```bash
cd /Users/jinchongliang/Downloads/lidar_architecture
python convert_to_html.py
```

### 转换脚本说明

脚本位置：`convert_to_html.py`

脚本功能：
1. 读取 `docs/textbook/lidar-teaching-material.md`
2. 使用 Python `markdown` 库转换为 HTML
3. 应用 CSS 样式模板（包含打印优化）
4. 输出到 `docs/textbook/lidar-teaching-material.html`

### HTML 特性

生成的 HTML 文件包含：
- 响应式布局
- 代码高亮样式
- 表格美化
- 打印优化（分页控制）
- 右上角"打印/导出 PDF"按钮

## 第三步：转换为 PDF

### 方法一：使用浏览器打印（推荐）

1. **启动本地服务器**

   ```bash
   cd /Users/jinchongliang/Downloads/lidar_architecture/docs
   python -m http.server 8888
   ```

2. **在浏览器中打开**

   ```
   http://localhost:8888/textbook/lidar-teaching-material.html
   ```

3. **打印为 PDF**

   - Mac: 按 `Cmd + P`
   - Windows: 按 `Ctrl + P`
   - 选择"另存为 PDF"或"Save as PDF"

### 方法二：使用 Playwright 自动化

如果安装了 Playwright，可以使用以下 Python 代码：

```python
from playwright.sync_api import sync_playwright

def convert_to_pdf():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 打开 HTML 文件
        page.goto('http://localhost:8888/textbook/lidar-teaching-material.html')
        page.wait_for_load_state('networkidle')

        # 生成 PDF
        page.pdf(
            path='docs/textbook/lidar-teaching-material.pdf',
            format='A4',
            margin={
                'top': '20mm',
                'bottom': '20mm',
                'left': '15mm',
                'right': '15mm'
            },
            print_background=True,
            display_header_footer=True,
            header_template='<div style="font-size: 10px; text-align: center; width: 100%;">机械旋转式激光雷达教学演示系统</div>',
            footer_template='<div style="font-size: 10px; text-align: center; width: 100%;">第 <span class="pageNumber"></span> 页</div>'
        )

        browser.close()

if __name__ == '__main__':
    convert_to_pdf()
```

### 方法三：使用 Pandoc（可选）

如果安装了 Pandoc：

```bash
# 安装 Pandoc（Mac）
brew install pandoc

# 转换为 PDF
pandoc docs/textbook/lidar-teaching-material.md \
  -o docs/textbook/lidar-teaching-material.pdf \
  --pdf-engine=xelatex \
  -V mainfont="PingFang SC" \
  --resource-path=docs
```

## 完整工作流程

### 修改教材内容

```bash
# 1. 编辑 Markdown 文件
vim docs/textbook/lidar-teaching-material.md
# 或使用任何文本编辑器

# 2. 重新生成 HTML
python convert_to_html.py

# 3. 转换为 PDF（选择一种方法）
# - 浏览器打印
# - Playwright 自动化
# - Pandoc 命令行
```

### 添加新截图

```bash
# 1. 运行截图脚本
python capture_screenshots.py

# 2. 截图自动保存到 docs/images/

# 3. 在 Markdown 中引用
![描述](../images/新截图文件名.png)
```

## 常见问题

### Q: PDF 中中文显示为乱码？

A: 确保系统安装了中文字体。浏览器打印方法通常能正确处理中文。

### Q: 图片没有显示在 PDF 中？

A:
1. 检查图片路径是否正确（使用相对路径）
2. 确保通过 HTTP 服务器访问 HTML（不能直接打开文件）
3. 等待页面完全加载后再打印

### Q: 如何修改 PDF 页面样式？

A: 编辑 `convert_to_html.py` 中的 CSS 模板：

```python
def get_html_template():
    return '''<!DOCTYPE html>
...
    <style>
        /* 修改这里的 CSS */
        body { font-size: 12pt; }
        ...
    </style>
...
'''
```

### Q: 如何添加页码？

A: 在 Playwright 的 `page.pdf()` 中设置：

```python
page.pdf(
    ...
    display_header_footer=True,
    footer_template='<div>第 <span class="pageNumber"></span> 页，共 <span class="totalPages"></span> 页</div>'
)
```

## 文件清单

| 文件 | 用途 | 格式 |
|------|------|------|
| `lidar-teaching-material.md` | 教材源文件 | Markdown |
| `lidar-teaching-material.html` | 网页版本 | HTML |
| `lidar-teaching-material.pdf` | 打印版本 | PDF |
| `convert_to_html.py` | MD→HTML 转换脚本 | Python |
| `capture_screenshots.py` | 截图脚本 | Python |

## 依赖要求

```
PyQt5>=5.15      # 运行主程序和截图
PyOpenGL>=3.1.5  # 3D 渲染
numpy>=1.21      # 数学计算
markdown>=3.4    # Markdown 转换（用于 convert_to_html.py）
```

安装依赖：
```bash
pip install -r requirements.txt
pip install markdown
```

---

*最后更新：2026年2月*
