# ESL Beginner's Handbook — 英语初学者学习手册

一本面向 ESL 初学者的语法学习手册，由 Pandoc + Eisvogel 模板生成。

## 项目结构

```
ESLBeginner/
├── MD/                     # 源文件（Markdown）
│   ├── 01-Be 动词的用法.md
│   ├── 02-There be 句型.md
│   ├── 03-it-句型.md
│   ├── 04-Frequency.md
│   ├── 05-Comparative And Superlative.md
│   ├── 06-How to describe a person.md
│   └── 07-定语从句练习.md
├── templates/              # PDF 模板
│   └── eisvogel.latex
├── metadata.yaml           # PDF 元数据/封面配置
├── build.ps1               # 一键构建脚本
└── README.md
```

## 前置要求

- [Pandoc](https://pandoc.org/installing.html) — 文档转换引擎
- [MiKTeX](https://miktex.org/download) — LaTeX 发行版（含 xelatex）

安装命令（Windows 可用 winget）：

```powershell
winget install JohnMacFarlane.Pandoc
winget install MiKTeX.MiKTeX
```

> **注意**：首次运行 xelatex 时 MiKTeX 会自动下载所需的 LaTeX 宏包，请确保网络畅通。

## 构建 PDF

```powershell
# 一键生成
.\build.ps1

# 清理生成的 PDF
.\build.ps1 -Clean
```

输出文件：`ESL_Beginner_Handbook.pdf`

## 添加新章节

1. 在 `MD/` 目录下创建 Markdown 文件，文件名前加序号控制顺序
2. 运行 `.\build.ps1` 重新生成 PDF

## 修改封面/样式

编辑 `metadata.yaml` 中的以下字段：

| 字段 | 说明 |
|------|------|
| `title` | 标题 |
| `subtitle` | 副标题 |
| `author` | 作者 |
| `titlepage-color` | 封面背景色（十六进制） |
| `titlepage-text-color` | 封面文字颜色 |

## 许可证

MIT
