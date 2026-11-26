# Headless Render & Programmatic Generation

两个方向：

1. **草稿 → 成片**（`scripts/draft2ffmpeg.py`）：不启动剪映，直接把 `draft_content.json` 渲染成 mp4。
2. **脚本 → 草稿**（`scripts/make_draft.py`）：从 JSON spec 生成基础结构草稿，可选加密；客户端兼容性仍待验证。

以下命令从技能根目录运行，路径为示例，执行前替换为实际路径。`--encrypt` 是生成器的可选开关；`--name-contains` 是批量筛选的可选参数。

两者可组成基础流程：`spec → 草稿 → 渲染`，无需打开剪映客户端。

> 这条链路是**只读消费**草稿结构：它解析并复现时间轴，不改动原草稿。它也不做付费/VIP 能力绕过——VIP 素材若在本地磁盘上存在，按普通素材处理；不存在就报 MISSING。

## 依赖

| 用途 | 依赖 |
| --- | --- |
| 渲染 | `ffmpeg`（含 `libx264`、`aac`、`subtitles`/`libass` 滤镜）在 PATH |
| 明文草稿解析 | 仅标准库 |
| 映映加密草稿解析 | Python 包 `cryptography`（首选），否则回退到 `scripts/decrypt_yingying_json.go`（需 `go`） |
| 生成加密草稿（`--encrypt`） | Python 包 `cryptography` |

## 渲染器：`scripts/draft2ffmpeg.py`

```powershell
# 时间轴总览（含空档统计）
py scripts/draft2ffmpeg.py --info "C:/drafts/example"
# 素材存在性检查
py scripts/draft2ffmpeg.py --probe "C:/drafts/example" --report probe.json
# 只打印 ffmpeg 命令，不执行
py scripts/draft2ffmpeg.py --dry-run "C:/drafts/example" --out out.mp4
# 实际渲染
py scripts/draft2ffmpeg.py --render "C:/drafts/example" --out "C:/outputs/out.mp4" --fit contain --crf 20 --preset medium --text-scale 1.0
```

长草稿 / 异常时间轴：

```powershell
# 只渲染 0~30s 窗口
py scripts/draft2ffmpeg.py --render "C:/drafts/example" --out out.mp4 --range 0:30
# 压缩 >SEC 秒的空档（0 = 全部消除）
py scripts/draft2ffmpeg.py --render "C:/drafts/example" --out out.mp4 --collapse-gaps 0
# 解密镜像（只含 JSON）+ 原始媒体目录
py scripts/draft2ffmpeg.py --render "C:/drafts/decrypted-example" --media-root "C:/drafts/original-example" --out out.mp4
```

能力矩阵：

| 能力 | 状态 | 实现要点 |
| --- | --- | --- |
| 明文/加密草稿自动识别 | ✅ | 首字节判断，加密走 `jy_draft_crypt` / Go |
| 画布 / fps | ✅ | `canvas_config` + `fps`（null → 30）；宽高向上对齐偶数 |
| 视频轨 | ✅ | `trim` → `setpts`(变速) → `scale` → `overlay` |
| 图片轨 | ✅ | `-loop 1 -t D -i`（注意：占 6 个 argv token，流序号要独立计数） |
| 变速 | ✅ | `speeds` 素材；视频 `setpts`、音频 `atempo` |
| 画中画/副轨（`flag=2`） | ✅ | 按 `track_index` 排序后逐层 `overlay` |
| 缩放 / 位移 / 透明度 | ✅ | `scale=iw*sx`、`overlay` 偏移、`colorchannelmixer=aa` |
| 文字 → ASS | ✅ | 解析 `content` 内嵌 JSON，`\pos`/`\fs`/`\1c`/`\3c`/`\bord` |
| 音频混合 | ✅ | `atrim`/`asetpts`/`volume`/`adelay` + `amix=normalize=0` |
| 复合片段展开 | ✅ | `extra_material_refs` → `materials.drafts[].draft` 递归 |
| 时间轴空档检测/折叠 | ✅ | `analyze_gaps` / `--collapse-gaps` |
| 时间窗口裁剪 | ✅ | `--range START:DUR` |
| 备用素材根目录 | ✅ | `--media-root DIR`（可多次） |
| 关键帧动画 | ❌ 未实现 | 缺真实样例（多数草稿 `keyframes` 为空） |
| 曲线变速 | ⚠️ 近似 | 按平均速度处理，未做曲线积分 |
| 蒙版/特效/转场/调色/`material_animations` | ❌ 未实现 | 目前忽略 |

## 生成器：`scripts/make_draft.py`

### 交付与失败处理

- `--probe` 使用 `ffprobe` 检查媒体流和有效视频尺寸；缺失或无效媒体返回非零退出码。它不是完整的逐帧解码检测。
- `--render` 默认预检媒体流，并写入 `<输出.mp4>.render-report.json`；`--report PATH` 可指定报告位置。
- `--strict` 在缺失素材、无效素材或检测到未实现能力时停止。未使用 strict 时，缺失片段可以跳过，报告标记 `rendered_with_limitations`。报告仅覆盖当前检测器能识别的能力，不能证明与剪映逐帧一致。
- 默认不覆盖已有 MP4；确需覆盖时使用 `--overwrite`。
- 字幕 ASS 文件按输出文件名隔离，避免批量并发相互覆盖。

```powershell
py scripts/draft2ffmpeg.py --render "C:/drafts/example" --out out.mp4 --strict --report render-report.json
```

```powershell
py scripts/make_draft.py "C:/inputs/spec.json" --out "C:/outputs/new-draft" --name MyDraft --copy-media
```

`spec.json`：

```json
{
  "name": "my-draft", "canvas": [1920, 1080], "fps": 30, "ratio": "16:9",
  "clips": [
    {"kind": "video", "path": "D:/a.mp4", "src_start": 0, "src_dur": 5,
     "tgt_start": 0, "tgt_dur": 5, "speed": 1.0, "volume": 1.0,
     "scale": [1, 1], "transform": [0, 0]},
    {"kind": "image", "path": "D:/p.jpg", "tgt_start": 5, "tgt_dur": 3, "scale": [0.6, 0.6]},
    {"kind": "audio", "path": "D:/m.mp3", "src_start": 0, "src_dur": 8, "tgt_start": 0, "volume": 0.6},
    {"kind": "text", "text": "Hello", "tgt_start": 1, "tgt_dur": 3,
     "transform": [0, 0.7], "size": 8, "color": "#FFE24D"}
  ]
}
```

字段说明：

| 字段 | 含义 |
| --- | --- |
| `kind` | `video` / `image` / `audio` / `text` |
| `src_start` / `src_dur` | 源内截取区间（秒）；`image` 忽略 |
| `tgt_start` / `tgt_dur` | 时间轴上的位置与时长（秒）；`tgt_dur` 缺省取 `src_dur` |
| `speed` | 变速倍率（>1 加速）；写入 `materials.speeds` |
| `scale` / `transform` | `clip.scale` / `clip.transform`；`transform.y` 向上为正 |
| `volume` | 音量（0~1+） |
| `size` / `color` / `stroke` | 文字字号（剪映字号）/ 填充色 / 描边色 |

输出包含 `draft_content.json`、`draft_meta_info.json` 和 `manifest.json`。相对素材路径按 spec 所在目录解析，生成前检查文件存在性。`--copy-media` 将素材复制到 `Resources/local` 并重写路径；默认保留素材绝对路径。已有草稿目录会被拒绝，避免覆盖原工程。

文字填充色写入内嵌 `content.styles`。图片、视频、独立音轨和文字可交给 `draft2ffmpeg.py` 做基础渲染。视频源声音请显式添加为独立音轨。

生成器依据已观察的草稿结构构建基础项目，没有公开官方 schema 一致性认证。当前没有完成本机剪映打开/保存验收；`manifest.json` 显式记录 `jianying_open_verified: false`。封面未生成也未被引用；原生编辑兼容性须针对实际剪映版本验收。搬移草稿包后，需要按新位置重写素材绝对路径。

## 结构映射要点（渲染必须知道）

这些是实测得到的、写渲染/生成代码时最容易踩的点：

- **时间单位**：草稿内部一律**微秒**（`1e6 = 1s`）。例外：文字 `content.words.*_time` 是**毫秒**。
- **坐标**：`clip.transform.y` **向上为正**；转屏幕坐标 `y_screen = (1 - y) / 2 * H`。
- **变速不在 segment 里**：`segment.source_timerange.duration` 与 `target_timerange.duration` 常常相等，真实速度在 `materials.speeds[i]` 的 `{speed, curve_speed, mode}`，通过 `extra_material_refs` 关联。部分顶层 `speeds` 只有 `{id,type}`。
- **`extra_material_refs` 是跨分组 ID 列表**：可同时指向 `speeds`、`material_animations`、`transitions`、`masks`、`drafts` 等 20+ 分组。必须先建全局 `id → (group, item)` 索引再解析。
- **复合片段**：`segment.extra_material_refs` → `materials.drafts[i]`（`type: "combination"`），其 `.draft` 字段是内嵌子草稿（含自己的 `tracks`/`materials`）。`combination_id` **不等于**磁盘 `subdraft/<id>/` 目录名。子草稿内 `##_draftpath_placeholder_<GUID>_##` 仍指向同一草稿根。
- **文字**：`materials.texts[i].content` 是**字符串套 JSON**，结构 `{"styles":[...], "text":"..."}`。多 `style` = 多色分段。`font_size` 是剪映字号，`text_size` 是像素近似。
- **图片输入 argv**：`-loop 1 -t D -i path` 是 **6 个 token**，推流序号不能用 `len(argv)//2`。
- **奇数画布**：libx264 要求宽高偶数，`1920×1447` 会渲染 0 字节，需向上对齐。
- **空档**：草稿可能存在巨量空档（实测 1 处 14429s），输出会超长，需 `--range` 或 `--collapse-gaps`。

## 批量工具

```powershell
# 盘点草稿库：解密 + 解析 + 素材可用性 + 空档
py scripts/scan_drafts.py "C:/drafts/library" --json scan.json

# 批量导出（默认只导素材齐全的）
py scripts/batch_export.py "C:/drafts/library" --out-dir "C:/outputs/batch" `
   --only-complete --min-dur 5 --max-dur 60 --jobs 3 --range 0:30
```

`scan_drafts.py` 的 `status` 取值：`OK` / `DECRYPT_FAIL` / `PARSE_FAIL`。`media_ok` / `media_missing` 统计素材可用性；`media_missing > 0` 时仍可导出，缺失片段会被跳过并告警。

批量导出文件名附加源目录标识，隔离同名工程。支持 `--strict`、`--overwrite` 和可重复的 `--media-root`。`--only-complete` 表示预扫描时文件存在，实际渲染还会做媒体流检查。`_batch_report.json` 包含 `results`、`parse_failures` 和未选中数量；任何解析失败或导出失败都会返回退出码 `2`，正常完成或 dry-run 返回 `0`。

## 回归验证

```powershell
py -m unittest discover -s scripts -p "test_*.py"
py scripts/validate_skill_resources.py
```

有 `ffmpeg` 和 `ffprobe` 时，交付测试会生成临时视频、图片和音频，从 spec 生成带素材的草稿，通过检查后实际渲染，并检查视频/音频流、时长、画面切换、字幕颜色、非静音音频与损坏素材识别。所有素材使用临时合成内容，不依赖第三方样例。

## 已知限制（未实现，不要假装支持）

1. **关键帧动画**（`common_keyframes` / `KFTypeScaleX` 等）—— 未实现。
2. **曲线变速** —— 按平均速度近似。
3. **蒙版 / 特效 / 转场 / 调色 / `material_animations`** —— 忽略。
4. **多 style 文字** —— 目前只取 `styles[0]`，多色分段需拆成多段 ASS。
5. **损坏素材** —— 存在 0×0 无效图片，渲染前建议 `--probe` 预筛。

需要精确还原上述能力时，先补样例草稿，再在 `draft2ffmpeg.py` 中扩展对应 filter，不要用近似冒充精确。
