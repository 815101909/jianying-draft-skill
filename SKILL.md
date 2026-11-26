---
name: jianying-draft
description: "生成、分析、修改、修复和检查剪映专业版草稿；解密映映小助手格式；将基础草稿通过 FFmpeg 渲染为视频。适用于剪映草稿 JSON、字幕包装、参考工程样式提取、程序化草稿生成和批量基础渲染。"
---

# 剪映草稿

处理剪映草稿结构、参考工程和字幕包装，并使用配套脚本完成基础草稿生成、检查与 FFmpeg 渲染。

## 按任务加载资源

只加载与当前任务相关的参考，不要一次读取整个样式库。

| 任务 | 资源 |
| --- | --- |
| 草稿结构、素材引用、效果编号 | `references/draft-json-structure-and-catalog.md`；大目录按名称或章节搜索 |
| 修改时间线、字幕、效果、转场或复合片段 | `references/draft-editing-and-packaging.md` |
| 映映小助手加密草稿 | `references/jiangying-encrypted-json.md` |
| spec 生成草稿、基础渲染、批量导出 | `references/headless-render-and-generation.md` |
| 知识付费、创始人 IP、商业口播字幕 | `references/knowledge-payment-subtitle-presets.json` |
| 多行业口播风格 | `references/talking-head-industry-style-system.json` |
| 字体、花字、文字形状选择 | `references/talking-head-font-flower-system.json` |
| 动画与音效搭配、密度和混音 | `references/talking-head-sound-motion-system.json` |
| 查找某个音效的工程证据 | 定向搜索 `references/talking-head-sound-scene-catalog.json` |
| 一创、高包装、人物故事、综艺或生活方式包装 | `references/original-edit-packaging-system.json` |
| 倒计时视频项目实现 | `references/project-implementation.md` |
| 小说视频项目实现 | `references/aigc-factory-implementation.md` |

## 执行流程

1. 确定输入是已有草稿、草稿库、JSON spec 还是文稿与素材。只询问实际阻塞执行的缺失信息。
2. 修改已有草稿时使用副本；解密默认只读，不覆盖源文件。解密器只支持已记录的映映格式。
3. 读取对应参考并执行制作或分析。字幕包装请求默认按语义选风格、组合字幕、字体及合理音效；用户明确要求简洁时使用简洁字幕。
4. 写草稿时遵守主素材与附加素材引用、唯一运行时 ID、微秒时间和文本内嵌 JSON 规则。完整细节见编辑参考。
5. 对交付草稿运行检查器；渲染交付优先使用严格模式，并审阅 JSON 报告。
6. 报告输出文件、实际实现的能力、检查结果及未验证项。

JSON 风格库是决策规则和蓝图，`composition_engine` 不是独立渲染程序。写入草稿前解析 `$ref`、替换占位符并生成运行时 ID。原生动画、花字和字体需要可用资源；缺失时按参考使用替代样式，避免附加失效资源。

## 配套命令

以下 PowerShell 示例假设技能安装在用户默认目录。先把输入和输出变量改成当前任务的路径；调用时不把方括号选项当作命令的一部分。

```powershell
$skillRoot = Join-Path $env:USERPROFILE '.codex/skills/jianying-draft'
$draftPath = 'C:/drafts/example'
$specPath = 'C:/inputs/spec.json'
$outputDraftPath = 'C:/outputs/new-draft'
$outputVideoPath = 'C:/outputs/video.mp4'

# 检查已有草稿
py "$skillRoot/scripts/inspect_draft.py" $draftPath --pretty

# 从 spec 生成草稿及元信息，并复制素材
py "$skillRoot/scripts/make_draft.py" $specPath --out $outputDraftPath --copy-media --name '示例草稿'

# 检查媒体流；严格模式渲染
py "$skillRoot/scripts/draft2ffmpeg.py" $draftPath --probe
py "$skillRoot/scripts/draft2ffmpeg.py" $draftPath --render --out $outputVideoPath --strict
```

批量样式提取使用 `scripts/extract_text_style_catalog.py`，音效/动画共现提取使用 `scripts/extract_sound_motion_pairs.py`；先运行 `--help` 确认参数。批量盘点和渲染使用 `scripts/scan_drafts.py`、`scripts/batch_export.py`，详细命令见渲染参考。

## 依赖与验证范围

- 普通草稿检查和明文生成使用 Python 标准库；Windows 优先使用 `py` 或已确认可用的 Python 路径。
- 检查器读取映映加密草稿需要 Go。渲染器可优先使用 Python `cryptography` 解密，缺少时回退到 Go；生成加密草稿需要 `cryptography`。
- 渲染需要 FFmpeg，媒体流预检需要 ffprobe；文字渲染需要 FFmpeg 的 subtitles/libass 支持。
- 检查器退出码 `0` 表示已实现的结构检查通过，`2` 表示验证问题，`1` 表示读取、解密或运行失败。检查器不验证视觉效果。
- 基础视频、图片、独立音轨和单样式字幕已通过合成素材实际渲染测试。严格模式只拦截当前检测器能识别的问题，不能证明与剪映逐帧一致。
- 关键帧、原生动画、蒙版、特效、转场、调色和多样式文字等渲染限制见能力矩阵。不要把 FFmpeg 的基础渲染称为剪映原生导出。
- 生成草稿在剪映客户端打开、保存和导出的兼容性仍未验证。只有在目标版本完成原生验收后，才能更新这一结论。

## 维护检查

```powershell
py "$skillRoot/scripts/validate_skill_resources.py"
py -m unittest discover -s "$skillRoot/scripts" -p 'test_*.py'
```

维护检查使用临时合成素材，不编辑用户工程。加密集成测试需要 Go 和 `cryptography`；真实渲染测试需要 FFmpeg 和 ffprobe。检查输出中的跳过项，不把跳过测试当作通过。

## 交付说明

提供生成或修改文件的路径，说明草稿检查和渲染是否通过，并列出缺失素材、未还原能力和客户端未验证项。需要视觉验收时，检查代表性字幕、画面和音频；只有实际预览或导出过的结果才能标为已验证成片。
