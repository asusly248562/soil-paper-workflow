# 豆包与 DeepSeek 通用启动说明

本说明提供两条使用路线，不依赖特定产品按钮或某个版本的原生 Skills 功能。提示词可复制到支持文本指令的助手；完整执行仍取决于该环境真实提供的工具。

这份适配未在豆包或 DeepSeek 产品端做真实操作测试。仓库中的文件生成与 Zotero 辅助脚本经过隔离测试；这不代表已验证任一聊天产品对本机文件或 Zotero 的访问能力。

## 路线一 普通聊天

1. 打开[通用提示词](../prompts/universal-paper-workflow.md)，将分隔线后的内容复制到新对话。若使用的自定义助手支持长期指令，也可以保存在那里。
2. 发送下面的启动请求，填写研究方向；已经在会话中说明的信息可以省略。
3. 如需精确解读，提供你有权使用的正文 PDF；如有联网能力，可让助手先查找合法全文。
4. 将输出的简读和笔记保存或复制到自己的文档与 Zotero。只有实际提供了可下载 docx，才算生成了 Word；本机归档仍需自己完成或由可访问本机的工具执行。

```text
按刚才的论文工作流帮我整理一篇论文。
学科与研究方向：填写我的主题。
选文范围：与课题相关的高价值研究，也接受该领域重要发现。
材料偏好：只要正文 PDF。
已有文献编号：填写最后一个编号；如我已提供文献列表，先查重并核对。
输出：中文简读、可复制的 Zotero 笔记，以及核验过的正文来源链接。
如果不能访问全文、生成 Word 或操作本机，请逐项说明，不要声称已经保存或导入。
```

仅提供文件路径，不代表聊天助手能读到文件。没有联网或没有拿到正文时，只能对已提供资料作相应范围的阅读，不能承诺最新检索或正文下载。

## 路线二 具备本地工具的助手或执行宿主

当使用环境可以执行本机 Python、访问文献目录并联网时，可复用同一提示词和本仓库脚本。模型通过 API 运行时，也需要外部执行宿主提供这些工具；配置模型名称本身不会赋予本机权限。

### 1 准备文件和运行环境

下载或克隆仓库，在仓库根目录运行。需要 Python 3.10+。使用隔离环境安装依赖，例如 Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

若宿主已提供包含 python-docx 和 pypdf 的 Python，则使用该运行时，不必重复安装。macOS 或 Linux 可使用隔离环境中的 bin/python。下面示例沿用 Windows 路径；不需要激活环境。

### 2 创建私人配置

复制 config.example.json 为 config.local.json，填写你自己的路径与分类。相对路径相对于配置文件所在目录解析。

```json
{
  "paper_root": "./Literature/Papers",
  "pdf_subdir": "文献",
  "word_subdir": "简读",
  "collection_name": "学术论文选读",
  "discipline": "填写学科",
  "research_focus": "填写具体研究问题"
}
```

在 Zotero 中提前建立或选择唯一对应的 collection_name。使用既有私人配置时保留原有研究主题、路径、分类和编号；不要复制别人的用户名路径。真实配置和研究材料留在本地，不提交 GitHub。

### 3 获取正文并准备 paper JSON

让助手依通用提示词完成文献查重、合法来源核验和正文阅读。把正文 PDF 下载到本地工作目录，再按 [paper JSON 说明](../references/workflow.md)填写 paper.local.json。

paper JSON 的 sections 要写经过正文核对的结论、方法或论证、证据位置、局限和启发；脚本不会从 PDF 自动生成这些内容。编号需与已有文献核对，不能照抄文档示例中的“文献七”。

### 4 生成文件并检查

```powershell
.\.venv\Scripts\python.exe scripts/workflow.py prepare --config config.local.json --paper paper.local.json --pdf work/fulltext.pdf --work work/task-001
```

prepare 会校验正文 PDF，复制带编号的 PDF，生成中文 Word 与 Zotero 导入数据。task-001 必须是新的空目录；重跑任务时查看原 manifest，不另起一次重复编号。

使用可用的 Word 或文档渲染工具逐页检查生成结果；未渲染检查就标注尚未视觉验证。

### 5 预览并导入 Zotero

先启动本机 Zotero，确保执行脚本的环境能访问它的官方本地 Connector：

```powershell
.\.venv\Scripts\python.exe scripts/workflow.py zotero-import --work work/task-001
.\.venv\Scripts\python.exe scripts/workflow.py zotero-import --work work/task-001 --commit
```

第一条预览并读取分类，不提交；第二条才实际导入书目信息、完整命名的中文笔记和本地正文附件。脚本先定位配置中的主题分类，分类不存在或同名不唯一时停止。

Connector 使用回环地址 http://127.0.0.1:23119，脚本不需要 Zotero 账号密钥。若运行在远程服务器、云沙箱或隔离容器，127.0.0.1指向那个环境，通常不能访问你电脑上的 Zotero；不要为此把本机接口暴露到公网。改用本机执行宿主，或在本机手工运行命令。

导入后在 Zotero 界面或可用的官方只读 API 中核实标题、笔记、主题分类和可打开的 PDF。接口成功并不等于最终核实完成。

## 常见情况

| 情况 | 处理方式 |
| --- | --- |
| 助手不能联网 | 上传或粘贴有权使用的资料；不声称检索到最新研究 |
| 只能看到摘要 | 标注摘要初读，不编正文方法或数据 |
| 正文需要订阅 | 用已有机构权限或合法作者版本；指定论文不能擅自换成另一篇 |
| 没有本地 Python 或文件权限 | 输出待复制的简读与笔记，走普通聊天路线 |
| Zotero 连接被拒绝 | 确认 Zotero 已启动、接口可用且执行环境位于正确机器 |
| 编号冲突或重复 DOI | 查看现有文件、Zotero 和任务账本，先解决重复关系 |
| 导入超时或结果不明 | 查看 manifest 与 Zotero；不盲目重复导入 |
| 希望每天定时运行 | 另用宿主提供的调度能力，明确时区和时间；提示词本身不是调度器 |

## 本地执行启动请求

```text
请使用本仓库的通用论文工作流提示词执行本次任务。
私人配置：config.local.json。
先确认可用的联网、PDF读取、本地文件、Python和Zotero能力，再完成已授权的操作。
按研究方向选一篇高价值论文，只下载正文，先查重并沿用已有编号。
阅读后准备paper JSON，运行prepare，检查Word，再预览并导入Zotero。
核实每项结果；不足的能力如实报告，不把待执行内容说成已完成。
```
