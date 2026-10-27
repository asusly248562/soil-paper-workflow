# Soil Paper Workflow · 土壤论文阅读与归档助手

把**选论文、下载正文、阅读提炼、Word 简读和 Zotero 归档**串成一套可重复执行的 Codex 工作流，适合希望持续积累文献、快速回顾研究发现的土壤与生态环境研究者。

以增温、水分变化、土壤碳循环与微生物机制为主要应用场景，也支持拓展阅读土壤领域的重要发现、经典研究和方法突破。可以结合已有文献与研究资料细化选文方向，兼顾研究相关性、证据质量与启发性。

- **有依据地选文**：核对论文来源和元数据，检查已有文献，减少重复推荐。
- **下载正文 PDF**：优先合法开放全文，默认不下载补充材料。
- **生成中文简读**：梳理研究问题、实验设计、主要发现、证据局限及对课题的启发。
- **整理 Zotero**：归入主题分类，添加标签、结构化笔记和正文附件。
- **统一文献编号**：PDF、Word 和 Zotero 笔记一一对应，方便查找与长期积累。

保存位置、研究主题和分类可配置；需要持续阅读时，可配合用户设定的每日自动化运行。

## 编号一致

| 交付物 | 示例格式 |
| --- | --- |
| PDF | 日期_文献七_论文名.pdf |
| Word | 日期_文献七_中文主题.docx |
| Zotero 笔记 | 文献七｜要点｜中文主题（期刊 年份） |

PDF 放论文目录的“文献”，Word 放“简读”。编号由已有文献与 Zotero 核对后确定，不会按当天日期重新从一开始。

## 安装与使用

将本仓库下载到 Codex skills 目录下的 `soil-paper-workflow` 文件夹，确认 `SKILL.md` 直接位于该文件夹内，重新加载 Codex。Windows 默认 skills 目录为用户主目录下 `.codex/skills`，也可遵循自己的 Codex 配置。

示例请求：

> 使用 $soil-paper-workflow，找一篇增温与水分变化影响土壤碳循环的高价值论文。只下载正文 PDF，沿用已有文献编号，整理 Zotero 笔记和 Word 简读。

先在本地复制并修改 `config.example.json`，再按 [操作说明](references/workflow.md) 提供经核验的论文信息。脚本生成文件需要 Python 3.10+、python-docx 和 pypdf。Zotero 导入需要桌面版正在运行且支持官方本地 Connector 接口；不同版本应先预览和核对，无法适配时使用已授权界面工具。

```text
python scripts/workflow.py prepare --config /path/private.json --paper /path/paper.json --pdf /path/fulltext.pdf --work /path/task
python scripts/workflow.py zotero-import --work /path/task
python scripts/workflow.py zotero-import --work /path/task --commit
```

它不是全自动学术搜索引擎：Codex 负责文献筛选、来源核验与阅读，辅助脚本处理确定性的文件与导入操作。Word 生成后还需渲染检查；Zotero 操作成功后还需通过界面或官方只读 API 核实。测试仅使用隔离临时目录和本地模拟接口。

每日09:00运行需要用户另行配置自动化；安装 skill 不会创建定时任务。

## 隐私与全文权限

仓库仅含技能、通用脚本和虚构示例，不含个人研究材料、论文全文、Zotero 数据库或密钥。真实配置、文献目录、账本与任务状态留在本地。全文仅经合法开放或用户已授权的机构途径获取。

## 验证

```text
python -m unittest discover -s tests -v
```

MIT License，详见 [LICENSE](LICENSE)。
