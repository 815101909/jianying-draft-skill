# 剪映草稿助手 Skill

让 AI 帮你分析、生成和修改剪映草稿，编排口播字幕与画面包装，并检查素材和时间线。

适合需要反复处理字幕样式、参考工程、草稿生成和批量检查的创作者与开发者。内含 Skill 指令、样式规则库，以及可单独运行的 Python 工具。

> 当前已用合成素材验证基础草稿生成与 FFmpeg 渲染流程；生成草稿在剪映客户端中的打开、保存和导出兼容性仍待验证。FFmpeg 渲染支持的效果范围见下文。

## 可以用它做什么

| 需求 | 提供的能力 |
| --- | --- |
| 看懂一个草稿 | 解析轨道、素材引用、文字样式和时间线，执行结构检查 |
| 修改字幕与包装 | 指导 AI 按文稿语义选择字幕、强调字、字体、动画与音效组合 |
| 复用参考工程 | 提取文字样式，分析音效与动画的搭配，整理可复用规则 |
| 程序化生成草稿 | 从 JSON spec 生成视频、图片、独立音轨和文字的基础草稿，可复制素材 |
| 检查与批量处理 | 盘点草稿库、检查素材与媒体流、识别时间线空档、输出检查报告 |
| 渲染基础视频 | 使用 FFmpeg 将支持的草稿内容渲染为 MP4，并输出能力限制报告 |

另附映映小助手特定加密格式的读写工具，仅适用于参考文档中记录的格式。

## 安装到 Codex

1. 下载此仓库的 ZIP 并解压。
2. 将包含 `SKILL.md`、`agents/`、`scripts/` 和 `references/` 的目录放到 `~/.codex/skills/jianying-draft/`。
3. 在 Codex 中开启新对话，使用 `$jianying-draft` 调用。

Windows 的默认安装位置为：

```text
C:\Users\你的用户名\.codex\skills\jianying-draft\
├── SKILL.md
├── agents/
├── references/
└── scripts/
```

仓库名为 `jianying-draft-skill`，Skill 调用名保留为 `jianying-draft`，与指令和脚本示例一致。安装后可显式调用，也支持 Codex 按任务自动选择。

## 直接这样问

把示例中的路径替换成自己的文件位置。

**检查现有草稿**

```text
使用 $jianying-draft 检查 C:/drafts/example。
列出结构问题、缺失素材和时间线空档，给出修复建议。
```

**为口播编排字幕**

```text
使用 $jianying-draft，为 C:/drafts/talking-head 的现有字幕做商业口播包装。
根据文稿语义安排关键词强调和大字标题，保持日常字幕清晰，控制动画和音效密度。
输出到新草稿目录。
```

**从配置生成基础草稿**

```text
使用 $jianying-draft，根据 C:/inputs/spec.json 生成基础草稿。
将素材复制到输出目录，检查生成结果，并报告剪映客户端尚未验证的部分。
```

**渲染可支持的内容**

```text
使用 $jianying-draft，预检 C:/drafts/example 的媒体流。
尝试用严格模式渲染为 C:/outputs/example.mp4；如果遇到未支持的效果，报告原因。
```

## 环境依赖

| 使用方式 | 需要准备 |
| --- | --- |
| 阅读规则、让 AI 分析结构或规划包装 | Codex 和本 Skill；具体操作需要相应草稿与素材 |
| 明文草稿检查与基础生成 | Python；相关工具使用标准库 |
| 检查媒体流、渲染视频 | `ffprobe`、`ffmpeg`，并加入 PATH；文字渲染需要 subtitles/libass 支持 |
| 读取已记录格式的加密草稿 | 检查器需要 Go；渲染器优先使用 Python `cryptography`，缺少时回退到 Go |
| 生成加密草稿 | Python `cryptography` |

以下命令使用 Windows 的 `py` 启动器；其他环境可替换为实际可用的 Python 命令。脚本整体的跨平台兼容性仍需在目标环境确认。

## 单独运行工具

这些工具也可以在终端中使用。以下命令从安装后的 Skill 根目录执行。

```powershell
Set-Location "$env:USERPROFILE/.codex/skills/jianying-draft"

# 检查已有草稿结构
py scripts/inspect_draft.py C:/drafts/example --pretty

# 根据 spec 生成草稿并复制素材，输出目录必须尚不存在
py scripts/make_draft.py C:/inputs/spec.json --out C:/outputs/new-draft --copy-media

# 检查媒体流
py scripts/draft2ffmpeg.py C:/drafts/example --probe

# 严格模式渲染并写出报告
py scripts/draft2ffmpeg.py C:/drafts/example --render --out C:/outputs/example.mp4 --strict
```

最小 `spec.json` 示例：

```json
{
  "name": "示例草稿",
  "canvas": [1080, 1920],
  "fps": 30,
  "ratio": "9:16",
  "clips": [
    {
      "kind": "video",
      "path": "C:/media/demo.mp4",
      "src_start": 0,
      "src_dur": 5,
      "tgt_start": 0,
      "tgt_dur": 5
    },
    {
      "kind": "text",
      "text": "这是一个示例",
      "tgt_start": 0,
      "tgt_dur": 5,
      "size": 8,
      "color": "#FFFFFF"
    }
  ]
}
```

确保示例视频存在且至少有 5 秒可用内容。spec 中的时间以秒为单位；视频源声音如需保留，请显式添加独立音轨。更多字段、批量命令和报告说明见 [生成与渲染参考](references/headless-render-and-generation.md)。

## 能力边界

**草稿编排与视频渲染是两个不同的环节。** Skill 提供的包装规则可以指导 AI 写入草稿结构，但具体效果仍依赖目标剪映版本、资源是否可用，以及实际客户端验收。

FFmpeg 渲染器当前的范围：

| 内容 | 支持情况 |
| --- | --- |
| 基础视频、图片、独立音轨、单样式字幕 | 已用合成素材完成实际渲染测试 |
| 固定缩放、位移、透明度、变速及音频混合 | 已实现，具体输入仍需检查和预览 |
| 关键帧动画、原生动画、蒙版、特效、转场、调色 | 尚未实现 |
| 曲线变速 | 按平均速度近似 |
| 多样式文字 | 当前只读取首个样式，不能完整还原分段样式 |

- 字体、花字、动画和音效规则库不附带对应媒体资源；使用时需要本地可用且有权使用的素材。
- `composition_engine` 是供 AI 使用的编排规则，不是独立执行程序。
- `--strict` 会阻止当前检测器能识别的缺失素材、无效媒体和未支持能力，不能保证与剪映逐帧一致。
- 使用 `--copy-media` 后移动草稿包，仍可能需要按新位置重写素材绝对路径。
- 草稿结构检查通过，不代表视觉效果或剪映客户端兼容性已经通过验收。

## 目录与参考

| 位置 | 内容 |
| --- | --- |
| [SKILL.md](SKILL.md) | Skill 入口、执行流程与资源索引 |
| `agents/openai.yaml` | Codex 展示信息与调用配置 |
| `scripts/` | 草稿检查、生成、基础渲染、样式提取及测试工具 |
| `references/` | 草稿结构、字幕包装、样式规则与项目实现参考 |

## 维护检查

```powershell
py scripts/validate_skill_resources.py
py -m unittest discover -s scripts -p 'test_*.py'
```

测试使用临时合成素材。加密集成测试依赖 Go 与 `cryptography`，真实渲染测试依赖 FFmpeg 与 ffprobe；请检查输出中的跳过项。
