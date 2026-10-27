# 输入与操作

Python 3.10+，依赖 `python-docx`、`pypdf`。在 Codex 中优先使用内置文档运行时；普通 Python 用户可在隔离环境安装 `requirements.txt`。脚本只处理用户已授权的本地文献目录与 Zotero。

## 路径配置

复制 `config.example.json` 到工作区的私人配置，填写 `paper_root`。相对路径相对于配置文件所在目录；不要把实际个人配置提交 GitHub。

```json
{
  "paper_root": "./Literature/Papers",
  "pdf_subdir": "文献",
  "word_subdir": "简读",
  "collection_name": "学术论文选读",
  "discipline": "",
  "research_focus": ""
}
```

`discipline` 和 `research_focus` 供 Codex 选文与阅读时使用；辅助脚本不会从这些字段自动搜索论文。留空且无法从会话判断方向时，先确定研究主题。`collection_name` 必须对应本机已有的唯一 Zotero 分类。使用用户已有文件夹，不额外猜测或迁移路径。两类子目录必须位于 paper_root 内。升级不会覆盖已有私人配置；土壤等领域的个人偏好可以继续保留。

## paper JSON

`number` 与 `number_label` 必须对应，例如 7 与“七”。脚本生成中文数字，输入无需 number_label。日期必须由用户时区确定。

```json
{
  "number": 7,
  "date": "2026-10-27",
  "title": "Example research paper",
  "title_zh": "示例学术研究",
  "journal": "Example Journal",
  "year": 2024,
  "doi": "10.0000/example",
  "url": "https://example.org/article",
  "pdf_source": "https://example.org/authorized-fulltext.pdf",
  "authors": [{"firstName": "A", "lastName": "Researcher"}],
  "volume": "1",
  "pages": "1-10",
  "tags": ["研究主题", "方法类型"],
  "sections": [
    {"heading": "一句话结论", "text": "替换成基于正文核验的结论。"},
    {"heading": "研究设计或论证路径", "text": "按学科梳理对象、方法、数据、实验或证明。"},
    {"heading": "主要发现与证据", "text": "关键数据及正文图表位置。"},
    {"heading": "局限与课题启发", "text": "区分实测结果、作者解释与研究建议。"}
  ]
}
```

示例为虚构元数据，不能当作真实论文。实际 sections 应覆盖 SKILL.md 的阅读要求，标题文字可调整。

## 命令

```text
python scripts/workflow.py prepare --config /path/private.json --paper /path/paper.json --pdf /path/lawful.pdf --work /path/task
python scripts/workflow.py zotero-import --work /path/task
python scripts/workflow.py zotero-import --work /path/task --commit
```

prepare 将正文复制到配置的文献目录，将 Word 写入简读目录，任务目录保存导入 JSON 与 manifest。各文件含相同编号；DOI、编号账本保存在 paper_root/.paper-workflow/。不要发布该账本或任务目录。相同 DOI/题名的再次 prepare 会停止；已占用编号也会停止，避免静默覆盖。

Zotero 需先运行；脚本先读取官方 `getSelectedCollection` 返回的可用分类，按名称找到唯一目标。两个同名分类需先由用户或界面区分。导入前再次检索现有库排除重复；脚本账本只能覆盖通过本脚本整理的文献。

正式导入会调用官方 Connector 的 `saveItems`、`updateSession` 和 `saveAttachment`。正文从已校验的本地文件以 `application/pdf` 传入，避免 Zotero 网络下载失败。保存会话失效时，保留现有条目，先核查再用界面补齐；不要新建另一条。

render 工作流依环境选择可用文档渲染器，例如内置 documents 技能或 LibreOffice。若用本机 Word 导出后出现退出错误，先核验导出的 PDF 是否完整，再决定是否重试。

## 完成条件

- PDF 签名、页数、题名与正文一致；没有用 SI 或付费登录页代替正文。
- 文件名与笔记编号相同，无覆盖或重复。
- Word 已逐页检查，科学结论可回溯到来源。
- Zotero 有正确书目信息、完整命名的笔记、目标主题分类和可打开的 PDF。
- 只有界面/API核实后，才能把 Zotero 项报告为全部完成。
