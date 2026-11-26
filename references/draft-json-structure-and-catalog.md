# 剪映效果草稿 JSON 结构实例

更新时间：2026-04-03

用途：这份文档只看“效果最终写进剪映草稿 JSON 后长什么样”。
不讲代码实现，只整理草稿里的结构实例。

---

## 0. 最小草稿骨架

如果你先想知道这些东西大概都挂在哪，最小骨架可以先记成下面这样：

```jsonc
{
  "materials": {
    "texts": [],
    "effects": [],
    "material_animations": [],
    "video_effects": [],
    "audio_effects": [],
    "audio_fades": [],
    "speeds": [],
    "audios": [],
    "videos": []
  },
  "tracks": [
    {
      "id": "video_track_001",
      "name": "main_track",
      "type": "video",
      "segments": []
    },
    {
      "id": "text_track_001",
      "name": "subtitle_track",
      "type": "text",
      "segments": []
    },
    {
      "id": "effect_track_001",
      "name": "effect_track",
      "type": "effect",
      "segments": []
    },
    {
      "id": "filter_track_001",
      "name": "filter_track",
      "type": "filter",
      "segments": []
    },
    {
      "id": "audio_track_001",
      "name": "audio_track",
      "type": "audio",
      "segments": []
    }
  ]
}
```

最常看的几组：

- 字幕样式：`materials.texts`
- 花字 / 文字气泡 / 滤镜：`materials.effects`
- 字幕动画：`materials.material_animations`
- 视频特效 / 人物特效：`materials.video_effects`
- 音效：`materials.audio_effects`

---

## 先记 3 个核心规则

### 1. 主素材引用

大多数片段都先通过 `material_id` 指向主素材：

```jsonc
{
  "id": "segment_xxx",
  "material_id": "material_xxx"
}
```

常见对应关系：

- 字幕片段 `material_id -> materials.texts[*].id`
- 滤镜轨片段 `material_id -> materials.effects[*].id`
- 特效轨片段 `material_id -> materials.video_effects[*].id`
- 音频片段 `material_id -> materials.audios[*].id`

### 2. 附加效果引用

动画、花字、文字气泡、音效、滤镜、视频特效，很多时候不是走 `material_id`，而是走：

```jsonc
{
  "extra_material_refs": [
    "speed_xxx",
    "effect_xxx",
    "animation_xxx"
  ]
}
```

常见对应关系：

- `extra_material_refs -> materials.material_animations[*].id`
- `extra_material_refs -> materials.effects[*].id`
- `extra_material_refs -> materials.video_effects[*].id`
- `extra_material_refs -> materials.audio_effects[*].id`
- `extra_material_refs -> materials.audio_fades[*].id`
- `extra_material_refs -> materials.speeds[*].id`

### 3. 字幕样式不在外层字段里，而在 `content` 字符串里

`materials.texts[*].content` 在草稿里不是对象，而是一段 JSON 字符串：

```jsonc
{
  "id": "text_material_001",
  "content": "{\"styles\":[...],\"text\":\"这是字幕正文\"}"
}
```

所以看字幕样式时，一定要把 `content` 再解一层。

---

## 一、字幕能力：完整草稿实例

这一组是“字幕 + 描边 + 阴影 + 花字 + 文字气泡 + 动画”的完整链路。

### 1. 文本轨上的 segment

```jsonc
{
  "id": "segment_text_001",
  "material_id": "text_material_001",
  "target_timerange": {
    "start": 0,
    "duration": 3000000
  },
  "source_timerange": null,
  "speed": 1.0,
  "volume": 1.0,
  "extra_material_refs": [
    "speed_001",
    "text_anim_pack_001",
    "text_shape_001",
    "text_effect_001"
  ],
  "is_tone_modify": false,
  "clip": {
    "alpha": 1.0,
    "flip": {
      "horizontal": false,
      "vertical": false
    },
    "rotation": 0.0,
    "scale": {
      "x": 1.0,
      "y": 1.0
    },
    "transform": {
      "x": 0.0,
      "y": -0.2
    }
  },
  "uniform_scale": {
    "on": true,
    "value": 1.0
  },
  "render_index": 15000,
  "common_keyframes": [],
  "keyframe_refs": []
}
```

这条片段的意思是：

- `material_id` 指向字幕正文
- `extra_material_refs` 里挂速度、动画包、文字气泡、花字

### 2. `materials.texts[*]` 外层结构

这是草稿里真正写进去的外层文本素材：

```jsonc
{
  "id": "text_material_001",
  "content": "{\"styles\":[{\"fill\":{\"alpha\":1.0,\"content\":{\"render_type\":\"solid\",\"solid\":{\"alpha\":1.0,\"color\":[1.0,1.0,1.0]}}},\"range\":[0,12],\"size\":15,\"bold\":false,\"italic\":false,\"underline\":false,\"strokes\":[{\"content\":{\"solid\":{\"alpha\":1.0,\"color\":[0.0,0.0,0.0]}},\"width\":0.08}],\"shadows\":[{\"diffuse\":0.025,\"alpha\":0.9,\"distance\":5.0,\"content\":{\"solid\":{\"color\":[0.0,0.0,0.0]}},\"angle\":-45.0}],\"effectStyle\":{\"id\":\"7539407429763796249\",\"path\":\"<effect-resource-path>\"},\"font\":{\"id\":\"font_resource_001\",\"path\":\"<font-resource-path>\"}}],\"text\":\"这是字幕正文\"}",
  "typesetting": 0,
  "alignment": 1,
  "letter_spacing": 0.0,
  "line_spacing": 0.02,
  "line_feed": 1,
  "line_max_width": 0.82,
  "force_apply_line_max_width": false,
  "check_flag": 47,
  "type": "subtitle",
  "global_alpha": 1.0
}
```

几个重点：

- `type` 可能是 `subtitle`，也可能是 `text`
- `check_flag: 47` 常见于带描边和阴影的字幕
- 真正的颜色、描边、阴影、花字入口都在 `content` 字符串里

### 3. `content` 解开之后的可读结构

为了方便肉眼看，通常会把上面的 `content` 还原成下面这样：

```jsonc
{
  "text": "这是字幕正文",
  "styles": [
    {
      "fill": {
        "alpha": 1.0,
        "content": {
          "render_type": "solid",
          "solid": {
            "alpha": 1.0,
            "color": [1.0, 1.0, 1.0]
          }
        }
      },
      "range": [0, 12],
      "size": 15,
      "bold": false,
      "italic": false,
      "underline": false,
      "font": {
        "id": "font_resource_001",
        "path": "D:"
      },
      "strokes": [
        {
          "content": {
            "solid": {
              "alpha": 1.0,
              "color": [0.0, 0.0, 0.0]
            }
          },
          "width": 0.08
        }
      ],
      "shadows": [
        {
          "diffuse": 0.025,
          "alpha": 0.9,
          "distance": 5.0,
          "angle": -45.0,
          "content": {
            "solid": {
              "color": [0.0, 0.0, 0.0]
            }
          }
        }
      ],
      "effectStyle": {
        "id": "7539407429763796249",
        "path": "C:"
      }
    }
  ]
}
```

看字幕样式时，重点盯这几个字段：

- `fill`：文字颜色
- `size`：字号
- `font`：字体
- `strokes`：描边
- `shadows`：阴影
- `effectStyle`：花字入口
- `range`：这段样式作用在哪个文字范围

### 4. 局部高亮样式的结构

如果一句字幕里只有某几个词高亮，还是继续加在 `styles` 里，不会单独多一条素材：

```jsonc
{
  "text": "五个快乐到死的顶级思维",
  "styles": [
    {
      "range": [0, 2],
      "size": 12,
      "fill": {
        "content": {
          "solid": {
            "color": [1.0, 1.0, 1.0]
          }
        }
      }
    },
    {
      "range": [2, 4],
      "size": 15,
      "fill": {
        "content": {
          "solid": {
            "color": [1.0, 0.4431372549, 0.0]
          }
        }
      },
      "strokes": [
        {
          "content": {
            "solid": {
              "alpha": 1.0,
              "color": [0.0, 0.0, 0.0]
            }
          },
          "width": 0.08
        }
      ],
      "useLetterColor": true
    }
  ]
}
```

### 5. 花字在 `materials.effects`

花字素材本体不在 `materials.texts`，而在 `materials.effects`：

```jsonc
{
  "apply_target_type": 0,
  "effect_id": "7539407429763796249",
  "id": "text_effect_001",
  "resource_id": "7539407429763796249",
  "type": "text_effect",
  "value": 1.0,
  "source_platform": 1
}
```

字段识别要点：

- `type == "text_effect"`
- `id` 给 `extra_material_refs` 引用
- `effect_id` / `resource_id` 给字幕 `content.styles[*].effectStyle.id` 对应

### 6. 文字气泡在 `materials.effects`

文字气泡和花字一样，也放在 `materials.effects`，只是 `type` 不一样：

```jsonc
{
  "apply_target_type": 0,
  "effect_id": "7412345678901234567",
  "id": "text_shape_001",
  "resource_id": "7412345678901234567",
  "type": "text_shape",
  "value": 1.0
}
```

字段识别要点：

- `type == "text_shape"`
- 文本 segment 的 `extra_material_refs` 会引用它
- 这种结构更像“文字气泡 / 文本底板 / 文字造型”

### 7. 字幕动画包在 `materials.material_animations`

字幕动画不是放在 `materials.effects`，而是单独放在 `materials.material_animations`：

```jsonc
{
  "id": "text_anim_pack_001",
  "type": "sticker_animation",
  "multi_language_current": "none",
  "animations": [
    {
      "anim_adjust_params": null,
      "platform": "all",
      "panel": "",
      "material_type": "sticker",
      "name": "变色输入",
      "id": "77035159",
      "type": "in",
      "resource_id": "7397306443147252233",
      "start": 0,
      "duration": 800000
    },
    {
      "anim_adjust_params": null,
      "platform": "all",
      "panel": "",
      "material_type": "sticker",
      "name": "渐隐",
      "id": "1644600",
      "type": "out",
      "resource_id": "6724919382104871427",
      "start": 2200000,
      "duration": 800000
    },
    {
      "anim_adjust_params": null,
      "platform": "all",
      "panel": "",
      "material_type": "sticker",
      "name": "抖动循环",
      "id": "27000001",
      "type": "loop",
      "resource_id": "7397306443147000001",
      "start": 800000,
      "duration": 1400000
    }
  ]
}
```

字段识别要点：

- `type == "sticker_animation"`
- 每个动画项的 `type` 可能是 `in` / `out` / `loop`
- 文本片段通过 `extra_material_refs` 引用整个动画包的 `id`

### 8. 这一整组的引用关系

```text
tracks.text.segments[0].material_id
  -> materials.texts[0].id = text_material_001

tracks.text.segments[0].extra_material_refs
  -> materials.speeds[*].id = speed_001
  -> materials.material_animations[*].id = text_anim_pack_001
  -> materials.effects[*].id = text_shape_001
  -> materials.effects[*].id = text_effect_001

materials.texts[0].content.styles[0].effectStyle.id
  -> materials.effects[type=text_effect].effect_id
```

---

## 二、滤镜：两种常见草稿写法

滤镜在草稿里常见有两种挂法：

1. 挂在视频片段的 `extra_material_refs`
2. 放在独立的 `filter` 轨道上

### 1. 写法 A：挂在视频 segment 上

#### 视频 segment

```jsonc
{
  "id": "video_segment_001",
  "material_id": "video_material_001",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "source_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "speed": 1.0,
  "volume": 1.0,
  "extra_material_refs": [
    "speed_video_001",
    "filter_material_001"
  ],
  "is_tone_modify": false,
  "render_index": 0,
  "common_keyframes": [],
  "keyframe_refs": []
}
```

#### `materials.effects` 里的滤镜素材

```jsonc
{
  "adjust_params": [],
  "algorithm_artifact_path": "",
  "apply_target_type": 0,
  "bloom_params": null,
  "category_id": "",
  "category_name": "",
  "color_match_info": {
    "source_feature_path": "",
    "target_feature_path": "",
    "target_image_path": ""
  },
  "effect_id": "7127828208690433311",
  "enable_skin_tone_correction": false,
  "exclusion_group": [],
  "face_adjust_params": [],
  "formula_id": "",
  "id": "filter_material_001",
  "intensity_key": "",
  "multi_language_current": "",
  "name": "1980",
  "panel_id": "",
  "platform": "all",
  "resource_id": "7127828208690433311",
  "source_platform": 1,
  "sub_type": "none",
  "time_range": null,
  "type": "filter",
  "value": 0.8,
  "version": ""
}
```

这时的识别方式是：

- `materials.effects[*].type == "filter"`
- 视频片段 `extra_material_refs` 直接引用这个滤镜 `id`

### 2. 写法 B：独立 filter 轨

#### `tracks[*].type == "filter"` 的 segment

```jsonc
{
  "id": "filter_segment_001",
  "material_id": "filter_material_002",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "render_index": 11000,
  "common_keyframes": [],
  "keyframe_refs": []
}
```

#### 对应的滤镜素材

```jsonc
{
  "adjust_params": [],
  "algorithm_artifact_path": "",
  "apply_target_type": 0,
  "bloom_params": null,
  "category_id": "",
  "category_name": "",
  "color_match_info": {
    "source_feature_path": "",
    "target_feature_path": "",
    "target_image_path": ""
  },
  "effect_id": "7391481866407391744",
  "enable_skin_tone_correction": false,
  "exclusion_group": [],
  "face_adjust_params": [],
  "formula_id": "",
  "id": "filter_material_002",
  "intensity_key": "",
  "multi_language_current": "",
  "name": "黑白记忆",
  "panel_id": "",
  "platform": "all",
  "resource_id": "7391481866407391744",
  "source_platform": 1,
  "sub_type": "none",
  "time_range": null,
  "type": "filter",
  "value": 1.0,
  "version": ""
}
```

这时的识别方式是：

- `tracks[*].type == "filter"`
- `segment.material_id -> materials.effects[*].id`

---

## 三、视频特效：两种常见草稿写法

视频特效也常见有两种挂法：

1. 挂在视频片段 `extra_material_refs`
2. 放在独立的 `effect` 轨道上

场景特效和人物特效都在 `materials.video_effects`，只是 `type` 不同。

### 1. 写法 A：挂在视频 segment 上

#### 视频 segment

```jsonc
{
  "id": "video_segment_002",
  "material_id": "video_material_002",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "source_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "speed": 1.0,
  "volume": 1.0,
  "extra_material_refs": [
    "speed_video_002",
    "video_effect_material_001",
    "face_effect_material_001"
  ],
  "is_tone_modify": false,
  "render_index": 0,
  "common_keyframes": [],
  "keyframe_refs": []
}
```

#### `materials.video_effects` 里的场景特效

```jsonc
{
  "adjust_params": [
    {
      "name": "effects_adjust_filter",
      "value": 1.0
    },
    {
      "name": "effects_adjust_texture",
      "value": 1.0
    }
  ],
  "apply_target_type": 0,
  "apply_time_range": null,
  "category_id": "",
  "category_name": "",
  "common_keyframes": [],
  "disable_effect_faces": [],
  "effect_id": "1183068",
  "formula_id": "",
  "id": "video_effect_material_001",
  "name": "1998",
  "platform": "all",
  "render_index": 11000,
  "resource_id": "6981791065204331044",
  "source_platform": 0,
  "time_range": null,
  "track_render_index": 0,
  "type": "video_effect",
  "value": 1.0,
  "version": ""
}
```

#### `materials.video_effects` 里的人物特效

```jsonc
{
  "adjust_params": [
    {
      "name": "effects_adjust_size",
      "value": 0.5
    },
    {
      "name": "effects_adjust_vertical_shift",
      "value": 0.5
    }
  ],
  "apply_target_type": 0,
  "apply_time_range": null,
  "category_id": "",
  "category_name": "",
  "common_keyframes": [],
  "disable_effect_faces": [],
  "effect_id": "1436386",
  "formula_id": "",
  "id": "face_effect_material_001",
  "name": "中刀",
  "platform": "all",
  "render_index": 11000,
  "resource_id": "7029514054179754510",
  "source_platform": 0,
  "time_range": null,
  "track_render_index": 0,
  "type": "face_effect",
  "value": 1.0,
  "version": ""
}
```

这时的识别方式是：

- `materials.video_effects[*].type == "video_effect"` 是场景特效
- `materials.video_effects[*].type == "face_effect"` 是人物特效
- 视频片段 `extra_material_refs` 直接引用特效素材 `id`

### 2. 写法 B：独立 effect 轨

#### `tracks[*].type == "effect"` 的 segment

```jsonc
{
  "id": "effect_segment_001",
  "material_id": "video_effect_material_002",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "render_index": 10000,
  "common_keyframes": [],
  "keyframe_refs": []
}
```

#### 对应的全局特效素材

```jsonc
{
  "adjust_params": [
    {
      "name": "effects_adjust_filter",
      "value": 1.0
    }
  ],
  "apply_target_type": 2,
  "apply_time_range": null,
  "category_id": "",
  "category_name": "",
  "common_keyframes": [],
  "disable_effect_faces": [],
  "effect_id": "1183068",
  "formula_id": "",
  "id": "video_effect_material_002",
  "name": "1998",
  "platform": "all",
  "render_index": 11000,
  "resource_id": "6981791065204331044",
  "source_platform": 0,
  "time_range": null,
  "track_render_index": 0,
  "type": "video_effect",
  "value": 1.0,
  "version": ""
}
```

这时的识别方式是：

- `tracks[*].type == "effect"`
- `segment.material_id -> materials.video_effects[*].id`
- `apply_target_type: 2` 更像“独立特效轨全局作用”

---

## 四、音效：完整草稿实例

音效一般挂在音频片段的 `extra_material_refs` 上。

### 1. 音频 segment

```jsonc
{
  "id": "audio_segment_001",
  "material_id": "audio_material_001",
  "target_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "source_timerange": {
    "start": 0,
    "duration": 5000000
  },
  "speed": 1.0,
  "volume": 1.0,
  "extra_material_refs": [
    "speed_audio_001",
    "audio_fade_001",
    "audio_effect_001"
  ],
  "is_tone_modify": false,
  "clip": null,
  "hdr_settings": null,
  "render_index": 0,
  "common_keyframes": [],
  "keyframe_refs": []
}
```

### 2. `materials.audio_effects` 里的音效实例

```jsonc
{
  "audio_adjust_params": [
    {
      "name": "change_voice_param_quantity",
      "value": 0.8
    },
    {
      "name": "change_voice_param_strength",
      "value": 0.762
    }
  ],
  "category_id": "sound_effect",
  "category_name": "场景音",
  "id": "audio_effect_001",
  "is_ugc": false,
  "name": "回音",
  "production_path": "",
  "resource_id": "7018011608408396325",
  "speaker_id": "",
  "sub_type": 1,
  "time_range": {
    "duration": 0,
    "start": 0
  },
  "type": "audio_effect"
}
```

### 3. `materials.audio_fades` 里的淡入淡出

这个不是“音效包”，但经常也会跟音频效果一起出现：

```jsonc
{
  "id": "audio_fade_001",
  "fade_in_duration": 300000,
  "fade_out_duration": 300000,
  "fade_type": 0,
  "type": "audio_fade"
}
```

这组结构的识别方式是：

- `audio_segment.material_id -> materials.audios[*].id`
- `audio_segment.extra_material_refs -> materials.audio_effects[*].id`
- `audio_segment.extra_material_refs -> materials.audio_fades[*].id`

---

## 五、按草稿反查时，最有用的定位顺序

### 1. 想看字幕样式

先找：

- `tracks[*].type == "text"`

然后顺着：

- `segment.material_id -> materials.texts[*].id`
- 再把 `materials.texts[*].content` 解开

重点字段：

- `styles[*].fill`
- `styles[*].font`
- `styles[*].strokes`
- `styles[*].shadows`
- `styles[*].effectStyle`

### 2. 想看花字和文字气泡

直接找：

- `materials.effects[*].type == "text_effect"`
- `materials.effects[*].type == "text_shape"`

再回头看哪些文本 segment 的 `extra_material_refs` 引用了它们。

### 3. 想看滤镜

两种地方都要看：

- `materials.effects[*].type == "filter"`
- `tracks[*].type == "filter"`

如果视频 segment 的 `extra_material_refs` 里直接挂了滤镜，也能找到。

### 4. 想看视频特效

直接找：

- `materials.video_effects[*].type == "video_effect"`
- `materials.video_effects[*].type == "face_effect"`

然后再看它是被：

- 视频 segment 的 `extra_material_refs` 引用
- 还是 `effect` 轨道 segment 的 `material_id` 引用

### 5. 想看音效

直接找：

- `materials.audio_effects[*].type == "audio_effect"`

再回头看哪个音频 segment 的 `extra_material_refs` 引用了它。

---

## 六、可以直接死记的一张表

| 能力 | 草稿 JSON 主要位置 | 典型 type | 典型引用方式 |
| --- | --- | --- | --- |
| 字幕正文与样式 | `materials.texts` | `subtitle` / `text` | `text segment.material_id` |
| 字幕动画 | `materials.material_animations` | `sticker_animation` | `text segment.extra_material_refs` |
| 花字 | `materials.effects` | `text_effect` | `text segment.extra_material_refs` |
| 文字气泡 / 文字造型 | `materials.effects` | `text_shape` | `text segment.extra_material_refs` |
| 滤镜 | `materials.effects` | `filter` | `video.extra_material_refs` 或 `filter segment.material_id` |
| 视频场景特效 | `materials.video_effects` | `video_effect` | `video.extra_material_refs` 或 `effect segment.material_id` |
| 人物特效 | `materials.video_effects` | `face_effect` | `video.extra_material_refs` 或 `effect segment.material_id` |
| 音效 | `materials.audio_effects` | `audio_effect` | `audio segment.extra_material_refs` |
| 音频淡入淡出 | `materials.audio_fades` | `audio_fade` | `audio segment.extra_material_refs` |

---

## 七、最短结论

如果你只想快速判断一个草稿里“某个效果写在哪”：

1. 先看 `tracks[*].segments[*]`
2. 记住 `material_id` 是主素材
3. 记住 `extra_material_refs` 是附加效果
4. 字幕样式一定去看 `materials.texts[*].content`
5. 花字 / 文字气泡 / 滤镜去看 `materials.effects`
6. 视频特效去看 `materials.video_effects`
7. 音效去看 `materials.audio_effects`

---

## 八、其它固定编号能力

### 1. 字体

字体不是单独放在 materials 某个数组里，而是直接写在字幕内容样式中：

```jsonc
{
  "font": {
    "id": "7246698168547545602",
    "path": "D:"
  }
}
```

要点：

- 草稿真正用的是 `font.id`
- 这个值对应字体元数据里的 `resource_id`
- `effect_id` 在文档附录里也保留，主要是为了对照仓库元数据

### 2. 视频动画

视频动画和字幕动画都挂在 `materials.material_animations`，区别只在动画项内部字段：

```jsonc
{
  "id": "video_anim_pack_001",
  "type": "sticker_animation",
  "multi_language_current": "none",
  "animations": [
    {
      "anim_adjust_params": null,
      "platform": "all",
      "panel": "video",
      "material_type": "video",
      "name": "淡入",
      "id": "1506926",
      "type": "in",
      "resource_id": "7049979667406656014",
      "start": 0,
      "duration": 500000
    }
  ]
}
```

要点：

- 视频片段通过 `extra_material_refs` 引用整个动画包 ID
- 动画项里的 `id` 是 `effect_id`
- 动画项里的 `resource_id` 是资源编号
- 视频动画的 `type` 通常是 `in` / `out` / `group`

### 3. 转场

转场单独放在 `materials.transitions`：

```jsonc
{
  "category_id": "",
  "category_name": "",
  "duration": 500000,
  "effect_id": "2917279",
  "id": "transition_001",
  "is_overlap": true,
  "name": "上移",
  "platform": "all",
  "resource_id": "6724846395116753416",
  "type": "transition"
}
```

要点：

- 通常由前一个视频 segment 的 `extra_material_refs` 引用
- 关键编号还是 `effect_id` 和 `resource_id`

### 4. 蒙版

蒙版单独放在 `materials.masks`：

```jsonc
{
  "config": {
    "aspectRatio": 1.0,
    "centerX": 0.0,
    "centerY": 0.0,
    "feather": 0.0,
    "height": 0.5,
    "invert": false,
    "rotation": 0.0,
    "roundCorner": 0.0,
    "width": 0.5
  },
  "id": "mask_001",
  "name": "圆形",
  "platform": "all",
  "position_info": "",
  "resource_type": "circle",
  "resource_id": "6791700663249146381",
  "type": "mask"
}
```

要点：

- 视频片段通过 `extra_material_refs` 引用蒙版素材 ID
- 蒙版本身还带 `resource_type`，比如 `line` / `circle` / `rectangle`

### 5. 混合模式

混合模式放在 `materials.effects`，但 `type` 是 `mix_mode`：

```jsonc
{
  "type": "mix_mode",
  "name": "正片叠底",
  "effect_id": "871333",
  "resource_id": "6758325895519277582",
  "value": 1.0,
  "apply_target_type": 0,
  "platform": "all",
  "source_platform": 0,
  "category_id": "",
  "category_name": "",
  "sub_type": "none",
  "time_range": null,
  "id": "mix_mode_001"
}
```

要点：

- 视频片段通过 `extra_material_refs` 引用它
- 和滤镜一样在 `materials.effects`，但 `type` 不同


---

## 九、固定编号类与自由参数类

### 1. 这份文档里能做“全量编号目录”的

这些能力在仓库里都有固定清单，所以我已经把它们全部展开成附录：

- 字体
- 花字
- 文字动画
- 视频动画
- 滤镜
- 视频场景特效
- 视频人物特效
- 音频场景音
- 音色
- 声音成曲
- 转场
- 蒙版
- 混合模式

### 2. 这些字段没有“全量编号表”，只能看结构

下面这些不是固定样式库，而是自由参数，所以不存在像滤镜那样的完整编号目录：

- 字幕 `fill` 颜色
- `strokes` 的颜色 / 宽度 / 透明度
- `shadows` 的颜色 / 扩散 / 距离 / 角度
- `size` / `bold` / `italic` / `underline`
- `alignment` / `letter_spacing` / `line_spacing` / `line_max_width`
- 背景相关字段，如 `background_color` / `background_alpha` / `background_round_radius`
- 片段 `clip` 里的缩放、位移、旋转、透明度
- 音量、速度、关键帧等连续值

这些内容前半部分已经给了结构示例，但它们不是“固定枚举库”，所以没法做成像附录那样的全量编号表。

### 3. 当前仓库没有直接附带全量目录的项

- `text_shape`：仓库只提供结构和引用方式，没有自带完整文字气泡 / 文字底板清单
- 贴纸：仓库有搜索接口/模板导入思路，但没有像滤镜那样的固定元数据枚举文件

如果你以后还要把 `text_shape` 也做成全量清单，只能再从真实模板草稿或素材库数据里额外抽。


---

## 十、全量样式目录总览

下面这张表是“当前仓库里可以直接枚举出来的全部固定样式目录”。
注意：`materials[*].id` 这种运行时素材 ID 每次生成草稿都可能变，不属于固定样式编号；附录里整理的是你真正需要记的 `effect_id` / `resource_id` / 花字 ID。

| 类别 | 数量 | 免费 | VIP | 草稿位置 | 实际编号字段 | 附录 |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 字体 | 798 | 480 | 318 | materials.texts[*].content.styles[*].font.id | resource_id | 附录 A |
| 花字 | 1673 | 94 | 1579 | materials.texts[*].content.styles[*].effectStyle.id + materials.effects[type=text_effect] | huazi_id（实际等于 effect_id/resource_id） | 附录 B |
| 文字入场动画 | 145 | 67 | 78 | materials.material_animations[*].animations[*] | effect_id + resource_id | 附录 C |
| 文字出场动画 | 97 | 51 | 46 | materials.material_animations[*].animations[*] | effect_id + resource_id | 附录 D |
| 文字循环动画 | 93 | 41 | 52 | materials.material_animations[*].animations[*] | effect_id + resource_id | 附录 E |
| 滤镜 | 1052 | 250 | 802 | materials.effects[type=filter] | effect_id + resource_id | 附录 F |
| 视频场景特效 | 1097 | 635 | 462 | materials.video_effects[type=video_effect] | effect_id + resource_id | 附录 G |
| 视频人物特效 | 240 | 159 | 81 | materials.video_effects[type=face_effect] | effect_id + resource_id | 附录 H |
| 音频场景音 | 85 | 12 | 73 | materials.audio_effects[type=audio_effect] | resource_id（草稿主要落这个） | 附录 I |
| 音色 | 57 | 14 | 43 | materials.audio_effects[type=audio_effect] | resource_id（草稿主要落这个） | 附录 J |
| 声音成曲 | 6 | 2 | 4 | materials.audio_effects[type=audio_effect] | resource_id（草稿主要落这个） | 附录 K |
| 视频入场动画 | 155 | 38 | 117 | materials.material_animations[*].animations[*] | effect_id + resource_id | 附录 L |
| 视频出场动画 | 124 | 21 | 103 | materials.material_animations[*].animations[*] | effect_id + resource_id | 附录 M |
| 视频组合动画 | 123 | 107 | 16 | materials.material_animations[*].animations[*] | effect_id + resource_id | 附录 N |
| 转场 | 453 | 130 | 323 | materials.transitions[*] | effect_id + resource_id | 附录 O |
| 蒙版 | 6 | 6 | 0 | materials.masks[*] | effect_id + resource_id | 附录 P |
| 混合模式 | 10 | 10 | 0 | materials.effects[type=mix_mode] | effect_id + resource_id | 附录 Q |


---

## 附录 A 字体清单（798 条）

- 挂载位置：materials.texts[*].content.styles[*].font.id
- 草稿实际使用编号：resource_id
- 补充说明：这里额外保留 effect_id，方便你和仓库元数据对照
- 免费 480 条，VIP 318 条
```text
name | effect_id | resource_id | is_vip
3D 만화 | 20402387 | 6841117833447870990 | false
A1明朝 | 20403949 | 7246698168547545602 | false
AlexBrush | 14864426 | 7241838813960475173 | false
Alice-Regular | 14443129 | 7238874837500826170 | false
Alike-Regular | 14443547 | 7238879091334582821 | false
Allura-Regular | 14864457 | 7239181917067678266 | false
Amble-Regular | 14138187 | 7236679983140180539 | false
Amigate | 1485328 | 7042231710112551431 | false
Anson | 37083210 | 7312373886476096001 | false
Anton | 643585 | 6807743423336944142 | false
Arizonia-Regular | 14864444 | 7239188828425032252 | false
Arvo | 14451489 | 7238901809073361467 | false
Ballet | 14864427 | 7241838661656908343 | false
Barrio-Regular | 14471579 | 7239174980292842044 | false
Belleza-Regular | 13824767 | 7234404156780319288 | false
Bevan-Regular | 14400121 | 7238530249451901496 | false
Bilbo-Regular | 14864440 | 7239189505289228861 | false
BlackMango-Regular | 41472093 | 7306445155244970497 | false
Blinker-Thin | 10587620 | 7209874013324055098 | false
Boxing | 1648729 | 7078972382651617805 | false
Bungee-Regular | 37039650 | 7314592672792973826 | false
Caladea-Regular | 10587623 | 7209874013319860797 | false
Calfine | 1632683 | 7076269550299255309 | false
Candal-Regular | 13854523 | 7234514498579599928 | false
Candice | 1656182 | 7080446593123488286 | false
Carattere-Regular | 22621896 | 7277869798401249851 | false
Cardo-Regular | 10587624 | 7209874013324055101 | false
Caveat-Bold | 14864446 | 7239187536675869242 | false
Caveat-Regular | 22621892 | 7277872672304796217 | false
Chonburi-Regular | 10608872 | 7209944750021939771 | false
Cinzel-Regular | 10587622 | 7209874013324055095 | false
Coda-Heavy | 13854593 | 7234514878008922681 | false
Coiny-Regular | 27240316 | 7203293403990200834 | false
Cola | 1632682 | 7076270486740537863 | false
Cookie-Regular | 14864454 | 7239182754624049720 | false
Cormorant Garamond-Medium | 14451211 | 7238899812190392888 | false
Coustard-Regular | 10587614 | 7209874014028698172 | false
Crimson-SemiboldItalic | 14864433 | 7239227834273632827 | false
Dynalight-Regular | 14864435 | 7239227395088060987 | false
Exo | 1349503 | 7003588519440421413 | false
Facon | 643587 | 6807743498851193352 | false
FiraSans-Book | 14037099 | 7236005080040739388 | false
Fraunces-Black | 10587607 | 7209874014221636155 | false
Fulbo-Argenta | 14490123 | 7239234097267085861 | false
Gallery | 1441466 | 7030677248797577765 | false
GenWanMinJP-Light（源云明体） | 20356559 | 7265529261530812985 | false
GenWanMinJP-Medium（源云明体） | 20356561 | 7265529620802310713 | false
GenWanMinJP-Regular（源云明体） | 20356563 | 7265529744542667322 | false
GenWanMinJP-SB（源云明体） | 20356565 | 7265529923547173413 | false
Giveny | 1441468 | 7030676531156357645 | false
Great Vibes-Regular | 14864431 | 7239229310119187001 | false
Grenze-Thin | 10587602 | 7209874014951445051 | false
HG行書体 | 20402937 | 6808052324217393677 | false
HarmonyOSCn-Ltlt | 20373125 | 7265589159580930621 | false
HarmonyOS_Sans_SC_Bold | 20374146 | 7265594890002633272 | false
HarmonyOS_Sans_SC_Light | 20374151 | 7265595050145354295 | false
HarmonyOS_Sans_SC_Medium | 20374140 | 7265595177916437050 | false
HarmonyOS_Sans_SC_Regular | 20374142 | 7265595305163231781 | false
HarmonyOS_Sans_TC_Bold | 20356569 | 7265530043495879226 | false
HarmonyOS_Sans_TC_Light | 20356571 | 7265530445658329661 | false
HarmonyOS_Sans_TC_Medium | 20356573 | 7265530519687795255 | false
HarmonyOS_Sans_TC_Regular | 20356575 | 7265530629050077754 | false
HeptaSlab-Light | 22621897 | 7277873865001275964 | false
Inter-SemiBold | 37039662 | 7314592494006571522 | false
Italianno | 14864422 | 7241839293499445820 | false
Jellee-Bold | 14489881 | 7239233471132996153 | false
Kanit-ExtraBoldItalic | 48512062 | 7341281330442801665 | false
Kanit-Regular | 48512024 | 7341281459799331330 | false
KaushanScript | 14864425 | 7241838959305691707 | false
Koulen-Regular | 48512036 | 7341281656319250945 | false
LXGWWenKai-Bold | 20373127 | 7265591538472718903 | false
LXGWWenKai-Light | 20373111 | 7265592227118715448 | false
LXGWWenKai-Regular | 20373101 | 7265591946897265212 | false
Letter | 349325 | 6740438320989344263 | false
Lexend Tera-Regular | 13897171 | 7234820388151104061 | false
Lora-Regular | 14443153 | 7238875962530599481 | false
Love | 459276 | 6766522308593979917 | false
Luxury | 41472051 | 7291876268541219329 | false
Maler | 1654362 | 7080115730963763743 | false
Marker | 459282 | 6766523474354639373 | false
Mirza-Regular | 14471319 | 7239174396349256249 | false
Misto | 1648728 | 7078972749472862757 | false
Modern | 349479 | 6740498577912500749 | false
Mokgech | 1485324 | 7042232545433358878 | false
Montserrat-Black | 37039624 | 7314592902414340609 | false
Montserrat-Thin | 10608863 | 7209944750529450554 | false
Nunito | 643589 | 6807743644842332685 | false
OldStandardTT-Regular | 22621894 | 7277874282493907512 | false
Parisienne-Regular | 14864430 | 7239229422367150652 | false
Playfair Display SC-Re | 14450193 | 7238897435437699639 | false
PlayfairDisplay-Italic | 14451355 | 7238900597125026341 | false
Plunct | 1459552 | 7035916496484176421 | false
Polly | 1648730 | 7078971156350374431 | false
Poppins-Bold | 41472095 | 7312373689708712449 | false
Poppins-Regular | 41472101 | 7202912523383738881 | false
Prata | 643593 | 6807743776916771335 | false
Quattrocento-Regular | 14450839 | 7238898734724026917 | false
RedHatDisplay-BoldItalic | 48512032 | 7341281783637348865 | false
RedHatDisplay-Light | 48512058 | 7341282109987754497 | false
ReenieBeanie-Regular | 22618063 | 7277866226397745701 | false
ResourceHanRoundedCN-Bold | 20374132 | 7265596195949515319 | false
ResourceHanRoundedCN-Lt | 20374136 | 7265596294683431485 | false
ResourceHanRoundedCN-Md | 20374131 | 7265596408491676197 | false
ResourceHanRoundedCN-Nl | 20374148 | 7265596514955694649 | false
Rix독도 | 645449 | 6808056629678838286 | false
Romantic | 643581 | 6807743277853315597 | false
Rubik | 1349502 | 7003588607231398430 | false
SansitaSwashed-Regular | 37108558 | 7314592065168347650 | false
SecularOne-Regular | 37082988 | 7312374157725929986 | false
Serrat | 1588332 | 7068208488563872286 | false
Signature | 1485330 | 7042230917837885965 | false
Soap | 1632684 | 7076269202771808804 | false
SourceHanSansCN-Bold | 20374122 | 7265596643066516029 | false
SourceHanSansCN-Light | 20374126 | 7265596753926165050 | false
SourceHanSansCN-Medium | 20374144 | 7265596846465094199 | false
SourceHanSansCN-Normal | 20374137 | 7265596944867660346 | false
SourceHanSansCN-Regular | 20374128 | 7265597035946971705 | false
SourceHanSansTW-Bold | 20356585 | 7265530703364756026 | false
SourceHanSansTW-Light | 20356587 | 7265530900580930085 | false
SourceHanSansTW-Medium | 20356589 | 7265530989479203389 | false
SourceHanSansTW-Normal | 20356591 | 7265531070680928828 | false
SourceHanSansTW-Regular | 20356593 | 7265531198548480568 | false
SourceHanSerifCN-Bold | 20374153 | 7265597144600416827 | false
SourceHanSerifCN-Light | 20374143 | 7265597259708895803 | false
SourceHanSerifCN-Medium | 20374123 | 7265597365539574329 | false
SourceHanSerifCN-Regular | 20374152 | 7265597449262076474 | false
SourceHanSerifCN-SemiBold | 20374118 | 7265598654294004281 | false
SourceHanSerifTW-Bold | 20356595 | 7265534770845585980 | false
SourceHanSerifTW-Light | 20356597 | 7265535017625850429 | false
SourceHanSerifTW-Medium | 20356599 | 7265535154775396919 | false
SourceHanSerifTW-Regular | 20356601 | 7265535307322233399 | false
SourceHanSerifTW-SemiBold | 20356603 | 7265535436594876984 | false
SourceSansPro-Regular | 14035983 | 7235998842880004665 | false
Specta | 1478300 | 7039992016805040671 | false
Spicy Rice-Regular | 14864429 | 7239229520828437053 | false
Staatliches-Regular | 37083204 | 7312373990083793409 | false
Sunset | 643591 | 6807743703436759566 | false
Thrive | 26148239 | 7290877082660246071 | false
Thunder | 1511612 | 7050422198724465189 | false
Work Sans-ExtraBoldItalic | 10608852 | 7209944751246676517 | false
WorkSans-BlackItalic | 14137039 | 7236677807634387511 | false
WorkSans-Regular | 14963149 | 7242301481699775032 | false
ZEN丸ゴシック | 20403385 | 7236735800514187831 | false
ZEN紅道 | 20403919 | 7244104371372298754 | false
ZY Alluring-Regular | 22616627 | 7277862842190008891 | false
ZY Azure | 13314774 | 7230715188326961721 | false
ZY Bless | 13168499 | 7229615361967002172 | false
ZY Coconut-Regular | 22618062 | 7277865493736722981 | false
ZY Dexterous | 38698692 | 7320169657841750529 | false
ZY Diligent | 21346088 | 7270787894317421093 | false
ZY Etiquette | 19649099 | 7262284005293167160 | false
ZY Fervent | 40751208 | 7325315777014272514 | false
ZY Heaven | 18436001 | 7256754129400238649 | false
ZY Hope | 22346588 | 7276364919165948474 | false
ZY Innocent | 18436002 | 7256754220588601913 | false
ZY Modest | 22346583 | 7276365485812224571 | false
ZY Oliver | 13314772 | 7230715372683399740 | false
ZY Panorama | 19649101 | 7262284073026982460 | false
ZY Radiance | 16174404 | 7248820625366585915 | false
ZY Rainbow | 22346586 | 7276365019292373559 | false
ZY Resolve | 37544856 | 7317175475195875841 | false
ZY Superb-Regular | 22618066 | 7277866017231999525 | false
ZY Vibrant | 22346584 | 7276365787147801145 | false
ZY Wonder | 21346084 | 7270788266683535932 | false
ZYCherish | 26013701 | 7290485005162123813 | false
Zapfino | 1632681 | 7076271146110292494 | false
いろは角クラシックE | 20403373 | 7236735800514187833 | false
いろは角クラシックM | 20403369 | 7236735800501604924 | false
きざはし金陵 | 20403943 | 7246698168547545601 | false
くり抜く | 20403197 | 6990291609376002562 | false
しっぽりアンチック | 20403443 | 7236735800442884645 | false
すずむし | 20404003 | 7246698168543351297 | false
だるまどろっぷ | 20403579 | 7236735800388358715 | false
つきみ丸ゴかな B | 20403581 | 7236735800371581501 | false
つきみ丸ゴかな R | 20403643 | 7236735800363192891 | false
はちきるポップ | 20403715 | 7236735799817933368 | false
ひな明朝 | 20403717 | 7236735799817933367 | false
ぽってり | 20403945 | 7246698168551739906 | false
オとマのペ | 20403367 | 7236735800459661861 | false
ギガ丸 | 20403939 | 7246698169348657665 | false
キャビン | 20403069 | 6841482472102826510 | false
クレー One | 20403427 | 7236735800442884667 | false
ゴシック | 20404037 | 7246698168543367682 | false
コスギ | 20402991 | 6808051939150926344 | false
ゴシック | 459278 | 6766522798685819399 | false
タイムマシンわ号 | 20404343 | 7236735800430301753 | false
チェリーボム | 20403877 | 7239261205582320129 | false
デラゴシック | 20403647 | 7236735799822127674 | false
ドットゴシック 16 | 20403657 | 7236735799813739069 | false
ニューテゴミン | 20403683 | 7236735799822127653 | false
ビジネス | 20402993 | 6808051344142766599 | false
ブロック | 20403043 | 6841483116922540558 | false
ペンレタ | 20404089 | 7246698168543384066 | false
ポッタ | 20404337 | 7236735799817933370 | false
ポジティブ | 20403295 | 7013643531847733761 | false
ミンサン書体B | 20403895 | 7239261205586514433 | false
ミンサン書体R | 20403909 | 7239261205594903041 | false
メモ | 20403011 | 6841483408602829326 | false
メモ帳 | 20403233 | 6990291446100136449 | false
モッチーポップ | 20403817 | 7236735799813739045 | false
ランパート | 20403869 | 7236735799817933373 | false
レゲエ One | 20403871 | 7236735799813739068 | false
ロックンロール | 20403875 | 7236735799809544763 | false
ローマ | 20403063 | 6841482587446186509 | false
中秀体 | 1014410 | 6917512631515353607 | false
书南体 | 25998982 | 7290445475461730875 | false
云魅手书 | 7048145 | 7174434449080193550 | false
今宋体 | 11443544 | 7216598549809599032 | false
仓耳与墨W05 | 20373115 | 7265576717970838076 | false
仓耳周珂正大榜书 | 20373112 | 7265577040110162492 | false
仓耳小丸子 | 20373117 | 7265576611347436093 | false
仓耳舒圆体W02 | 20373116 | 7265576364948853303 | false
仓耳非白W02 | 20373124 | 7265576127073096250 | false
仓耳非白W04 | 20373114 | 7265576259957035579 | false
以梦为马 | 9182767 | 7197366059056239141 | false
优设好身体 | 20379296 | 7265610359807939132 | false
优设标题圆 | 19366221 | 7260808713844298295 | false
优设标题黑 | 1588336 | 7068207165277737502 | false
伯兮体 | 25999024 | 7290440685616894522 | false
佑字 朴 | 20403343 | 7236735801042670136 | false
佑字 舞 | 20403425 | 7236735801021698619 | false
佳妙体 | 25998997 | 7290443628554490423 | false
俊雅体 | 1648731 | 7078971008769593887 | false
俪金黑 | 349465 | 6740499317733200388 | false
像素体 | 466469 | 6770944991167517192 | false
元也 | 20403229 | 6990291473216311809 | false
元气泡泡体 | 9898775 | 7203664981080937021 | false
元瑶体 | 25999023 | 7290447082886795832 | false
先锋体 | 1488720 | 7043775345333375519 | false
光远体 | 25999003 | 7290442818584056357 | false
兰亭圆 | 6949825 | 7173608955527041567 | false
凌东齐伋体-combo | 20379306 | 7265611544820453948 | false
凌东齐伋体-fallback | 20379309 | 7265611310132367931 | false
凝琴体 | 25999011 | 7290444849298281021 | false
刘炳森 | 814922 | 6852190696930021902 | false
初尘体 | 25998986 | 7290441058238861879 | false
匹喏曹 | 1488716 | 7043773350555947551 | false
半梦体 | 25999018 | 7290439421625635385 | false
南廱明體 | 20356611 | 7265535751624856101 | false
卡酷体 | 1494864 | 7045187669847970341 | false
古典体 | 1459456 | 7035911487646339598 | false
古印宋简 | 11443545 | 7216598368791827002 | false
古雅体 | 1425152 | 7025895760583463438 | false
古风小楷 | 11443543 | 7216598671016596029 | false
台北黑体-Bold | 20356617 | 7265536086472921658 | false
台北黑体-Light | 20356619 | 7265536169083933242 | false
台北黑体-Regular | 20356621 | 7265536307932172861 | false
后现代体 | 349307 | 6740435494053614093 | false
启功行楷 | 814921 | 6852190785740214791 | false
吹き出し | 20403057 | 6841482925955879431 | false
唐瑜体 | 25998993 | 7290445542331519525 | false
喜悦体 | 1494856 | 7045187886924173861 | false
喜鹊万人造字 | 10379503 | 7208056956471218748 | false
喜鹊梅花楷 | 10379504 | 7208056839089427002 | false
喵魂体 | 349315 | 6740436949040894475 | false
嘉木体 | 25999016 | 7290443820041245241 | false
圆体 | 349313 | 6740436583247254029 | false
基础像素 | 9893377 | 7203638484752405049 | false
墩墩体 | 1488712 | 7043772438898807304 | false
大字报 | 1530068 | 7054126026267300382 | false
天云体 | 25998981 | 7290445618533634617 | false
妙松体 | 25998991 | 7290444755811439141 | false
妙黑体 | 9893375 | 7203638484756599333 | false
子どもたち | 20402995 | 6766524209620324877 | false
字制区喜脉体 | 75248650 | 7391765808835203647 | false
字制区喜脉喜欢体 | 75248705 | 7391765873716892199 | false
孤月体 | 25999015 | 7290441418395357754 | false
宋体 | 349517 | 6740513279296147982 | false
小杉ｺﾞｼｯｸ | 20403079 | 6841482326321402375 | false
小薇体 | 20373097 | 7265594602311127607 | false
尔雅新大黑 | 11593555 | 7217732136894206501 | false
居酒屋 | 20403285 | 7013643566341689858 | false
山林体 | 1459484 | 7035912592925135396 | false
岩柚体 | 25999002 | 7290445914571805245 | false
峰骨体 | 1530066 | 7054126189211816462 | false
幸せ | 20403193 | 6990291634747347458 | false
幼萱体 | 25998999 | 7290446812442268217 | false
庞门正道标题体 | 20379302 | 7265611148060267045 | false
庞门正道粗书体 | 20379291 | 7265611032465248805 | false
庞门正道轻松体 | 20379295 | 7265610901795902013 | false
张子山体 | 961476 | 6894206029785993736 | false
彼岸体 | 25999019 | 7290440016646378042 | false
得意黑 | 77844112 | 7399865900821647935 | false
德古拉 | 1404774 | 7021353291850191368 | false
快乐体 | 20373113 | 7265594331262620217 | false
快速体 | 9182766 | 7197366121069023804 | false
思源中宋 | 643579 | 6807743192671195655 | false
思源粗宋 | 643575 | 6807742980271641102 | false
悠悠然 | 1665070 | 7081924596999393805 | false
悠然体 | 349311 | 6740436145831678467 | false
悦妍体 | 25998984 | 7290447167821451813 | false
惊鸿体 | 9893376 | 7203638484756599356 | false
手書 | 20403235 | 7013643615326966273 | false
抖音美好体 | 15332487 | 7244518590332801592 | false
招牌体 | 1459526 | 7035914068053463565 | false
拼音体 | 349319 | 6740437635287749133 | false
挥墨体 | 1464398 | 7037018943218782757 | false
教科書 | 20403203 | 6990291514886722050 | false
文研体 | 1203468 | 6990293257540342302 | false
文艺繁体 | 349321 | 6740437797456318983 | false
文轩体 | 25998976 | 7290445778273702455 | false
文雅体 | 1588334 | 7068208151488631309 | false
新青年体 | 349309 | 6740435892441190919 | false
方正王铎行草 | 814918 | 6852191050547597832 | false
方糖体 | 1464396 | 7037017159280628231 | false
无界黑 | 9893370 | 7203638485670957629 | false
日式标题 | 1665068 | 7081925137355772453 | false
星光体 | 11443542 | 7216598789103030821 | false
晨风体 | 25999012 | 7290440791967666725 | false
景天体 | 25999010 | 7290444063004693029 | false
晴雪体 | 25999004 | 7290445254241555005 | false
書道 | 20403191 | 6990291666124935681 | false
有猫在 | 459290 | 6766524065151717901 | false
未来黑 | 1665065 | 7081925520866152997 | false
本黑体 | 9554613 | 7200743888816968247 | false
李李体 | 9893380 | 7203638484752405053 | false
极简拼音 | 1600484 | 7070430470667768333 | false
柏青体 | 8393133 | 7187746468785033787 | false
柳公权 | 814920 | 6852190880837669390 | false
梅雨煎茶 | 1665067 | 7081925245099053604 | false
梦寒体 | 25999021 | 7290444357499359781 | false
梦想家 | 1005688 | 6914965725543141896 | false
梦桃体 | 25998998 | 7290444545689391653 | false
梦槐体 | 25998996 | 7290444451179139641 | false
棘薔薇ボールド | 20403299 | 7236735801134944823 | false
棘薔薇ライト | 20403311 | 7236735801105584701 | false
楚辰体 | 1600482 | 7070430593925779981 | false
楷書MCBK1 | 20404083 | 7246698168547578369 | false
欣然体 | 1589146 | 7068531082265629197 | false
正奇体 | 25999005 | 7290447230488547901 | false
毛笔行楷 | 999616 | 6912033793700270606 | false
毡笔体 | 1459716 | 7035924520854622757 | false
汇文明朝体 | 95241741 | 7444913491762221577 | false
汉仪英雄体 | 349471 | 6740499052644798984 | false
汉仪贤二体 | 20379294 | 7265612201199669816 | false
江户招牌 | 1654205 | 7080096840875512334 | false
江湖体 | 1654203 | 7080097079397192228 | false
沈尹默 | 814919 | 6852190963947803143 | false
油性マジック | 20403341 | 7236735801076224568 | false
油漆体 | 1459392 | 7035906361040835079 | false
海岛森林-全字符 | 95365506 | 7445240658693984805 | false
清刻本悦 | 1698068 | 7086429206543864350 | false
清酒体 | 25999017 | 7290445172834308664 | false
渊亭体 | 25999013 | 7290447006659514941 | false
温宁体 | 25998977 | 7290445705578025529 | false
温柔体 | 1511616 | 7050009415155454500 | false
港风繁体 | 349323 | 6740438140432945675 | false
游园体 | 25998988 | 7290446760739082789 | false
游思体 | 25998994 | 7290446655604658748 | false
源ノ角ゴシック | 20403397 | 7236735800992338487 | false
漫语体 | 1665066 | 7081925440264213000 | false
澄月 | 20404007 | 7246698168547561986 | false
瀞ノクーゲル明朝 | 20403339 | 7236735801088807482 | false
点宋体 | 1654204 | 7080096967543493150 | false
烈金体 | 1488714 | 7043773114546655781 | false
烟波宋 | 1589144 | 7068531367386026526 | false
爨宝子碑 | 814916 | 6852191233356337671 | false
特黑体 | 349329 | 6740439840254333443 | false
玉轩体 | 25999001 | 7290446916402287163 | false
玩童体 | 459292 | 6766524209620324877 | false
琉璃宋 | 1402720 | 7020719089999942157 | false
瑞意宋 | 3997461 | 7130447431891685895 | false
瑶蝶体 | 25998987 | 7290446536050217532 | false
甜甜圈 | 4009729 | 7130634783163421215 | false
白舟武骨 | 10971151 | 7212913285383852600 | false
目光体 | 1459640 | 7035921361348334117 | false
真言体 | 1349505 | 7003588300720050696 | false
知夏森林 | 12441415 | 7224042336223760954 | false
研宋体 | 4010355 | 7130644288047682085 | false
研月体 | 25998978 | 7290446001947546149 | false
禅影体 | 22902355 | 7278963576167993916 | false
秀英四号太かな | 20404005 | 7246698168543351298 | false
站酷仓耳渔阳体-W02 | 20379308 | 7265609366311539237 | false
站酷仓耳渔阳体-W03 | 20379299 | 7265610166744125989 | false
站酷仓耳渔阳体-W04 | 20379307 | 7265609848438395449 | false
站酷文艺体 | 20373100 | 7265593885475213880 | false
站酷酷黑体 | 20379297 | 7265609486646121018 | false
童趣体 | 1459176 | 7035888265290846756 | false
竹柏体 | 25998983 | 7290447547208831544 | false
竹风体 | 25998973 | 7290447605065060901 | false
简中圆 | 1511618 | 7050009066717844005 | false
糯米团 | 1053146 | 6934225430266253837 | false
結月 | 20403297 | 7013643491003601410 | false
纯真体 | 1494870 | 7045185581772444174 | false
细体 | 349521 | 6740511815358222859 | false
经典雅黑 | 1488718 | 7043775037559542279 | false
综艺体 | 349467 | 6740499188347310605 | false
综艺字 | 4010283 | 7130642664080282149 | false
美佳体 | 9898774 | 7203665054338650685 | false
聚珍体 | 9893381 | 7203638484752405051 | false
胡晓波男神体 | 20379293 | 7265612031825285689 | false
胡晓波真帅体 | 20379292 | 7265611790313067069 | false
胡晓波骚包体 | 20379298 | 7265611912849658429 | false
芋圆体 | 1478272 | 7039989971796628005 | false
花语手书 | 1665069 | 7081925028773630471 | false
芷云体 | 25998979 | 7290447317247726139 | false
若烟体 | 25999000 | 7290445344557503033 | false
荔枝体 | 349483 | 6740498118342611464 | false
萌趣体 | 1494868 | 7045186231122006535 | false
萧疏体 | 25998989 | 7290445832845791801 | false
蒹葭体 | 25999014 | 7290443923556667959 | false
薯条少年 | 1589148 | 7068530728467698213 | false
蜡笔体 | 1049208 | 6932407677234450952 | false
蝉影隶书 | 1494867 | 7045186520738697742 | false
蝶汐体 | 25999007 | 7290441304029270587 | false
装甲明朝 | 20356625 | 7265536455655559739 | false
解星デコール | 20403335 | 7236735801088807461 | false
谷槐体 | 25999006 | 7290442552933618213 | false
谷秋体 | 25999008 | 7290442742822343205 | false
超级战甲 | 1156412 | 6970982657576407559 | false
超重要体 | 9893378 | 7203638484752405048 | false
轻吟体 | 1459730 | 7035927184275411464 | false
轻烟体 | 25998992 | 7290445091401896507 | false
追光体 | 9893371 | 7203638485666763325 | false
造字工房朴月体 | 7046698 | 7174426619228983816 | false
逸致拼音 | 1600480 | 7070430706689643038 | false
醉冬体 | 25998974 | 7290447667463721531 | false
醉山体 | 25998980 | 7290447771503432250 | false
金陵体 | 1698067 | 7086699209738424840 | false
钟隶体 | 25998975 | 7290447395433747002 | false
锦瑟体 | 25999022 | 7290443998345302586 | false
闘龍 | 20403941 | 7246698168547561985 | false
陈森田 | 349461 | 6740499585669534215 | false
雁兰体 | 25998990 | 7290446084780855867 | false
雅酷黑简 | 4010137 | 7130640934366089758 | false
霸燃手书 | 1494865 | 7045187409960505886 | false
青松体 | 25998985 | 7290444911940211237 | false
青翼体 | 25998995 | 7290445024435638842 | false
风铃悠悠 | 979898 | 6903832640005083655 | false
风雅宋 | 10379505 | 7208056673317950011 | false
飒爽手写 | 1530070 | 7054125855676568095 | false
飞扬行书 | 1459678 | 7035922620969128479 | false
飞驰体 | 1494866 | 7045186745100407310 | false
高字标志黑 | 20885841 | 7268259518427959866 | false
高字湘黑体 | 20885842 | 7268259657167147577 | false
魏碑体 | 1459722 | 7035925927364137480 | false
鲁迅行书 | 814917 | 6852191147230499341 | false
鸿朗体 | 25999020 | 7290443206641062456 | false
鸿潮榜书 | 1654206 | 7080096689553412615 | false
黄令东齐伋复刻体 | 20356605 | 7265535655105532476 | false
黄油体 | 20373099 | 7265594455246246456 | false
黄金时代 | 1511614 | 7050010418932093471 | false
黎首体 | 25999009 | 7290444159842783803 | false
黒明朝 | 20404021 | 7246698169310908930 | false
默陌手写 | 1424938 | 7025886295524119053 | false
검 | 20402365 | 6841117522335371789 | false
검은 고딕체 | 20402283 | 6808056243958059534 | false
고딕 | 20402461 | 6841143710177038856 | false
고딕체 | 20402279 | 6808056385679397389 | false
귀염 | 20402361 | 6841117240457171470 | false
나눔 명조체 | 20402271 | 6808057418866496014 | false
낭만 | 20402441 | 6841119058838950414 | false
로맨틱가이 | 20402275 | 6808056744258834952 | false
로봇 | 20402445 | 6841119449815192071 | false
룬 | 20402401 | 6841118098964091405 | false
버터 | 20402443 | 6841119192150708744 | false
성냥개비 | 20402431 | 6841118217641923085 | false
소나무 | 20402359 | 6841116992846434829 | false
시트콤 | 20402357 | 6841116836445032974 | false
십대 | 20402363 | 6841117356756832776 | false
아기 | 645451 | 6808056941458231815 | false
아이 | 20402433 | 6841118486639415822 | false
유행 | 20402399 | 6841117979371901454 | false
이야기 | 20402435 | 6841118628025209358 | false
전통 | 20402311 | 6808056067201700360 | false
초승달 | 20402369 | 6841117705538376205 | false
추사체 | 20402301 | 6808057229309121038 | false
커피 | 20402437 | 6841118775186559495 | false
필기 | 459288 | 6766523918946669069 | false
한드 | 20402439 | 6841118889850442254 | false
행복 | 20402465 | 6841151352597385735 | false
흑백만 | 20402327 | 6841116695759688205 | false
ｱﾄﾞｺﾞｯｼｸ | 20403099 | 6841482093025825288 | false
ｵｰﾊﾞｰﾗｯﾌﾟ | 20403059 | 6841482806573404680 | false
ｽｸﾘﾌﾟﾄ | 20403035 | 6841483289438458381 | false
ｾﾘﾌ太字 | 1402800 | 7020729846334493215 | false
ｾﾘﾌﾗｲﾄ | 20403113 | 6841481513985380872 | false
ﾓｰﾀﾞ太字 | 20403121 | 6841481374243754510 | false
ﾓｰﾀﾞﾗｲﾄ | 20403133 | 6841480712739099150 | false
ﾚｷﾞｭﾗｰ | 20403061 | 6841482701082464776 | false
Aa之云体 | 115474299 | 7501533851718521394 | true
Aa乌日莫 | 115375585 | 7501234570835006003 | true
Aa人间蹉跎 | 115473709 | 7501532931635024434 | true
Aa全息黑体 | 114156127 | 7497891126481785381 | true
Aa刃黑体 | 114159648 | 7497895571210900005 | true
Aa剑豪体 | 115395999 | 7501261456420114981 | true
Aa动员宋 | 115377308 | 7501238408837075483 | true
Aa勘亭流 | 115360771 | 7501211609050649115 | true
Aa厚底黑 | 7047541 | 7174431250067755577 | true
Aa古线体 | 115360774 | 7501211793906209331 | true
Aa台灣漢字心動信號（简繁） | 114154846 | 7497889331973984805 | true
Aa封神榜书 | 115375582 | 7501235311461012018 | true
Aa小星星 | 115474013 | 7501533449530905114 | true
Aa居酒屋 | 115478734 | 7501539460945809957 | true
Aa巴洛克 | 115375583 | 7501235648557224498 | true
Aa幻想 | 115473869 | 7501533252969042470 | true
Aa德古拉简 | 114171804 | 7497898575926399498 | true
Aa放放隶书 | 114155759 | 7497890527145103881 | true
Aa新华墨竹体 | 114158131 | 7497893640140755494 | true
Aa新华惊马体 | 115377540 | 7501238774051902002 | true
Aa新怪谈 | 115375584 | 7501235484727710246 | true
Aa方块黑 | 114158130 | 7497893873037873714 | true
Aa未央宫词 | 114157130 | 7497892647986532914 | true
Aa杜康手书 | 115396001 | 7501262679810511370 | true
Aa欢乐堡 | 115375586 | 7501235116673339954 | true
Aa水玉圆体 | 115360773 | 7501211417521951270 | true
Aa浮梦体 | 115360769 | 7501212180285493787 | true
Aa海豹体 | 115360770 | 7501212376713138698 | true
Aa清欢圆体 | 114158127 | 7497893259797074441 | true
Aa漆书 | 114155607 | 7497890203277726235 | true
Aa烈焰隶书 | 115378827 | 7501239212855792165 | true
Aa狂派手书 | 115396002 | 7501260939212100146 | true
Aa疏漫宋 | 114171805 | 7497897887477535242 | true
Aa百物语 | 115375580 | 7501234966815052339 | true
Aa祝融隶 | 115396000 | 7501262524466074121 | true
Aa简正隶黑 | 115377425 | 7501238583911518729 | true
Aa芥末墩 | 115375581 | 7501234746416960050 | true
Aa菊花体 | 114158129 | 7497894073559159323 | true
Aa融融宋 | 115377151 | 7501238214691131930 | true
Aa西风手书 | 114156355 | 7497891525213295114 | true
Aa跃然体 | 115395996 | 7501262110492463625 | true
Aa醒狮体 | 115395997 | 7501260756655018533 | true
Aa金石体 | 114156237 | 7497891337044234789 | true
Aa锐智体 | 115377035 | 7501238022352933413 | true
Aa锐甲黑 | 114159647 | 7497896024078291482 | true
Aa锐雅体 | 114159649 | 7497896536597074483 | true
Aa镁宋 | 114171803 | 7497898052825387530 | true
Aa闲云体 | 115396003 | 7501261128207438386 | true
Aa霸道楷 | 115360768 | 7501210878839099930 | true
Aa顽宋 | 114159645 | 7497896719514866203 | true
Aa鲸潮体 | 115395998 | 7501261289486815795 | true
Aa鹅卵石 | 114158128 | 7497894333161411098 | true
Aa麟兰宋 | 114159646 | 7497896347551404595 | true
Aa龙象体 | 115360772 | 7501211164332790298 | true
Atomic-Marker | 111804574 | 7490531359736205834 | true
Awelier | 112259365 | 7491984624688566835 | true
CC-Captial | 84086581 | 7418508570066424330 | true
CC-Chubby | 108570272 | 7481130667518988850 | true
CC-Decocut | 84566362 | 7419969356659954214 | true
CC-DerStil | 108570258 | 7481130779821478426 | true
CC-Element | 83388253 | 7416649778416587274 | true
CC-Fluffy | 82112759 | 7412942953905132049 | true
CC-Fusion | 93510805 | 7441202923708617227 | true
CC-Glee | 87224070 | 7428153662695805478 | true
CC-Loopy Letters | 109692383 | 7484186924291199526 | true
CC-Manga | 109692410 | 7484175941208379914 | true
CC-Moderno | 94915234 | 7444152681741947403 | true
CC-MonoCut | 83245166 | 7416261331872911881 | true
CC-Piston | 82624536 | 7414496688611529255 | true
CC-Rapid | 89156910 | 7434004568716874259 | true
CC-UltraMass | 108570236 | 7481130884687467046 | true
CC-Vita | 84566385 | 7419969457788817929 | true
CC-lemon | 109692355 | 7484188078546883082 | true
Clostan | 112259661 | 7491985061500162598 | true
Gildan | 112260846 | 7491984485504782874 | true
Gildan-It | 112259122 | 7491984248069427750 | true
JYruantang | 98222876 | 7451897289527792178 | true
JYshiduo | 98222874 | 7451897058371310117 | true
JYzhuqingting | 98222875 | 7451897479320048166 | true
Mellow | 112259480 | 7491984798026568218 | true
Merry Christmas | 98103035 | 7451574186692055578 | true
Morska | 112259573 | 7491984914565304870 | true
MyFont凌渡哥哥简 | 36880890 | 7316825302406009395 | true
MyFont凌渡猪猪简 | 36880879 | 7316826370200310298 | true
Railway-Gank | 111805300 | 7490534157064344074 | true
Sugary | 112259022 | 7491984099733672485 | true
Sugary-Dreams-Italic | 111804589 | 7490531151350600219 | true
Thinker-Alt1 | 111804584 | 7490531314752295450 | true
Ugly-Dave-Alternates | 111804564 | 7490531414392181258 | true
Vogue | 112258561 | 7491983297870828058 | true
ZY Amity | 34200643 | 7311977316970664449 | true
ZY Balloonbillow | 55106512 | 7353574360667394561 | true
ZY Blossom | 30910322 | 7304640684311450113 | true
ZY Brief | 34200651 | 7311977774799917570 | true
ZY Classical | 34200639 | 7311977840574992897 | true
ZY Concise | 37544776 | 7317175365288333826 | true
ZY Coruscant | 30000836 | 7302355236243378689 | true
ZY Courage | 30910326 | 7304640798488793602 | true
ZY Daisy | 30000858 | 7302355415038169601 | true
ZY Dots Art | 80464454 | 7407288650473411088 | true
ZY Elegant-Black | 40250742 | 7324166053649453570 | true
ZY Elixir | 30000844 | 7302355533313348097 | true
ZY Fabulous | 30000832 | 7302355634538680833 | true
ZY Fantasy | 53177510 | 7350189137770582529 | true
ZY Flexible | 38698722 | 7320169752465248769 | true
ZY Flourishing-Italic | 43287756 | 7330606083335000577 | true
ZY Fortitude | 43041469 | 7330160852353421825 | true
ZY Genial | 49626244 | 7343835314105881090 | true
ZY Harmony | 34200663 | 7311977407244669441 | true
ZY Ingenious | 44370268 | 7332772999801606657 | true
ZY Kindly Breeze | 80464440 | 7407289076090409489 | true
ZY Loose | 34200631 | 7311977919948001793 | true
ZY Loyalty | 66322554 | 7371704099433091600 | true
ZY Majestic | 39631829 | 7322744435404444161 | true
ZY Modern | 51844020 | 7347670651626328577 | true
ZY Multiplicity | 66322523 | 7371704261878485521 | true
ZY Pace | 34200623 | 7311978000008876546 | true
ZY Panacea | 30000850 | 7302355742936273410 | true
ZY Relax | 34200615 | 7311977487469122049 | true
ZY Rhythm | 34200633 | 7311978076647199233 | true
ZY Slender | 34200655 | 7311977578821063170 | true
ZY Spunk | 30910324 | 7304640886703395329 | true
ZY Squiggle | 66322535 | 7371704357009494529 | true
ZY Starry | 31942077 | 7304640983893807618 | true
ZY Steady | 48055822 | 7340237950094938625 | true
ZY Tactful | 49626266 | 7343835205418881537 | true
ZY Timing | 30910320 | 7304641084833927682 | true
ZY Trend | 51844010 | 7347670845185069569 | true
ZY Upright | 76415424 | 7394802257847390737 | true
ZY Vigour | 48332840 | 7340906771109646849 | true
ZY Vision | 48332846 | 7340906978828358145 | true
ZYLAA Demure | 35459490 | 7313895257991549442 | true
ZYLAA Flechazo | 35459194 | 7313895610061427201 | true
ZYLAA Gambol | 35459480 | 7313895522496942593 | true
ZYLAA Infinity | 35459464 | 7313895149266801153 | true
ZYLAA Serein | 35459448 | 7313895348269748738 | true
ZYLAA lavender | 35459252 | 7313895433011466754 | true
一笔壹画加油体 | 74697345 | 7390218575979483659 | true
一笔壹画潮黑体 | 74696981 | 7390218461990883876 | true
三极云隶体中 | 34549534 | 7312720330986885642 | true
三极力量体简-粗 | 79942352 | 7405555944769196595 | true
三极古拙楷书 | 81318534 | 7410300778998403610 | true
三极妙漫体 | 79942353 | 7405556011081142822 | true
三极宋黑体超粗 | 34549526 | 7312720224510284326 | true
三极拙墨体 | 79942349 | 7405556255906861605 | true
三极拙隶简体 | 34549528 | 7312720520011584038 | true
三极极宋超粗 | 112957135 | 7494187329054052901 | true
三极榜楷简体 | 81318537 | 7410300778990015027 | true
三极欢乐体 | 79942350 | 7405555876368486939 | true
三极正雅黑粗 | 34549517 | 7312720421177004571 | true
三极气泡体 | 79942351 | 7405556128832033317 | true
三极泼墨体 | 79942347 | 7405556071848219186 | true
三极活力黑简体 粗 | 81318539 | 7410300778994209307 | true
三极浓密仙粗 | 34549529 | 7312720141865718282 | true
三极湘乡体 | 81318538 | 7410300778994209289 | true
三极纯真体粗 | 34549518 | 7312719708283736627 | true
三极罗丽黑简体-粗 | 81318535 | 7410300778994209290 | true
三极萌喵简体 | 81318536 | 7410300778994225674 | true
三极行楷简体-粗 | 79942348 | 7405556194279952905 | true
三极铿锵体 | 34549521 | 7312720059191792154 | true
三极黑宋体中粗 | 34549520 | 7312719852194501158 | true
云书法三行魏碑体 | 36880893 | 7316822178538721830 | true
云书法手书建刚静心楷简 | 36880886 | 7316823183905002010 | true
云书法生如夏花简 | 36880894 | 7316822784103944713 | true
云书法罗西硬笔楷书体 | 36880892 | 7316819473019703859 | true
云书法萨瓦迪卡简 | 36880889 | 7316821586038755877 | true
亦然体 | 26003134 | 7290457372814742073 | true
仓耳丝柔体 | 85757836 | 7423616269384946186 | true
仓耳丰黑 | 85757844 | 7423616269397545499 | true
仓耳体 | 85757842 | 7423616268759994890 | true
仓耳力士 | 85757837 | 7423616269326225946 | true
仓耳明黑 | 85757841 | 7423616269552718345 | true
仓耳曙黑 | 85757840 | 7423616268755800603 | true
仓耳榜黑 | 85757838 | 7423616269313643035 | true
仓耳状元楷 | 85757849 | 7423616268764189222 | true
仓耳视频体 | 85757847 | 7423616269338808841 | true
仓耳趣黑 | 85757839 | 7423616269397529115 | true
仓耳酷黑 | 85757853 | 7423616268759994930 | true
优设书华体 | 91065725 | 7438524730103042599 | true
优设字由棒棒体 | 34131538 | 7311914390259765811 | true
优设字美体 | 91065726 | 7438524940153786934 | true
优设招牌体 | 91065727 | 7438524840576815627 | true
修羽体 | 26003131 | 7290456770160366139 | true
凌丝体 | 26003145 | 7290455877864133157 | true
利飞体 | 85757848 | 7423616268764189193 | true
剪映专辑 | 107789541 | 7479022906626806298 | true
剪映云迹 | 115815828 | 7502335387969262130 | true
剪映半山海 | 113931114 | 7497171321915183625 | true
剪映印章 | 114520924 | 7499001991096439347 | true
剪映团子 | 113096610 | 7494617559677800970 | true
剪映圆隶 | 113927430 | 7497162943239295539 | true
剪映手书 | 110450154 | 7486448265496367625 | true
剪映新年体 | 102584862 | 7463380715107783206 | true
剪映春日部 | 108780445 | 7481618551309079077 | true
剪映狗爬体 | 110206413 | 7485673940988203558 | true
剪映细毛笔 | 115825070 | 7502351067770786341 | true
剪映香蕉 | 113927966 | 7497163735652373018 | true
励字俊林简 | 36825422 | 7316745865731772955 | true
励字勇敢黑简 大黑 | 36880884 | 7316817704143295003 | true
励字大黑简繁 | 36825420 | 7316745335257174578 | true
励字姚体简繁 | 36880881 | 7316817407664722441 | true
励字小怪兽简 | 36825428 | 7316747164716110345 | true
励字志向黑简 特粗 | 36880880 | 7316819223840297481 | true
励字憨憨简 | 36825429 | 7316745679055884837 | true
励字敲可爱简 中粗 | 36825430 | 7316746541820023306 | true
励字星宜简 | 36825423 | 7316747352956473882 | true
励字玉树临风简 | 36880878 | 7316818084935766565 | true
励字行楷简繁 | 36880877 | 7316817018030658075 | true
励字趣石简 | 36825427 | 7316746949489594931 | true
励字趣黑简繁 | 36825424 | 7316746727430558234 | true
励字逆反差圆舞简 超级黑 | 36825426 | 7316746365185298981 | true
励字造梦简 特粗 | 36880891 | 7316818766493389339 | true
励字隶书简繁 | 36825425 | 7316746076373914139 | true
华书体 | 26003140 | 7290455554504266298 | true
听露体 | 26003132 | 7290456595102700089 | true
唧唧国王 | 34549532 | 7312719555653014053 | true
壮楷体 | 93697432 | 7441547528874496539 | true
妙如体 | 26003137 | 7290456177559736889 | true
字由爱驾公路体 | 34131532 | 7311912714970862107 | true
字语云黑宋 | 34549538 | 7312719287796371978 | true
字语俊言体 | 113453150 | 7495685759022666278 | true
字语叙黑体 | 113448754 | 7495677959626297907 | true
字语叙黑体-中粗 | 113443244 | 7495667671212495386 | true
字语叙黑体-常规 | 113449404 | 7495679051764339251 | true
字语叙黑体-粗体 | 113448362 | 7495676881946022451 | true
字语叙黑体-细体 | 113449788 | 7495679735909847589 | true
字语叙黑体-超粗 | 113442102 | 7495661432017523250 | true
字语古兰体 | 34549527 | 7312718551096234523 | true
字语古映体 | 113453641 | 7495686582133854730 | true
字语咏宋体 | 34549533 | 7312719367769166386 | true
字语咏宏体 | 34549522 | 7312719426845938203 | true
字语咏楷体 | 34549530 | 7312719210373714459 | true
字语嘟嘟体 | 34549523 | 7312718329347576347 | true
字语圆体 | 113454943 | 7495689259223880202 | true
字语康宋体 | 113436253 | 7495657467548799515 | true
字语康宋体繁体 | 113456064 | 7495691210900640293 | true
字语文乐体 | 113452362 | 7495684286788407818 | true
字语文乐体-粗体 | 113452063 | 7495683757769232906 | true
字语文乐体-细体 | 113452597 | 7495684762376344091 | true
字语文刻体 | 113451682 | 7495683056359969306 | true
字语文熙体 | 113452995 | 7495685451823452723 | true
字语文酷体 | 34549524 | 7312718751328113162 | true
字语文雅体 | 34549525 | 7312718961991225894 | true
字语文韬体 | 34549539 | 7312718857334952498 | true
字语文韵体 | 34549537 | 7312719046229627402 | true
字语漫雅手书 | 113453534 | 7495686373119103526 | true
字语萌酱体 | 113455471 | 7495690155840246298 | true
字语软糖体 | 34549535 | 7312718629982704166 | true
字语颖黑体 | 34549516 | 7312719121404138021 | true
宜宋 | 85757843 | 7423616269825348122 | true
小可爱体 | 85757845 | 7423616269267505691 | true
少年南波万 | 93697433 | 7441547528870302258 | true
山雁体 | 26003150 | 7290456514370736698 | true
幽梦体 | 26003126 | 7290457477873668666 | true
归雁体 | 26003136 | 7290455353756488247 | true
怜秋体 | 26003139 | 7290455783932695100 | true
承英体 | 26003146 | 7290455103704666679 | true
星汉宋 | 85757834 | 7423616268764189211 | true
景曜体 | 26003133 | 7290455645264810555 | true
月亮供电不足 | 34549519 | 7312720704959418930 | true
未光体 | 26003147 | 7290456683027894839 | true
毛体行楷 | 98548489 | 7452649447441306121 | true
毛体行草 | 98548450 | 7452649545395081755 | true
汉字之美棒棒糖粗简 | 36795730 | 7316732709747823114 | true
汉字之美玉龙简 | 36825421 | 7316745091178041865 | true
汉字之美郝刚牡丹体简 | 36880888 | 7316816467062690330 | true
流苏体 | 26003142 | 7290455967735484987 | true
游乐体 | 26003128 | 7290457554574905914 | true
点字佳楷 | 34131531 | 7311912796520714779 | true
点字奇巧 | 34131533 | 7311913943188902427 | true
点字小隶书 | 34131539 | 7311914134109426203 | true
点字玄真宋 | 34131530 | 7311914225767551498 | true
点字王者风范 | 34131529 | 7311914033571959333 | true
点字艺圆 | 34131536 | 7311914298060575283 | true
点字青花楷 | 34131534 | 7311913734081876506 | true
点字青花隶 | 34131535 | 7311913858942112306 | true
烟客体 | 26003138 | 7290457082921226811 | true
爱你是无解命题 | 34131537 | 7311911945655816730 | true
爱民小楷 | 85757851 | 7423616268760011314 | true
玄鸟体 | 26003129 | 7290456889668670013 | true
知新体 | 85757852 | 7423616268952932902 | true
章鱼小丸子 | 85757850 | 7423616269254922762 | true
竹言体 | 85757835 | 7423616269850513947 | true
花锦体 | 26003144 | 7290455460186952251 | true
莫雪体 | 26003143 | 7290456347177390629 | true
蕴行体 | 93697435 | 7441547528878690867 | true
造字侠今朝醉简 | 36880876 | 7316824086712160806 | true
造字侠寻味江湖简 | 36880883 | 7316824437930594867 | true
造字侠昊仔简繁 | 36880885 | 7316823873930924582 | true
造字侠永刚漆书简繁 | 36880882 | 7316824945592373770 | true
造字侠陈坤风行简繁 | 36880887 | 7316823545399480841 | true
锋舞九天 | 85757854 | 7423616268764205595 | true
阳华体 | 26003127 | 7290457161887388219 | true
阳煦体 | 26003130 | 7290457267030200869 | true
雅月体 | 85757855 | 7423616268764189234 | true
雅韵体 | 26003135 | 7290456990571041340 | true
青印体 | 26003149 | 7290456429276697149 | true
青春加糖体 | 93697434 | 7441547528874496538 | true
青禾体 | 85757846 | 7423616269275894310 | true
青鸟华光中长宋 | 81332681 | 7410326723805319706 | true
青鸟华光书宋2 | 81332684 | 7410326723780153893 | true
青鸟华光仿宋2 | 81332685 | 7410326723327185435 | true
青鸟华光大标宋 | 81332679 | 7410326723322974746 | true
青鸟华光报宋2 | 81332677 | 7410326723314586149 | true
青鸟华光标题黑 | 81332682 | 7410326723318780467 | true
青鸟华光楷体2 | 81332676 | 7410326723318780453 | true
青鸟华光粗黑 | 81332680 | 7410326723327169051 | true
青鸟华光细黑 | 81332678 | 7410326723792736795 | true
青鸟华光细黑1 | 81332673 | 7410326723796931109 | true
青鸟华光美黑 | 81332683 | 7410326723327169034 | true
青鸟华光黑体 | 81332674 | 7410326723331363337 | true
青鸟华光黑变 | 81332672 | 7410326723322991154 | true
飞鸟集 | 4010301 | 7130643143719916069 | true
高字标志圆 | 34549540 | 7312720780599497225 | true
鱼太闲躺平体 | 34549531 | 7312720611694875162 | true
鸣翠体 | 26003148 | 7290456267212984889 | true
鹿鸣体 | 26003141 | 7290456058328257084 | true
黑糖体 | 1600490 | 7070430083919385119 | true
```


---

## 附录 B 花字清单（1673 条）

- 挂载位置：materials.texts[*].content.styles[*].effectStyle.id + materials.effects[type=text_effect]
- 草稿实际使用编号：huazi_id；在当前仓库里它等于 effect_id 和 resource_id
- 免费 94 条，VIP 1579 条
```text
title | huazi_id | is_vip
红黄火焰综艺花字 | 7539407429763796249 | true
综艺-黑暗斑驳红色 | 7351316503771368713 | true
蓝白色立体综艺描边花字 | 7403923146862087424 | true
花字 | 7527336771223407934 | true
黄字橙光花字 | 7506878563723840783 | true
综艺-我看看 太夸张了吧!! | 7351314020114124068 | true
黑色描边花字 | 7404884940837473590 | true
音乐节-超粗描边 | 7272728092529986827 | true
潮酷橙底黄色渐变立体花字 | 7160594825933262087 | true
美食-肉 | 7212892794778668345 | true
蓝白渐变立体花字 | 7405155739943079178 | true
橙黄色描边立体花字 | 7477040473454939454 | true
动感黄色发光故障风花字 | 7406159958045232435 | true
渐变黄红色发光字 | 7404758577623289123 | true
黄色渐变红描边发光字 | 7403930784630967604 | true
火焰燃烧花字 | 7371391474404986150 | true
618立体 | 7508541988401368345 | true
花字 | 7545767280450227481 | true
渐变黄色立体描边花字 | 7404010442118515994 | true
金箔纹理字 | 7546806821701504281 | true
蓝色质感渐变立体 | 7406646972330953994 | true
蓝字黄背景字 | 7431415454515612963 | true
白色蓝边立体花字 | 7403728277036125449 | true
黄色渐变描边花字 | 7404668885196131603 | true
黄色花字 | 7508204538659310872 | true
白色纹理花字 | 7405520166701813018 | true
蓝色冰块立体花字 | 7371423297289866505 | true
黄红色渐变立体花字 | 7477792820707757336 | true
黄橙渐变立体秋日花字 | 7533685266033347902 | true
红金立体发光花字 | 7548286146946616600 | true
花字 | 7430745422412549385 | true
蓝色渐变花光字 | 7406860981114015014 | true
黄色立体字（秋天） | 7405788077832080659 | true
裂缝纹理投影 | 7450158325188070668 | true
元旦新年氛围金色闪粉发光花字 | 7441868112556739849 | true
红黄描边立体 | 7479056232117062937 | true
金色发光镂空花字 | 7406015916380605733 | true
运动教程-花字 | 7311259207590776075 | true
综艺风红色渐变纹理立体花字 | 7478970969026022680 | true
蓝色立体描边文字 | 7406221865171111208 | true
25元旦-晕染红描边 | 7447932873845247286 | true
蓝色蜡笔纹理立体花字 | 7404700591949204799 | true
粉笔拼贴花字（教师节） | 7403915995569474870 | true
黄色渐变粉蓝描边立体花字 | 7523881114054970648 | true
蓝色花字 | 7480494571168795966 | true
轻复古 | 7350889130865265970 | true
综艺 红色渐变 | 7127681027346058503 | true
蓝白霓虹灯镂空效果发光花字 | 7404140347892305202 | true
黄色立体描边多彩花字 | 7404837954532789523 | true
黄字彩色多层投影文字 | 7406655431940033792 | true
红色紫色渐变立体描边花字 | 7506824081531243801 | true
黄色渐变立体花字 | 7347907413363789094 | true
美食-发光白 | 7212896770370571557 | true
复古橙黄渐变醒目 | 7400711954731371786 | true
冬至立体 | 7430861390933413130 | true
黑底白色立体花字 | 7278242937488690493 | true
金边浮雕文字 | 7405521516131093795 | true
橘黄色渐变温柔发光花字 | 7467426470714051902 | true
蓝色闪粉星光闪闪发光划走 | 7496504150797274393 | true
上下错落发光花字 | 7368866329337580851 | true
蓝色立体 | 7362931435809901859 | true
蓝字白边蓝光花字 | 7231501825311116577 | true
岩石花字 | 7477883005953051928 | true
618-红紫渐变 | 7375227839542480191 | true
简约黄蓝方块综艺花字 | 7494576393569733913 | true
红色 | 7511243674546867518 | true
运动教程-花字 | 7311259516392197439 | true
3D蓝字黄边立体综艺花字 | 7404134454844788018 | true
黄色渐变纹理粉蓝立体花字 | 7485579082764225817 | true
JP冬日-结霜字 | 7303813440127126836 | true
红粉渐变花字 | 7405872381320842515 | true
紫色阴森情绪发光花字 | 7406170424935058726 | true
黄底字 | 7343614179732966691 | true
黄色渐变立体花字 | 7298566943722851594 | true
红黄渐变背景花字 | 7404440675225292083 | true
渐变黄字红边星光立体花字 | 7404352881861659931 | true
黄紫撞色复古立体字 | 7405221368561700148 | true
霓虹灯花字 | 7404008412607958323 | true
红色渐变白霜立体花字 | 7308367002253544741 | true
红色复古投影字 | 7405906746461424930 | true
像素化花字 | 7488151895048211736 | true
蓝橙色立体花字 | 7492933140210666776 | true
拼贴多色 | 7360526293596671273 | true
黄蓝紫渐变立体花字 | 7546405848860511513 | true
复古红色发光立体花字 | 7160599091750161671 | true
综艺红黄立体 | 7434585603439742218 | true
综艺-巅峰 厉害!!真是太火爆了!!!2 | 7351319129124506930 | true
黄红蓝边立体花字 | 7525867881331215640 | true
复古黄色立体 | 7406970077368618274 | true
黄蓝立体字 | 7431490038736702760 | true
花字 | 7533790251915955518 | true
黄色霓虹灯发光花字 | 7408956728529751333 | true
花字 | 7532883085390548286 | true
黄色马卡龙 | 7509743284898794777 | true
撞色描边立体字 | 7406334288930557218 | true
游戏像素文字效果花字 | 7405871504769961254 | true
粉色立体字 | 7475271686095506712 | true
霓虹灯花字 | 7330423055900069155 | true
黄色红色 | 7389147072064179506 | true
红樱桃 | 7539187400808123672 | true
粉紫描边立体 | 7474511004676803902 | true
花字 | 7495665652816956697 | true
渐变黄色中秋圆底花字 | 7405070516706381092 | true
复古背景字 | 7430809868333780259 | true
蓝紫色粗体描边花字 | 7259922491185958203 | true
黄绿发光字 | 7403962881252805903 | true
粉蓝色渐变立体发光花字 | 7366086107366182153 | true
花字 | 7525463353603640601 | true
粉色描边白色字 | 7474605929825193240 | true
穿搭立体 | 7536671491740634392 | true
好物美妆-黄白跳色 | 7264547410817387795 | true
绿色东南亚 | 7411032759457631515 | true
蓝色纸纹纹理花字 | 7520663448003415358 | true
红黄渐变发光字 | 7406976068789210403 | true
粉色星空花字 | 7396798321739730226 | true
粉色立体字 | 7404321887817452800 | true
金属划痕暗黑立体字 | 7405501393248881960 | true
粉色 | 7507145578984361241 | true
橘黄色立体字 | 7407078807309503744 | true
双色爱心花字 | 7362054905256758591 | true
三花猫配色 | 7532428202199797016 | true
绿色立体花字 | 7477511783801163032 | true
高级幻彩花紫字 | 7293329973694172435 | true
红绿撞色发光字 | 7406650793631223075 | true
绿色发光花字 | 7265723229216525620 | true
绿色渐变背景字 | 7404290078723312931 | true
蓝绿纹理花字 | 7527597707930799422 | true
粉色立体渐变 | 7376607395046231331 | true
黄色立体花字 | 7405087980685167922 | true
花字 | 7478268728992419096 | true
#花字招募令 彩虹花字 | 7398456039634406666 | true
少女粉星星花字 | 7404459246961577257 | true
未来科技感发光花字 | 7404471553607421222 | true
潮流紫色荧光花字 | 7241759007952735491 | true
橙色渐变花字 | 7404263174230297882 | true
可爱花字 | 7430667459683831079 | true
渐变综艺发光花字 | 7539752808367574297 | true
橙色万圣花字 | 7293140122332122368 | true
棕色立体粗描边 | 7406388990837886234 | true
立体字 | 7260043007997562149 | true
酸性质感花字 | 7481664682638560537 | true
绿色渐变立体花字 | 7492430244570303806 | true
赛博朋克风故障字 | 7404304312135896360 | true
粉色立体花字 | 7404522256929459494 | true
粉橙立体花字 | 7475398432807521561 | true
复古牛皮纸花字 | 7362833837627378944 | true
黑色纹理立体花字 | 7306894668795612442 | true
圆环花字 | 7349078136480386345 | true
薰衣草 | 7509044952912055614 | true
清新条纹投影纹理花字 | 7404757226583362854 | true
马卡龙色渐变文字 | 7406238235141213440 | true
白字红光花字 | 7351431205692181786 | true
纹理花字 | 7333249201419160868 | true
描边橙色黄色双色立体花字 | 7405049138867424523 | true
粉色渐变 | 7491540791689530686 | true
黄粉色立体渐变花字 | 7371110382393494793 | true
低饱和紫色渐变综艺花字 | 7388017781117160745 | true
莫兰迪清新蓝色描边花字 | 7404083693003853096 | true
节日花字 | 7405888865132711220 | true
3D多层渐变红 | 7174401031399312670 | true
红色 | 7389185223600114995 | true
多色渐变花字 | 7405856965332585764 | true
3D腮绿 | 7173927171881323789 | true
黄色渐变纹理花字 | 7431429108791266611 | true
黄绿色立体纹理花字 | 7404772432323546422 | true
白字橘色描边立体花字 | 7371117571757641011 | true
蓝色纹理白描边花字 | 7378313478852906280 | true
桃红色渐变立体花字 | 7388024664980770060 | true
潮酷粉黄撞色立体花字 | 7404058441481866511 | true
复古镂空花字 | 7345391635267603753 | true
粉黄渐变立体字 | 7405944611430092066 | true
绿橙花字 | 7392196588426382629 | true
中式背景框文字 | 7406225575712443663 | true
彩色花边花字 | 7366911458824752410 | true
节日粉色渐变立体描边花字 | 7539491294188440857 | true
黄绿综艺花字 | 7476505479364201753 | true
抹茶绿多层描边立体花字 | 7405039371037986089 | true
粉紫色渐变立体发光花字 | 7407013513979251978 | true
红粉色渐变立体发光花字 | 7475276656626863385 | true
花字 | 7543043727103675673 | true
粉色亮晶晶花字 | 7265614497119735040 | true
樱花粉 粉色花字 | 7336859597287804169 | true
蓝绿立体花字 | 7405924713400126747 | true
万圣紫色花字 | 7293778917603822848 | true
3D粉色立体花字 | 7350157127207456037 | true
粉蓝色渐变爱心底花字 | 7542084187285703998 | true
五一立体 | 7359406447718862131 | true
粉色紫边立体字 | 7409954407321783586 | true
立体黄蓝纹理花字 | 7537970908221394238 | true
3D粉色渐变立体花字 | 7403948957547760906 | true
浅蓝黄渐变立体花字 | 7312845270671232294 | true
复古红色立体花字 | 7480506672746794264 | true
绿色花字 | 7431433243922107689 | true
美妆纹理 | 7411406288350874917 | true
黄绿花字 | 7404294636656774451 | true
糖果色彩色渐变描边花字 | 7404705863442713910 | true
粉色立体花字 | 7298637894481169701 | true
蓝色渐变花字 | 7252284645998464288 | true
纹理花字 | 7339054041458036006 | true
纹理复古深色字 | 7404307108625206563 | true
红色描边黄色花字 | 7404774919315197195 | true
白字黑边裂痕综艺花字 | 7404884426150235418 | true
黄字红边立体粗描边花字 | 7404394775664708901 | true
国风水墨 | 7405990788053683482 | true
火焰立体 | 7407352720815836443 | true
红色描边纹理立体字 | 7405218557342059816 | true
蓝色渐变阴影立体花字 | 7495216846946274584 | true
红色立体纹理花字 | 7405838293843070234 | true
渐变花字 | 7368685720325655817 | true
纸质 | 7360556929959087397 | true
蓝白色渐变立体花字 | 7404520330502458674 | true
花字 | 7547970729258519833 | true
蓝色 | 7507097456283274520 | true
黑白线条花字 | 7404819849140063551 | true
愚人节立体 | 7482688482754694462 | true
中秋桂花花字 | 7406740764207713577 | true
花字 | 7455608333563874585 | true
双十一红黄立体 | 7430822256806284594 | true
金色渐变立体红边发光花字 | 7459686003079630104 | true
银色渐变描边发光花字 | 7405031205877419305 | true
白色立体花字 | 7474543369054702910 | true
蓝色渐变镂空描边花字 | 7405927551417306378 | true
蓝白立体花字 | 7405716848106310931 | true
白色发光花字 | 7371368226606943514 | true
金红纸纹理发光字 | 7404877070158908698 | true
橙白渐变花字 黑白描边花字 | 7241953374780804410 | true
云纹金箔字 | 7405518341814668544 | true
综艺风黄色渐变纹理立体花字 | 7478934394141527358 | true
蓝红色立体综艺花字 | 7371410942061546803 | true
红金国风花字 | 7507460201549843736 | true
黄色渐变描边立体花字 | 7404667171537767699 | true
白纸纹理蓝阴影花字 | 7509041829556522265 | true
国风花字 | 7406648659976260903 | true
黑色拼贴方底花字 | 7405933257776172314 | true
描边字 | 7360986749046213928 | true
花字 | 7465177921276136766 | true
点金花字 | 7406200724171787574 | true
白字内发光蓝边字 | 7406693646592003366 | true
米白厚底立体花字 | 7371351770045484338 | true
水墨红底白色花字 | 7405529606859607347 | true
条纹纹理黄色立体花字 | 7404709465209064745 | true
红色恐怖氛围纹理花字 | 7404872280662166834 | true
蓝色折纸 | 7459675119116373272 | true
港风立体 | 7434560086166490418 | true
红色发光花字 | 7431445423283244297 | true
黄色渐变立体字 | 7404696990510042402 | true
蓝莓奶酪 | 7506829483878649150 | true
新年立体花字 | 7451570972550991166 | true
花字 | 7430745414313332006 | true
25元旦-红花背景花字 | 7447831886874938678 | true
黑色金箔描边立体花字 | 7404523157400472869 | true
灰白水墨国风花字 | 7405537335850306853 | true
科技感朋克发光立体标题花字 | 7405801186286259466 | true
田字格图案蜡笔纹理花字 | 7405067510053211446 | true
黄红撞色立体 | 7406637506977877299 | true
中式背景文字 | 7405203982286720256 | true
日综蓝白方框字 | 7472013339640614206 | true
综艺蓝黄立体 | 7436409520848522546 | true
水墨风白字黑边红墨点花字 | 7405514240779357449 | true
创意立体黄色花字高级感主题文字封面标题字 | 7507075178447359282 | true
白色 | 7509055757908806937 | true
黄字黑边 | 7406683118108806437 | true
大理石花纹字 | 7411036229677878554 | true
中秋黄色字 | 7404409329991879988 | true
综艺感黄色立体描边花字 | 7481983816001834265 | true
月饼花字 | 7548895672402185497 | true
蓝色渐变微立体花字 | 7406980293233560859 | true
白字橘色发光花字 | 7371372494336396570 | true
几何纹理黑色阴影花字 | 7404700217553063209 | true
悬疑剧字幕 | 7411046109285485861 | true
蓝色纹理花字 | 7479073211918044441 | true
划重点花字 | 7369127125569342731 | true
橙色底纹花字 | 7533453859830713662 | true
雪花图案渐变蓝色立体花字 | 7405034038135655719 | true
蓝色渐变描边简约风格花字 | 7455983000291937586 | true
黄色渐变橘色阴影立体花字 | 7495033287438781758 | true
双十一-立体紫色 | 7296357486490144036 | true
黄色贴纸描边字效 | 7533293069123390744 | true
渐变蓝色阴影 | 7283715592316554555 | true
黑白水墨花字 | 7405536862133046565 | true
复古黄沙水彩纹理花字 | 7405517504128273676 | true
红色渐变 | 7461550488073538841 | true
潮酷背景字 | 7431460080228257039 | true
撞色描边字 | 7404391553164135715 | true
紫色立体花字 | 7406690026009972004 | true
冬季渐变蓝色立体花字 | 7431012567369125161 | true
红黄复古浮雕纹理字 | 7405414031072169250 | true
3D渐变橘红色立体花字 | 7404702615671508263 | true
粉蓝渐变花字 | 7404522414941424923 | true
花字 | 7511273485730237758 | true
花字 | 7491617722359565630 | true
黑紫星空花字 | 7405795232748490025 | true
冷色调简单花字 | 7430642926293732658 | true
金色渐变立体花字 | 7371420451526020389 | true
红色金箔纹理立体花字 | 7404507481205984539 | true
黄蓝撞色纹理立体花字 | 7405570848041487666 | true
花字 | 7365356770652376330 | true
渐变圆底花字 | 7406353145938382130 | true
白字蓝粉相间底色花字 | 7444510136296541465 | true
综艺风黄色立体描边花字 | 7505458612001852697 | true
蓝色纸张质感立体花字 | 7430855417703435529 | true
彩色带图案花字 | 7407037141584203059 | true
红蓝橙描边立体花字 | 7481302843849329982 | true
红色印章花字 | 7407464175347272998 | true
五一立体 | 7493107948286250302 | true
淡黄色渐变发光花字 | 7371414308770647346 | true
白色方底拼贴花字 | 7405931282632412442 | true
红金立体国风花字 | 7548337425781935422 | true
暗黑金泼墨风花字 | 7405492993878281510 | true
花字 | 7545366362924043582 | true
红色描边花字 | 7442261279013604644 | true
金色渐变立体花字 | 7506868020917226777 | true
橙色立体花字 | 7405152529522101531 | true
红色锈迹文字 | 7412523765768178944 | true
紫色渐变 | 7398455661513674035 | true
黄色 | 7398454655505763593 | true
黑色渐变白蓝描边 | 7406687421921791282 | true
端午61立体字效 | 7506872589642665240 | true
黄色立体文字 | 7405120470477065507 | true
花字 | 7431452163181792524 | true
炫彩模糊花字 | 7236984607575461154 | true
五四青年立体 | 7494656119529393470 | true
复古方底立体 | 7406389812925680933 | true
喜庆花字 | 7467033569848839486 | true
中秋黄白立体字效 | 7546585357555649816 | true
黄蓝色立体综艺描边花字 | 7403927160563551528 | true
白紫色立体花字 | 7405229843220106534 | true
金色渐变立体发光花字 | 7372363920864005386 | true
花字 | 7547731905500794174 | true
蓝色描边立体花字 | 7471910410766109977 | true
黄色白色 | 7505771535878098200 | true
渐变色白边立体花字 | 7406364344176414003 | true
橘猫花字 | 7403728040653573387 | true
综艺字立体 | 7409333268195101979 | true
红橘新年花字 | 7455529495043525950 | true
红包花字 | 7449034603760749839 | true
花字 经典黄色加深蓝经典配色凸显文字 | 7231489008126266679 | true
橙色花字 | 7519880279205448984 | true
淡蓝色渐变发光花字 | 7371415414817000754 | true
紫色双层描边花字 | 7406385391265156362 | true
新年红金花字 | 7455254263888104766 | true
晕染蓝 | 7357027100324367627 | true
黑色渐变立体花字 | 7431440010152316169 | true
拼贴绿 | 7360540744035142953 | true
橘黄色波点渐变发光花字 | 7404370982238014747 | true
红黄白多层渐变立体花字 | 7403764204420730122 | true
蓝色渐变 | 7364604452323495204 | true
黄绿高饱和多重描边字 | 7404415905066782004 | true
粉色发光花字 | 7400335293565455679 | true
简约雪纹理立体花字 | 7430397468082228543 | true
白字红边重影风格花字 | 7450496790354234674 | true
蓝色渐变 | 7385227292521418018 | true
粉蓝色渐变立体发光花字 | 7366060581410901286 | true
黄色奶酪字 | 7405831511003417871 | true
彩虹色描边白字 | 7406673678412418354 | true
橙黄色渐变立体花字 | 7406360821216988416 | true
蓝色纸张质感黄底花字 | 7430856547934211379 | true
花字 | 7533174868930645273 | true
粉色爱心立体字 | 7474476846223101209 | true
蓝色纹理立体描边花字 | 7406335734044577035 | true
拼贴浅红 | 7360960769703398695 | true
红色花字 | 7359358208286215464 | true
故障字 | 7347989608908606783 | true
橙色秋叶立体花字 | 7538998611628084542 | true
国庆黄红立体字效 | 7546423084874599705 | true
黄红渐变纹理花字 | 7548711671317974334 | true
黄橙玻璃质感秋日花字 | 7538711238725946649 | true
复古黄色方底背景 | 7406380674057358642 | true
花字 | 7539626317688425753 | true
花字 | 7548813025013419289 | true
花字 | 7540868241737141529 | true
立体桔黄 | 7546349045032439102 | true
花字 | 7538719944897236286 | true
618黑边 | 7509793945480613144 | true
综艺风红色立体描边花字 | 7508042807811280190 | true
高考立体 | 7509930498681163032 | true
糖炒栗子 | 7545871911138577726 | true
花字 | 7540131523937357118 | true
花字 | 7546127896943840536 | true
斜纹花字 | 7546131418620071192 | true
黄色渐变蓝色描边立体花字 | 7507853100984667416 | true
三原色 | 7527398816782454040 | true
糖炒栗子 | 7546032665510841662 | true
花字 | 7544777148205190425 | true
黄色纹理蓝棕色阴影描边立体花字 | 7511339634761420057 | true
橙色渐变立体花字 | 7533092158820142360 | true
立体花字 | 7532701961364278553 | true
毛绒字 | 7535694140227456280 | true
我的潮流指南 | 7506898516468370750 | true
蓝莓奶酪 | 7507101495339568446 | true
综艺风蓝色立体描边花字 | 7495312625169911065 | true
彩铅渐变黄色花字 | 7477620313522703678 | true
彩色 | 7474582555853901080 | true
膨胀感字 | 7480089681586130238 | true
花字 | 7492216396290542873 | true
花字 | 7507526398710435097 | true
花字 | 7482733632910675262 | true
蓝紫色混合花字 | 7236599551984028939 | true
蓝色 | 7481665617796369689 | true
彩铅渐变粉色花字 | 7477756249665342744 | true
渐变花字 | 7260020603044826427 | true
绿色花字发光 | 7506874577159572755 | true
可爱彩色涂鸦花字 | 7350563191123938611 | true
花字 | 7508005459065097497 | true
粉色闪闪芭比花字 | 7507082793592032536 | true
粉色渐变 | 7469677410414382398 | true
马卡龙 | 7509757725908225304 | true
发光字 | 7348369625215749388 | true
粉笔字 | 7403964791372533027 | true
蓝白 | 7508363172798270744 | true
黄绿渐变立体字 | 7477149973520583961 | true
花字 | 7495692617561181502 | true
多层描边彩色多巴胺花字 | 7494493486155042110 | true
蓝粉 | 7492310644704841022 | true
节日绿色立体描边花字 | 7507164704448679193 | true
蓝绿色花字 | 7347171058488823066 | true
粉色立体拼贴花字 | 7405934415567736074 | true
彩色描边立体可爱花字 | 7492411773329476889 | true
绿色立体 | 7492716248091004222 | true
花字 | 7471905506001669401 | true
春日综艺感渐变纹理花字 | 7479683834464898329 | true
绿紫黄紫立体字 | 7478608447794187582 | true
膨胀感字 | 7480097920361073945 | true
立体综艺花字 | 7403676308145802522 | false
白色纹理描边花字 | 7405202500493610275 | false
复古淡黄花字 | 7441152469352090889 | false
白色发光字 | 7405564299122429219 | false
黄色渐变立体白描边花字 | 7403679510702378278 | false
白字红边立体字 | 7403960732490157364 | false
蓝色立体字 | 7405107629137186082 | false
美拉德立体文字 | 7410649194110733602 | false
绿色立体通用花字 | 7404477237837270299 | false
绿色镂空透明文字 | 7405105991651544360 | false
绿色描边投影字 | 7405410790867586344 | false
绿色透明纹理花字 | 7405203773066415360 | false
综艺火焰 | 7543157780769803582 | true
系统故障字 | 7347967906669415716 | true
蓝色黄色渐变立体描边花字 | 7532041202787487038 | true
综艺 黄色 | 7127670164996328740 | true
黑白黄色花字 | 7260340249581128996 | true
红色火焰燃烧花字 | 7405896759987227931 | true
复古紫光蓝色渐变立体花字 | 7160595602236116232 | true
综艺风蓝色描边立体花字 | 7494932494253608216 | true
喷溅红立体 | 7411046111760125211 | true
红黄渐变纹理立体花字 | 7313160248175398154 | true
白字蓝框综艺花字 | 7403899942944705819 | true
美食-金色渐变 | 7205144150390443301 | true
红色火焰字 | 7406328633205312820 | true
镂空发光字 | 7404690754590821632 | true
蓝色纹理花字 | 7405902936175381787 | true
白色质感纹理立体花字 | 7310113812168871177 | true
黄色花字 | 7430781079058976026 | true
综艺立体 | 7448962185159609625 | true
五一复古立体 | 7494493305716378905 | true
好物美妆-双层投影 | 7264501278175202572 | true
白字绿底花字 | 7350578203905232166 | true
渐变错位花字 | 7406249723423640871 | true
彩色 | 7474546033763224894 | true
像素格背景字 | 7406866881144966409 | true
橙黄渐变花字 | 7404777689518738728 | true
彩色手绘线条花字 | 7342020000812731658 | true
立体麻布花纹字体 | 7262979013637967119 | true
红色渐变波点底纹立体花字 | 7406013385969569062 | true
综艺风蓝色渐变纹理立体花字 | 7478945314318241086 | true
高饱和彩虹字 | 7404293089377930536 | true
3D蓝红色立体综艺花字 | 7404132140365008179 | true
音乐节-杂点黄字 | 7272729157895769355 | true
拼贴位移字 | 7343806780583038247 | true
彩色立体底框花字 | 7347548073897364746 | true
综艺风蓝色立体描边花字 | 7495656020006669592 | true
黑字底红光 | 7230694221513035020 | true
海浪卡通立体字 | 7405947244395924770 | true
浪花紫 | 7261598257762045219 | true
裂纹立体文字 | 7405953030996184335 | true
漫画层叠花字 | 7406307881865301258 | true
节点营销直播主题立体字蓝色 | 7403686755486010634 | true
黑色立体投影紫色发光镭射纹理花字  艺术字体 | 7251715329162841347 | true
复古白蓝色立体花字 | 7405563025169632562 | true
爆款热卖 | 7430816571443940659 | true
蓝紫渐变多重投影字 | 7403937403397885184 | true
综艺白色立体描边纹理花字 | 7404868077101255988 | true
红金渐变国风立体花字 | 7547984081930161470 | true
立体字粉色背景 | 7409964157296020751 | true
金色渐变红底立体花字 | 7330165240576970021 | true
热销字体 | 7431487397017226507 | true
位移字 | 7343541738537061651 | true
美食-立体描边 | 7205148909730024762 | true
格子背景双色字 | 7404037981952068879 | true
落日鸡尾酒 | 7174051263578000678 | true
春节-半透明 | 7187622568717749565 | true
黑色综艺花字 | 7241429233287925044 | true
白/黄方块图案质感花字 | 7405060175322795276 | true
时尚黑蓝粉 | 7284906593399950647 | true
3D蓝色渐变综艺花字 | 7403911656587234597 | true
白色蓝色描边红色荧光花字 | 7241398402125253903 | true
白色仿3D立体花字 | 7371129776494365990 | true
蓝色立体描边花字 | 7406357450166635776 | true
破碎裂开文字 | 7404701167156088116 | true
黄边黑字立体花字 | 7270881305070423356 | true
立体星星花字 | 7405886722011172150 | true
多色花字 | 7405917295421263158 | true
立体方块花字 | 7481488244421741848 | true
水墨纹花字 | 7252151198805986572 | true
花字 | 7529442177953352985 | true
白字蓝底花字 | 7368858909295136010 | true
橙色纹理立体发光花字 | 7430724518248729919 | true
红黄绿复古花字 | 7407014154613116210 | true
橙黄色渐变立体描边花字 | 7404037530980453647 | true
潮酷薄膜纹理字 | 7404380953893735714 | true
粉色贝壳光泽花字 | 7265614510084443444 | true
四色蜡笔花字 | 7348679900477279507 | true
蓝色立体描边发光花字 | 7404828145255288075 | true
限时抢购 | 7510183639066627352 | true
游戏综艺风蓝色波点渐变花字 | 7404883759012597030 | true
紫色梦幻   白字紫底红醒目花字 | 7334687695660272947 | true
蓝色渐变综艺 | 7435551949266701580 | true
黑色粉色阴影花字 | 7289732660077874491 | true
黑体蓝紫边发光花字 | 7259399609452088637 | true
粉笔涂鸦花字（教师节） | 7405546666498985227 | true
可爱花字 | 7430667612146666764 | true
黑粉甜酷拼贴文字 | 7431814893415812362 | true
彩色立体 | 7506818824885390616 | true
浅棕色描边花字 | 7328771445960592640 | true
蓝红蜡笔质感纹理花字 | 7543482227871599896 | true
黄色渐变 | 7410369831503006988 | true
综艺风方块背景立体花字 | 7404072480870026534 | true
彩色花字 | 7252116303329217824 | true
综艺感蓝色立体描边花字 | 7482027387266469145 | true
彩色透明花字 | 7406321401969364264 | true
橙色蓝色花字 | 7369415539795529012 | true
黑字黄绿拼贴花字 | 7406010573961317670 | true
蓝橙白立体花字 | 7504864758944927001 | true
黄蓝撞色描边字 | 7435272797611429172 | true
玫粉黑花字 | 7407015583444782375 | true
芭比粉背景白字 | 7405183112906378522 | true
万圣节多色花字 | 7407047445240139071 | true
复古风花字 | 7406318872862674185 | true
深红白边黄影立体花字 | 7231502419723603239 | true
APT花字 | 7431429796434890021 | true
粉底黄边黑色立体花字 | 7270171712136776997 | true
未来科技感立体厚重标题花字 | 7405789476561095986 | true
白字带描边花字 | 7405944078992559411 | true
美妆方底 | 7411583332707863835 | true
酒红风格   黄字酒红底色花字 | 7337839774079798566 | true
多色花字 | 7406589254157061439 | true
黄绿撕纸拼贴质感花字 | 7405065396648283455 | true
橙黄色立体霓虹花字 | 7405186414284999971 | true
黄色渐变粉色花朵底纹立体花字 | 7544660134732057881 | true
青团底纹花字 | 7348639844198878515 | true
黄蓝渐变立体字 | 7382058294157774107 | true
紫色描边发光小字体 | 7252346023656394042 | true
粉蓝色渐变黑边立体花字 | 7404290790391860530 | true
红色渐变黄绿描边 | 7406979682911931657 | true
美妆拼贴 | 7411563961381817610 | true
游戏综艺风黄红紫渐变花字 | 7404883418774818086 | true
彩色花字 | 7430759634757061926 | true
蓝橙波点纹理玻璃质感立体花字 | 7543299507744967960 | true
蓝色纹理立体花字 | 7406011366865161481 | true
放射背景字 | 7404009350399937792 | true
白字黄绿拼贴花字 | 7406011150829194546 | true
夏日蓝描边立体 | 7548102481977593113 | true
白色国风水墨花字 | 7405537186436648201 | true
金箔纹理阴影花字 | 7405530102324415807 | true
书法墨迹白色花字 | 7405519026367122727 | true
泼墨书法纹理花字 | 7405512855434382611 | true
红色斑驳 | 7475566213477977368 | true
红色立体 | 7546579616576720152 | true
金色质感立体花字 | 7405499580399357210 | true
国风花字 | 7406643508242582825 | true
黑白水墨字 | 7405516433863511348 | true
复古红色立体花字 | 7435884430620691739 | true
国风花字 | 7406646658768882983 | true
水墨风晕染花字 | 7405497799036407090 | true
白金花字 | 7405510219633036555 | true
古风质感花字 | 7483351934074817817 | true
暗黑系红色火焰纹理花字 | 7405504415408409865 | true
红金国风花字 | 7405500731253411108 | true
点墨金银花字 | 7405517111231073575 | true
春节新年福字背景花字 | 7404078955344448777 | true
银色花字 | 7405512551879970067 | true
红色暗黑花字 | 7405501851887586611 | true
国风花字 | 7406643758231571766 | true
黑红渐变立体描边花字 | 7405506413524569363 | true
书法水痕阴影花字 | 7405527291209469196 | true
水墨背景白色花字 | 7405534702221790515 | true
国风金红花字 | 7405499186109533494 | true
红金国风花字 | 7507132514088062233 | true
黑白水墨花字 | 7405498270568418611 | true
暗黑红色立体花字 | 7405503477444644106 | true
暗黑墨迹字 | 7405513478645091636 | true
青绿色水墨风古典边框花字 | 7405879747340700937 | true
水墨书法纹理花字 | 7405514792724745484 | true
黑灰色质感立体花字 | 7405500890620120358 | true
暗黑火焰红边花字 | 7405494488019275059 | true
暗红色墨痕书法花字 | 7405528972135583030 | true
银色国风花字 | 7405504097429867815 | true
书法墨环图案花字 | 7405524745959034124 | false
金箔描边书法水墨花字 | 7405523665145613631 | false
综艺金色花字 | 7127823728267791647 | true
潮酷发光立体花字 | 7160598356237012261 | true
潮酷金色发光花字 | 7160595759375666446 | true
光芒万丈 | 7269602984844102947 | true
综艺立体花字 | 7160596923781598472 | true
美食-渐变小字 | 7205150731035266341 | true
金色渐变立体发光花字 | 7406007163417529638 | true
粉色花字 | 7127655008715296031 | true
粉色发光字 | 7403924857282432271 | true
蓝色发光 | 7346895765458947366 | true
元旦透明燥点花字-2022元旦 | 7179606734166592825 | true
红色渐变黄色发光花字 | 7406005354070379802 | true
蓝色霓虹灯发光花字 | 7408957503892884774 | true
黄色发光花字 | 7404896582182767908 | true
金色渐变立体发光花字 | 7459717947620363582 | true
蓝色发光花字 | 7404751791503576339 | true
圣诞红白条 | 7174330567222185253 | true
粉色花字 | 7127839722893774087 | true
潮酷白色发光立体花字 | 7160597532043644174 | true
综艺立体渐变 | 7160596088011951373 | true
黄色渐变花字 | 7273017604837625151 | true
发光 | 7346916622247955763 | true
闪光的新年花字-2022元旦 | 7179634097906519356 | true
红色渐变描边花字 | 7265622933702184232 | true
粉色发光 | 7362142403416952115 | true
霓虹灯黄红发光花字 | 7322482076958149914 | true
洒金粉花字-2022元旦 | 7179628047832730941 | true
元旦透明飘雪花字-2022元旦 | 7179616970399124795 | true
浅蓝色发光花字 | 7281951975275597114 | true
红色内发光文字 | 7405197593808096527 | true
克莱因蓝发光字体 | 7240995033393007931 | true
红黄配色花字 | 7403941808302066979 | true
红色发光花字 | 7128327279804976397 | true
黄色橙色描边花字 | 7241397134128352551 | true
霓虹灯发光红黄花字 | 7404014524900199706 | true
薄荷冰花字 | 7312709252928277812 | true
荧光绿炫酷字体 | 7241480073759575357 | true
渐变花字 | 7260439366953110825 | true
烟雾纹理花字 | 7245610210386136357 | true
红配蓝发光炫酷字体 | 7243255465822506255 | true
潮酷发光立体花字 | 7160595918226525453 | true
电商节日直播贴片标题立体字 | 7406289529096719625 | true
渐变 蓝紫色花字 | 7336848964819504434 | true
蓝色渐变花字 | 7241432857447583028 | true
黄色字荧光描边花字 | 7241389070943866164 | true
粉色渐变描边花字 | 7265621281838533923 | true
圆环发光花字 | 7322679348106906918 | true
绿色渐变描边花字 | 7265622422022262051 | true
白紫立体发光 | 7390410514976804122 | true
甜粉 | 7266447274115419449 | true
红色霓虹灯发光花字 | 7408956912089206067 | true
金色花字 | 7266696486363106616 | true
空心白色描边发光花字 | 7404503527617301770 | true
白字蓝光花字 | 7351422706086169866 | true
亮黄字橙色描边发光花字 | 7404047060221037851 | true
冬季发光 | 7434806614781168947 | true
黄的红边花字重叠 | 7231824394559982886 | true
渐变彩虹色发光花字 | 7405056348200684827 | true
霓虹灯发光花字 | 7322881735522290995 | true
绿色纹理立体花字 | 7391283375606156585 | true
红色霓虹灯发光字 | 7322678574719339802 | true
星空 | 7266724384205786427 | true
美食-中间渐变 | 7212896736849841467 | true
夏日的亮丽 | 7259709733790125366 | true
纯黑底色，荧光绿和黑色描边 立体 发光 花字 | 7274035971207744824 | true
黄色蓝色发发光花字 | 7241392284686683395 | true
梦幻蓝紫色简约渐变花字 | 7241477841567649080 | true
红色荧光花字 | 7241410291521670400 | true
彩色发光立体 | 7390315130128452890 | true
黄色渐变发光字 | 7404001083665812771 | true
发光灯箱感红色花字 | 6926827744189779207 | true
霓虹灯发光花字 | 7322422789355392265 | true
黑色红边柔光花字 | 7231468045976292645 | true
粉色渐变温柔发光花字 | 7404385123975613706 | true
渐变紫色花字 | 7241393396575735040 | true
红配绿发光拼色字体 | 7243262147210267944 | true
黑底荧光绿描边 发光 花字 | 7273831317136035133 | true
霓虹灯发光花字 | 7322380988430994715 | true
绿字蓝白描边荧光字 | 7403932533995425039 | true
粉色渐变双层立体发光花字 | 7494822504427539737 | true
东南亚渐变 | 7411034104415685939 | true
蓝色渐变花字 | 7241398727125011746 | true
黄红色霓虹灯镂空发光花字 | 7404089520070593843 | true
粉色渐变圆圈 | 7403922592194710834 | true
紫色发光花字 | 7248870704752397579 | true
粉色发光 | 7361004787967495462 | true
纯色黄色字体 | 7260373127249595687 | true
紫色发光字 | 7403992509212314920 | true
粉色闪粉星光闪闪发光划走 | 7496497861224516926 | true
绿底黑边黄色立体花字 | 7270129109974469945 | true
简约蓝 | 7264481843301354813 | true
花粉绿 | 7241230847741791521 | true
粉色发光立体花字 | 7404070348263607603 | true
绿色渐变立体描边花字 | 7406241968847670569 | true
粉色糖果风格花字 | 7291429737774255412 | true
紫色花字 | 7355608527144062217 | true
渐变发光花字 | 7238624559178485031 | true
荧光绿线条发光字 | 7405916937353465128 | true
渐变花字 | 7270718850256211259 | true
粉色发光花字 | 7274771737999379749 | true
粉色闪粉白色描边发光花字 | 7404388775264030003 | true
紫红发光字 | 7405417769446968610 | true
彩色渐变花字 | 7248130865094561036 | true
绿色立体花字 | 7241415162345852194 | true
条纹黄色综艺发光花字 | 7275250557386788156 | true
梦幻紫星光双层立体花字 | 7404321217110396187 | true
粉色闪闪 | 7529808923725925657 | true
荧光线条发光字 | 7405939554047233295 | true
机械装甲绿色科技感文字标题 | 7327845943305358646 | true
发光灯箱感绿色描边立体花字 | 7404100687820229922 | true
白花纹发光花字 | 7259233733964811572 | true
清新绿色 绿色花字 | 7334225752663149850 | true
浅绿色 绿色花字底发光 | 7334229773402606886 | true
夏日青春派对 | 7249749880611015988 | true
紫色发光字 | 7406201706456960256 | true
白色描边芭比粉发光花字 | 7404708538926353700 | true
花字-雪花彩粉渐变立体字 | 7232089500518862140 | true
赛博朋克纹理发光字 | 7405875861712342307 | true
浅梦幻少女色 | 7281283804235402533 | true
彩色镭射渐变花字 | 7404330497574309129 | true
紫色发光立体花字 | 7245923862574009635 | true
薄荷绿花字 | 7404021791427005723 | true
青色 红色 荧光花字 | 7241393660334574848 | true
绿色花字 | 7351303614104636699 | true
紫宝石 | 7241904291722693944 | true
粉橙色花字 | 7241388504381541666 | true
格子纹理花字 | 7260122300564000012 | true
复古格子清新蓝花字 | 7297906734755073319 | true
深绿色黑边紫光花字 | 7231501962041117955 | true
紫色粉边花字 | 7291157036098735401 | true
清新蓝色发光花字 | 6896138122774514951 | false
潮酷 白色橙边 | 7127615338035924238 | false
简约白色发光立体花字 | 7166445713029729568 | false
超酷发光镂空花字、潮人必备 | 6896141886055107854 | false
潮酷蓝色发光镂空花字 | 6896141886055091470 | false
综艺 橙色 | 7127654126997048607 | false
清新粉色发光灯箱感花字 | 6896138122774531335 | false
炫彩发光跳色花字， | 6896141886055058702 | false
潮酷 橙色 | 7127817897061125413 | false
潮酷黄色霓虹灯花字 | 6926796566346960141 | false
红色镂空发光花字 | 6926825801258126599 | false
潮酷蓝色霓虹灯发光花字 | 6926827744189795591 | false
潮酷黄底白色发光立体花字 | 7187616139642522936 | false
蓝色镂空发光花字 | 6927159112887176459 | false
潮酷 白色粉边 | 7127819154018602277 | false
暗黑潮酷黑色花字 | 6926825801258159367 | false
超酷黄色发光花字 | 6896143968241798408 | false
小清新 白色 | 7127680616283295006 | false
黄色发光字 | 7405565480678739200 | false
炫彩发光花字，跳字变色 | 6896141886055075086 | false
发光灯箱感绿色花字 | 6896144021568179469 | false
潮酷黄色发光花字 | 6926825801384021256 | false
复古 红色 | 7127827287826779428 | false
赛博朋克未来科技感立体发光花字 | 7404088879780826406 | false
红色潮酷外发光花字 | 6927160254996253967 | false
红色朦胧港风复古花字 | 6927160144421866752 | false
Y2k粉色立体灯箱发光花字 | 7127675252410289445 | false
潮酷粉色发光镂空花字 | 6896143968241782024 | false
梦幻粉色发光立体花字 | 7197333872466611513 | false
潮酷发光青色 | 7127669605199351048 | false
黄橙渐变黑红描边立体字 | 7403926640260123944 | true
蓝色纹理立体发光花字 | 7430703360409554212 | true
黄色渐变红边发光花字 | 7407014765907774747 | true
潮酷发光立体花字 | 7160596855456320776 | true
立体金属字 | 7317088712154696969 | true
黑金色立体花字 | 7244940532298829090 | true
黑灰色花字【严肃】 | 7281947750139219257 | true
美食-黄网格 | 7212896770370587941 | true
金属灰渐变立体白边花字 | 7388020661312146751 | true
一窝时光标题花字字体设计美食海报大气简约醒目小龙虾 | 7260358084772547903 | true
蓝色渐变3D立体花字 | 7405125461438762267 | true
立体效果 | 7274581371975142710 | true
美食-金色网格 | 7212897121249283383 | true
土酷蓝色渐变立体花字 | 7160599091750145287 | true
蓝色渐变花字 | 7220003213171281192 | true
黄色渐变花字 | 7265625223381273891 | true
黄色渐变花字 | 7493083674158796094 | true
黄白涂鸦花字 | 7369091570345282866 | true
黑灰渐变 | 7224762483448237345 | true
彩色渐变描边 | 7369985913310448911 | true
黄色渐变花字 | 7439987370033728807 | true
橘黄色渐变波点底纹立体花字 | 7405889740081237285 | true
大雪渐变 | 7431533312738348314 | true
黑白配 | 7268912246900772135 | true
美食-黄白跳色 | 7252679635027168567 | true
蓝色渐变立体描边花字 | 7511237110914125080 | true
美食-弹幕 | 7212885712495070519 | true
蓝色花字 | 7264536942832848165 | true
橘色渐变描边花字 | 7265622781008629032 | true
黄橙色渐变描边立体花字 | 7405056217225104681 | true
金色渐变 金灿灿花字 富贵 | 7328610126296796468 | true
花字 | 7491562659268119870 | true
暗黑红黑渐立体花字 | 7205151372805754167 | true
粉色渐变红色底花字 | 7404684532756073791 | true
黄色渐变立体花字 | 7313119295792352539 | true
综艺立体花字 | 7160601969629891847 | true
扁平化请新白蓝 | 7233363221497842977 | true
春节-兔彩头-银色立体 | 7187770975822433594 | true
蓝色渐变花字 | 7404899700970753321 | true
花字 | 7530918113899105561 | true
七夕-粉白渐变 | 7265298421341277452 | true
金色红底春节喜庆花字 | 7324218891222240522 | true
花字 | 7431462520835099955 | true
金色渐变红底立体花字 | 7324255228310654235 | true
黄红渐变黑边立体花字 | 7431549062475762959 | true
美食-红黄渐变 | 7205154202757172541 | true
美食-划痕渐变 | 7212896808798801213 | true
蓝色渐变白色描边花字 | 7330967545240964404 | true
渐变蓝色花字 | 7384325883584056617 | true
红色描边双色渐变立体花字 | 7391023993802804521 | true
橙色渐变波点双层立体花字 | 7404880919582018854 | true
浅蓝粉渐变立体花字 | 7312840128949505307 | true
紫色立体花字 | 7399918916232826123 | true
简约蓝色渐变立体花字 | 7248118492111703357 | true
黄蓝撞色渐变立体花字 | 7405583007098195237 | true
彩色渐变 | 7369988046277594383 | true
黄橘渐变 | 7410717398510128424 | true
红色渐变透明花字 | 7405253473299696931 | true
雪花字 | 7298358091664362793 | true
美食-辣 | 7205147811573271864 | true
黄白色渐变立体花字 | 7493079330654899480 | true
彩色 | 7369460089767480614 | true
白字霓虹灯渐变花字 | 7406294702212877619 | true
冬日寒冷发光花字 | 7263267444020596005 | true
彩色渐变花字 | 7405953290271198491 | true
黄绿渐变发光字 | 7406253347746876706 | true
黄色渐变描边立体花字 | 7383803879730842931 | true
简约渐变花字 | 7236638821901733175 | true
黄色渐变橙蓝色描边立体花字 | 7505100141288901950 | true
白绿紫渐变 | 7127664822887402759 | true
蓝绿渐变花字 | 7391445684953681192 | true
紫色立体渐变 | 7376115629230673204 | true
蓝色纹理发光立体花字 | 7430709931411623204 | true
黄色渐变双色描边花字 | 7265636111211449634 | true
蓝色渐变花字 | 7285696655989411133 | true
黄绿花纹立体字 | 7404026606869613864 | true
星空梦幻炫彩立体花字 | 7404369195875487016 | true
紫色 立体 渐变 花字 | 7527575726220987672 | true
花字 | 7241433848943365436 | true
蓝字彩虹渐变描边花字 | 7404026005389708595 | true
国风粉色渐变 | 7406640534036532490 | true
多色渐变花字 | 7405867875317173516 | true
蓝色渐变立体花字 | 7371124565839301925 | true
渐变白色描边花字 | 7405949704904658203 | true
黄色手绘蜡笔质感花字 | 7366899343451852058 | true
3D渐变绿色立体花字 | 7404710833344892196 | true
简约双层描边蓝色渐变花字 | 7497111940762995993 | true
五色花字 | 7430992115376704819 | true
炫彩星空花字 | 6896143862222327047 | true
美妆立体 | 7482318463755734334 | true
忧郁蓝 | 7481306716752219417 | true
黑底纹粉渐变描边发光花字 | 7407010177842482459 | true
粉色渐变镂空描边 | 7406359623545933093 | true
金色渐变描边花字 | 7391015553818692927 | true
白字花字 | 7404038278057332005 | true
暗色花字 | 7249649958297783589 | true
双十一-彩色立体字 | 7296106361153293618 | true
天蓝色渐变花字 | 7241433473796394255 | true
红色渐变立体文字 | 7406232498734157090 | true
粉色梦幻立体 | 7404129182244031782 | true
粉色渐变发光花字 | 7405578926489160998 | true
彩色 | 7369459252290718986 | true
黄色渐变粉色阴影立体花字 | 7495776303799618878 | true
低饱和蓝色渐变立体白边花字 | 7388019320686693686 | true
绿色渐变蓝紫色描边花字 | 7315437477425155368 | true
粉色渐变 | 7475023258228788505 | true
红色燃烧花字 | 7405837403782384906 | true
春节喜庆金字红边立体花字 | 7460547039252909337 | true
斜线纹理黑白漫画感花字 | 7405244303586397476 | true
白纸纹理蓝边拼贴花字 | 7509039282737302808 | true
花字 | 7545325777781280024 | true
粉笔质感纸张花字 | 7538694611150130457 | true
黄色立体纹理花字 | 7405846768010661157 | true
像素化花字 | 7488161196357487934 | true
白色纸质纹理立体 | 7406014922078965001 | true
黄红立体字 | 7492626374239243545 | true
像素化花字 | 7482734426015730968 | true
花字 | 7480452404811615512 | true
金属质感硬朗立体花字 | 7405140394662530354 | true
冰雪大世界立体雪花字 | 7407272554445999411 | true
不织布新年红 | 7449585330547625228 | true
复古纸张纹理字 | 7404377624690101544 | true
花字 | 7541849024001740056 | true
像素化游戏花字 | 7482761022504275262 | true
未来科技感赛博斜体字 | 7405126783332404517 | true
复古格纹立体花字 | 7406192655488519433 | true
清爽冰块纹理字 | 7405853759911333172 | true
绿叶绿色纹理花字 | 7435107467366878503 | true
港风图案纹理花字 | 7451442109753675070 | true
冰块立体字 | 7405824092479196431 | true
蓝色星空花字 | 7405857800208928037 | true
红色纹理立体花字 | 7405855842072808755 | true
复古红轴 | 7483893116274117950 | true
红黄质感立体花字 | 7481535145284160792 | true
蓝紫色发光纹理花字 | 7405843250960993586 | true
牛奶花字 | 7532883438072778008 | true
木纹雕刻立体字 | 7405870250916384015 | true
像素化花字 | 7486311409861528894 | true
粉笔黑板花字（教师节） | 7405550386234281235 | true
梦幻爱心纹理底花字 | 7330983004631878964 | true
流光立体花字 | 7405693659536051492 | true
蓝色渐变DIY纹理立体花字 | 7371332005948083494 | true
冬日冰花 | 7407265065272937778 | true
红色黑条纹字 | 7406984542742924582 | true
蓝色天空纹理立体花字 | 7406190866626366770 | true
荧光紫渐变字 | 7404383053906267392 | true
红色洒墨花字（书法古风） | 7405523650423639308 | true
蓝色渐变立体描边花字 | 7405919974411242791 | true
圣诞-四色纹理 | 7306473747953863975 | true
渐变纹理花字 | 7506817303296675123 | true
游戏像素化花字 | 7486231125992623385 | true
花石榴 | 7471979945447836952 | true
紫色纹理描边立体花字 | 7405866412570348836 | true
蓝色毛毡绒毛立体花字 | 7404145370399329587 | true
紫色纹理立体发光花字 | 7430717597039054143 | true
粉笔蓝白色立体花字 | 7405201103903624463 | true
绿粉圈圈纹理综艺花字 | 7546407203654159678 | true
红色棋盘格纹理立体花字 | 7405573811107663155 | true
方块游戏花字 | 7477911542575516952 | true
彩色纹理花字 | 7406205168200568115 | true
绿色粉笔描边花字 | 7405201692775451904 | true
3D蓝粉色渐变立体花字 | 7406173713428745509 | true
红砖纹理立体花字 | 7405864219809287433 | true
蓝黄拼色立体花字 | 7405917544126647602 | true
红色花字 | 7481938079507418430 | true
光影立体花字 | 7405856104946748723 | true
镭射荧光酸性纹理花字 | 7404891005968747802 | true
潮酷镭射立体文字 | 7405104737386892584 | true
绿色立体花字 | 7480467236327820606 | true
花字 | 7482727212375035160 | true
芭比闪粉星光花字 | 7405130183306415397 | true
黄绿格纹立体花字 | 7405647754199895305 | true
青草绿纹理花字 | 7442563568295218441 | true
粉蓝格纹立体花字 | 7405919944526892315 | true
双色纹理立体字 | 7405860859177717032 | true
绿色波点纹理花字 | 7405844279479913766 | true
粉色纹理多层阴影花字 | 7405245402917735691 | true
粉橙色条纹纹理立体发光花字 | 7542359139469626649 | true
粉黄纹理立体花字 | 7405645973613022515 | true
粉色格纹立体字 | 7406387389809069321 | true
黄色纹理描边发光花字 | 7404875825729850659 | false
毛笔质感 | 7410762405778705715 | false
春节-立体红白 | 7321972094949018921 | true
春节火焰 | 7457575657376238910 | true
红色渐变花字 | 7404876992962759999 | true
红色渐变裂痕综艺花字 | 7404314496833015077 | true
红色描边花字 | 7401445200071003404 | true
白色纹理红色字 | 7405812611427749158 | true
白字红蓝描边 | 7403692022239956274 | true
红色黑边立体花字 | 7270171000652696893 | true
重阴影红白渐变黑描边花字 | 7328997429544488244 | true
万圣-血滴字 | 7294156228794535207 | true
开工立体 | 7462945508533931288 | true
红色白色描边花字 | 7404769759432084748 | true
红纹理立体白描边花字 | 7403672172897553715 | true
多层红色渐变描边黑色花字 | 7329003799433973027 | true
万圣-红木板字 | 7294182924587502889 | true
像素化花字 | 7489037914584681790 | true
双11-红白 | 7294992987908541715 | true
大红色描边花字 | 7399184087103196428 | true
白字带红划白黑描边 | 7406678794901130534 | true
金箔字喜庆圆底花字 | 7407014800204549413 | true
暗红花字 | 7127646385628908807 | true
友友红色渐变图案立体花字 | 7166470216396885280 | true
红黑渐变花字 | 7252964174744096003 | true
综艺 红色渐变 | 7127624093628697864 | true
红色复古文字 | 7404416840476265780 | true
镂空印章花字 | 7348241821694233867 | true
红底雪花纹理花字 | 7404888947479825715 | true
25元旦-福圈背景花字 | 7447922811793853732 | true
红色光斑纹理立体深红影花字 | 7245603807105699106 | true
怀旧红 | 7388867127597403428 | true
立体效果花字 | 7233578306912767271 | true
复古红蓝 | 7460441811627035929 | true
双十一-霓虹立体 | 7296357051788168467 | true
暗黑橙色渐变描边花字 | 7405143396869770534 | true
黄红新年花字 | 7462291141325688088 | true
春节喜庆金粉红边黑色花字 | 7404082176163106099 | true
红色立体 | 7457924478878928152 | true
红色渐变花字 | 7400944971932536099 | true
元旦-红白 | 7309137807929281831 | true
金色描边红色纹理花字 | 7404681840377875766 | true
红色描边花字 | 7400213633055198503 | true
综艺红蓝撞色立体花字 | 7404068280916397362 | true
红色细闪黑色投影花字 | 7404893190593072393 | true
白红渐变花字 | 7127822719047011621 | true
年味-红字金边 | 7322728803560754482 | true
红色渐变黑边立体花字 | 7404036215848144179 | true
橙色热情简洁 橙色立体花字 | 7334612804831431987 | true
星星立体花字 | 7494900604641365310 | true
老电影 | 7266696776747486523 | true
复古红色渐变立体花字 | 7160597344935890206 | true
红白立体花字 | 7405737574372756772 | true
毛衣花字 | 7310234093625691404 | true
春节-奇怪兔-红底白花字 | 7187739440347958589 | true
黑红渐变 | 7404028453063888155 | true
双十一-霓虹立体黄 | 7296352415060626699 | true
红色蓝白边花字 | 7335713356629822730 | true
红色渐变裂痕花字 | 7404769483220405531 | true
社媒-网格红白子 | 7300919700102401316 | true
红色 花字 | 7390391149338348800 | true
3D红色渐变星光立体花字 | 7406174570966781221 | true
红色渐变立体花字 | 7371379435443948809 | true
港风复古蓝字红底花字 | 7319136118539078922 | true
红黄渐变纹理立体花字 | 7313169456081947931 | true
简约黄底橙色渐变花字 | 7181327362708098359 | true
红色渐变立体波点底纹花字 | 7404035148204739867 | true
红色立体发光花字 | 7430675317255179574 | true
春节对联质感花字 | 7403928233030241587 | true
射线红色花字 | 7349746427217710377 | true
儿童节花字 | 7365464569642323252 | true
红色立体花字 | 7493087421102411033 | true
红色内投影白边立体花字 | 7404782201583324466 | true
红色渐变花字 | 7273017574063901991 | true
粉色描边花字 | 7399922623116840231 | true
红字双层描边纸张纹理花字 | 7405025997860490506 | true
元旦-红黄质感 | 7312747055447854390 | true
港风复古红底花字 | 7319408651859397926 | true
红黄立体花字 | 7127669886762945805 | true
红黄立体字 | 7410765061796416768 | true
白字红边渐变立体加厚花字 | 7404521144532929819 | true
红色填充白色描边 | 7430448068283206950 | true
粉金新年花字 | 7459730150943395134 | true
圣诞-纹理红 | 7305806489069833491 | true
春节-奇怪兔-白底红花字 | 7187743354308873529 | true
米色橘色描边立体花字 | 7371354957989055782 | true
红色复古立体描边花字 | 7404112581427858703 | true
元旦红色立体花字 | 7404796157727083814 | true
橙色描边立体综艺花字 | 7405243169991855423 | true
红色描边花字 | 7402051434893593919 | true
红底雪花纹理黑边立体字 | 7405204082987683123 | true
渐变黑荧光绿花字 | 7405947349379452211 | true
春节-立体红 | 7321977363233803574 | true
春节-花窗底花字 | 7320257181046082870 | true
招财猫花字 | 7329740101192387878 | true
23带货-红白花字 | 7273028546514193675 | true
圣诞-雪花红色字 | 7312419048623541545 | true
复古红绿撞色立体字 | 7406644388358540544 | true
122 | 7332292224668994867 | true
春节-隐藏 | 7187615351868280121 | true
红色绿色发光字 | 7406863699895389449 | true
渐变黄色阴影花字 | 7245154816765234488 | true
东北大花修改版 | 7397798364848393481 | true
红色渐变花字 | 7483443907032911166 | true
粉色立体花字 | 7402043271733628172 | true
简约描边红色纹理花字 | 7460455706701892889 | true
红色渐变立体发光花字 | 7328403746214464819 | true
互动立体 | 7407340226189757733 | true
重阴影金色金属渐变纹理伪三维花字 | 7328988831762484480 | true
黄面红底黑边双重花字 | 7277814401518800147 | true
潮酷发光立体花字 | 7160596855686991140 | true
阴影金色金属纹理立体伪三维花字 | 7328988266768764194 | true
火焰燃烧花字 | 7402109946025790747 | true
复古橙色渐变立体花字 | 7160601605233052959 | true
黄色立体花字 | 7260019709662219576 | true
复古橙色渐变立体花字 | 7166483277631540492 | true
金色纹理花字 | 7465587976928660760 | true
复古橙色渐变发光立体花字 | 7160603032248405285 | true
黄色黑底古典中国风风格花字 | 7398576754434067723 | true
黄色底字 | 7343599630678019362 | true
面包黄渐变花字 | 7445226210377927977 | true
渐变星星花字 | 7460434187036691737 | true
金镂空花字 | 7181467986249796920 | true
黄色立体花字 | 7273052950707145996 | true
黄色描边花字 | 7401444618681847103 | true
年味-金箔字 | 7322735036669758729 | true
春节-奇怪兔-黄针织花字 | 7187743885479791932 | true
3D黄色渐变立体综艺花字 | 7403927207162203402 | true
清新黄色立体花字 | 7203613972434685242 | true
淡黄色花字 | 7245162195829460263 | true
黄字黑边红底花字 | 7431549056674991375 | true
综艺-宇宙一番 | 7351315241428471090 | true
黄粉立体 | 7127667703048965389 | true
中秋灯笼星星花字 | 7406743750933810471 | true
黄色渐变纹理描边花字 | 7328737068006378787 | true
黄绸缎 | 7495311379738397976 | true
浪漫中秋渐变 | 7407412458370944294 | true
黄色花字 | 7448948322427047230 | true
渐变金色花字 | 7349752453350395155 | true
3D综艺风蓝黄渐变立体花字 | 7404135722242067722 | true
芭比黄色 | 7260815156861619493 | true
综艺立体花字 | 7160597556869795102 | true
黄色渐变花字 | 7311260697751457063 | true
描边四色花字-黄 | 7324728355134147876 | true
元旦-黄红 | 7309138668319444287 | true
纹理花字 | 7399157478648253732 | true
橙子 | 7263114818876476729 | true
格纹复古立体花字 | 7405945244237303091 | true
粉黄撞色星星装饰花字 | 7406205299100536074 | true
金黄色渐变多色复合描边花字 | 7460131684537601331 | true
邮票字 | 7325388931430763812 | true
黄色 | 7371660746725330217 | true
黄色渐变波点纹理花字 | 7405224102115527936 | true
红背景用浅黄色无边无影花字 | 7244522111643946275 | true
简约花字 | 7160597869638978824 | true
综艺字星星 | 7409320679838846234 | true
黄色立体质感花字 | 7480466283088235801 | true
黄色描边花字 | 7402069935075151123 | true
描边新年花字 | 7307096095828528395 | true
浅黄色渐变发光花字 | 7328738345616510242 | true
金属金色立体花字 | 7187774415130643769 | true
黄白字体重复花字 | 7265639510296300852 | true
黄色立体描边花字 | 7405023729782164747 | true
黄色渐变立体发光花字 | 7371124431713832201 | true
可爱风立体描边 | 7434103306181528882 | true
好物美妆黄白渐变 | 7264858160744221971 | true
金花字 | 7406269205164592396 | true
黄色发光透明字 | 7406979588020047104 | true
双11-黄色渐变 | 7294994395907018025 | true
白色立体字 | 7389657424883387699 | true
黄边橙底花字 | 7340552492331142454 | true
黄色线条花字 | 7404825166351469860 | true
黄色立体描边花字 | 7405239905443482919 | true
黄色立体发光字 | 7405078751823809801 | true
渐变白色花字 | 7349078549061504275 | true
黄色描边花字 | 7407448816653258036 | true
黄蓝立体 | 7127675251604966669 | true
黄色镂空描边花字 | 7406349356347002138 | true
奶酪花字 | 7328608627542002998 | true
橙色立体花字 | 7400210254580944169 | true
纯黑底色 黄色黑色描边 立体 花字 | 7275153233226616124 | true
黄色花字 | 7380754518914518287 | true
国庆旅行-手绘黄 | 7283170032912256310 | true
黄底纸张撕边字 | 7404023782316313890 | true
黄色波点描边立体花字 | 7404881915871825186 | true
红色渐变伪三维多层描边花字 | 7329011018632269108 | true
黄色 | 7405879107424111910 | true
复古阴影描边花字 | 7345385438401580307 | true
黄色黑白描边花字 | 7270426004617825593 | true
黄色描边花字 | 7402075098393365823 | true
黄白纯色花字 | 7265643261631417635 | true
好物美妆-双层投影 | 7264502894546767116 | true
白底橙描黄字 | 7251576577530531110 | true
运动教程-花字 | 7311260579992227091 | true
美食-白网格 | 7212892034623950141 | true
描边白蓝字体 | 7387594122032385321 | true
黑白描边 | 7127676763148143885 | true
综艺-黑暗斑驳白色 | 7351313732443671827 | true
简约透明渐变 | 7160601239800040712 | true
音乐节-杂点白字 | 7272727186036116755 | true
黑白 动漫 波普 美漫 复古 | 7114534269543828766 | true
韩国综艺-紧张的瞬间 | 7351311491821276452 | true
美食-白色躁点 | 7252680796429897021 | true
黑色手绘质感花字 | 7345748543577099547 | true
黑色白边花字 | 7325238973809298742 | true
纸张背景字 | 7343223006396828968 | true
白色DIY纹理立体花字 | 7371395905561365770 | true
复古黑色渐变立体花字 | 7166468321125207299 | true
立体花字 | 7369126670915226899 | true
复古白色图案立体花字 | 7166477143159868710 | true
纹理花字 | 7337938878139010355 | true
撒银粉花字 | 7181453824148753702 | true
暗黑白边黑色立体花字 | 7166490848820038945 | true
透明渐变-白 | 7181336409813372197 | true
运动教程-纹理花字 | 7311952196956917033 | true
潮酷灰色立体花字 | 7160595742489382151 | true
黑白花字 | 7273018315025550628 | true
纸张背景字 | 7343809832324975891 | true
元宵-黑字发光 | 7194356393271446843 | true
黑白复古红色 | 7260344475921190207 | true
拼贴白纸底纹理花字 | 7313563919245643008 | true
拼贴底黑白纹理花字 | 7313511240523959604 | true
撕边纸张背景字 | 7343584149648772352 | true
白色立体花字 | 7241426840395549985 | true
3D白字 | 7173539578815483149 | true
复古花字 | 7435890198455536923 | true
描边纸纹花字 | 7343449320475151627 | true
纸张背景字 | 7343160086795242788 | true
黑白花字 | 7349124649973730599 | true
运动-潮流运动-黑色纸纹 | 7160602457658117384 | true
黑色纹理立体花字 | 7310103573377846538 | true
黑色立体花字 | 7400199119807008036 | true
斑马纹字 | 7285632742400740645 | true
黑份星空体 | 7266689977793269048 | true
万圣-白木板字 | 7294186899491654951 | true
白色毛绒豹纹花字 | 7265615157953334562 | true
潮酷花字 | 7365355573036059913 | true
潮流运动-纸纹描边 | 7200668850155801893 | true
简约黑色描边立体花字 | 6927160144421784832 | false
简约白色黑边花字 | 6896137990788091143 | false
灰色金属质感花字 | 6896143808942066952 | false
简约黑字白边花字 | 7166467215410187552 | false
简约白色花字 | 7166472183814950183 | false
综艺黑白立体花字 | 7127681015732096270 | false
232 | 7127668616656506149 | false
网感-黑字白边外发光花字 | 7166473306248465703 | false
简约黑白镂空花字 | 6896137661153676552 | false
简约黑白花字 | 6896137924853648648 | false
白色裂纹花字 | 6896137727012637959 | false
综艺 白色 | 7127830659275459871 | false
综艺 白色 裂纹 | 7127540233750596871 | false
简约白色镂空花字 | 7166476751420329248 | false
绿边黑底白色花字 | 7127830631601474824 | false
简约白色镂空花字，排版适用 | 6896144074487696654 | false
金属感渐变灰色花字，日本综艺 | 6896138188792843527 | false
综艺 白色黑边 | 7021075312532393247 | false
投影红底白色花字 | 7181337352327941431 | false
白色镂空感简约花字 | 6896138254819577102 | false
简约黑灰色拖影花字 | 6896138254819560718 | false
简约黑白色花字 | 6896144074487729422 | false
简约黑白花字 | 6926796566347025677 | false
小清新 白色 | 7127823728070741278 | false
简约透明白色花字 | 7127669342325542158 | false
暗黑白色渐变发光花字 | 7166475342436224267 | false
简约白色立体花字 | 7166474083817884966 | false
潮酷 白色 | 7127674303260265764 | false
白底橙色波点花字 | 7127676414962224421 | false
简约黑白几何立体花字 | 6896137727012654343 | false
丝印纹理花字 | 7304198748958199076 | false
半透明灰色立体花字 | 6896144234013854990 | false
白色大理石纹理立体花字 | 6896137793022545159 | false
潮酷星空立体花字 | 6927160139363388684 | false
潮酷黑色绿边发光立体花字 | 7194356906171927866 | false
综艺 黑色 | 7127594686541286687 | false
黑丝印蓝阴影字 | 7304122881682853161 | false
潮流运动2-黑色纹理 | 7200660554552331575 | false
深蓝白色立体花字 | 7405917902894927114 | true
蓝色渐变描边花字 | 7265628111796964643 | true
蓝色渐变文字 | 7236980379452787968 | true
蓝白色立体花字 | 7431507293306506533 | true
3D蓝色渐变立体花字 | 7405874090348711218 | true
蓝白花字 | 7127828208690482463 | true
花字 | 7478297038023871769 | true
蓝色立体描边花字 | 7297087768889494847 | true
蓝色渐变星星花字 | 7404757920535055679 | true
蓝色 花字 | 7390775733812989199 | true
蓝色立体字 | 7404828637326757172 | true
蓝色白边立体字 | 7284086330060033334 | true
蓝色星空填充花字 | 7234332653498027325 | true
蓝色花字 | 7339051729943661851 | true
蓝色渐变立体 | 7404341814565539110 | true
蓝色描边字 | 7403983551021993243 | true
伪三维多层描边花字 | 7315430777976655139 | true
蓝色描边花字 | 7274827617654656308 | true
蓝色渐变动漫风格花字 | 7424738578648894732 | true
蓝色雪花花字 | 7252223990217837862 | true
蓝色立体花字 | 7511286098283351320 | true
冬天花字 | 7298723012642229523 | true
知识-花字 | 7317914423186820391 | true
双层描边白蓝双色花字 | 7404710098255269139 | true
蓝色质感纹理立体花字 | 7306901916288666906 | true
复古蓝色花字 | 7274824941151800610 | true
深蓝色立体花字 | 7283010376986299663 | true
白蓝色粗描边立体字 | 7300921005386566931 | true
冷酷蓝色渐变 | 7400713144886119730 | true
蓝色霓虹灯 | 7291342429117107471 | true
蓝色立体 白字 | 7287492960478973238 | true
知识-花字2 | 7317913619340070207 | true
蓝色白描边字 | 7378305489609706752 | true
冬日-发光蓝 | 7302303263188159779 | true
冰爽蓝色花字 | 7245601258441133369 | true
蓝色投影字 | 7404004705740786996 | true
背景字 | 7360972639780850978 | true
黑蓝花字 | 7273026280830946572 | true
蓝黑渐变综艺描边立体花字 | 7404089887411965199 | true
蓝黑双描边冰块冰雪万花筒花字 | 7404876048438938895 | true
蓝边白花字 | 7300920494520356108 | true
蓝白描边花字 | 7259925979139722553 | true
蓝色科技花字带阴影 | 7400998328315448627 | true
蓝色描边花字 | 7400211255723642151 | true
蓝色描边花字 | 7400215751618989331 | true
韩式综艺 | 7245935944744946944 | true
蓝色渐变花字 | 7265626134212054324 | true
闪烁蓝 | 7363764911773699340 | true
蓝底拼贴字 | 7343225910864153896 | true
蓝色双层描边 | 7406384565951941914 | true
蓝色花字 | 7300919051906321727 | true
蓝色梦幻立体花字 | 7401436090340576563 | true
清新简化单色花字 | 7267373226962095415 | true
蓝色小清新花字 | 7399182466470169919 | true
白字蓝底拼贴花字 | 7379206506035662117 | true
蓝色花字 | 7448931302520278296 | true
蓝色花字 | 7241417086294166836 | true
简约描边纸纹理蓝色花字 | 7460439436510301464 | true
蓝色渐变花字 | 7400200671015783716 | true
白色纸张质感立体花字 | 7430995853440994570 | true
蓝白描边 | 7434900706798161203 | true
深蓝色渐变花字 | 7252220565577026828 | true
浅色格子布纹花字 | 7260765036711251261 | true
白蓝纹理字 | 7431505103326137615 | true
蓝白花字 | 7366638884362390803 | true
浅蓝内阴影白色描边字 | 7405953919085595930 | true
蓝色冰块效果立体花字 | 7404362111041735974 | true
白色描边字 | 7247317471550623009 | true
蓝黄综艺花字 | 7471593256606895385 | true
花字 | 7526161513816739097 | true
白色蓝紫渐变立体花字 | 7329779937915702537 | true
冰冰凉 | 7497604377235049790 | true
蓝色立体花字 | 7525043694467255614 | true
白字多层次描边花字 | 7450314918068243739 | true
蓝色立体拆痕花字 | 7248079950924893451 | true
蓝白色冬季冰雪花字 | 7404526221230443785 | true
游戏立体字 | 7405801528612769060 | true
赛博花样字体 | 7245076686734167329 | true
白色纸张质感立体花字 | 7430824690727275802 | true
白色石材质感立体蓝阴影花字 | 7404076575030922505 | true
蓝色立体花字 | 7400212292211641663 | true
多巴胺蓝色花字 | 7256676293956128055 | true
白色花字 | 7510996426575449368 | true
蓝色描边投影立体花字 | 7377956281291672842 | true
蓝色阴影花字 | 7346455592367623443 | true
蓝色立体花字 | 7511159840157453592 | true
蓝色阴影花字 | 7331609291226402102 | true
蓝色渐变波点纹理花字 | 7405224199884737827 | true
像素风游戏风纹理花字蓝色伪三维 | 7314956298682928384 | true
浅蓝色纹理立体花字 | 7404762475582786852 | true
蓝色渐变卡通花字 | 7291337904947776802 | true
复古蓝色字 | 7430797889141509416 | true
白字蓝边粗描边花字 | 7404381121615613210 | true
蓝色描边花字 | 7400214111411293451 | true
卡通条纹渐变花字 | 7402114255383760166 | true
立体字 | 7480096931411266840 | true
冬至圆底 | 7430854925019565321 | true
蓝色渐变花字 | 7252216909721029899 | true
蓝色渐变方底花字 | 7405238192510602546 | true
互动引导立体 | 7527223959767764248 | true
特殊纹理粉色渐变花字白色描边 | 7332635756839718179 | true
粉色黑投影立体字 | 7403931785077329167 | true
时尚亮粉色花字 | 7268272864770460991 | true
白色立体字 | 7389651692385570075 | true
粉色花字 | 7399162410034105636 | true
端午61立体字效 | 7506871646129573182 | true
七夕-粉色渐变 | 7265147554952711465 | true
描边阴影花字 | 7350942991793622335 | true
美妆立体 | 7526125596955659545 | true
粉色描边白色花字 | 7263028102610144575 | true
粉色渐变花字 | 7350941310355868991 | true
粉色描边花字 | 7399826245703175487 | true
粉蓝色多层立体综艺风花字 | 7371412248163568905 | true
粉黄描边立体 | 7471642975651564862 | true
复古发光立体花字 | 7160605820927872292 | true
母亲节立体 | 7496412960647286078 | true
粉色渐变立体爱心背景花字 | 7405576947159387443 | true
粉色系花字 | 7273263711744232741 | true
小清新粉绿渐变立体花字 | 7471951122425515288 | true
粉色立体花字 | 7401443574719483155 | true
粉色立体描边花字 | 7476028091077430552 | true
发光花字 | 7405950908644723977 | true
粉色发光花字 | 7401438526962666788 | true
粉色草莓熊花字 | 7265599528579943714 | true
综艺-超期待 | 7351316363849354534 | true
鼠鼻红 黑描边 | 7278850102503001403 | true
粉白描边立体 | 7474566247460441368 | true
蓝粉色渐变多层立体花字 | 7404367331842936115 | true
玫红色  玫红色黑边花字 | 7337322283540696347 | true
粉绿花字 | 7127666013495102750 | true
粉色立体 | 7469667482442222910 | true
红边立体字 | 7362783053573262629 | true
可爱渐变粉色立体花字，少女漫画 | 6896144127935761672 | true
红色发光 | 7403924486346509606 | true
黑粉撞色 | 7355780050513382668 | true
立体字 | 7257044199663602998 | true
立体樱花花字 | 7348036600766483751 | true
红色立体花字 | 7252103474719051020 | true
玻璃质感 | 7241808652640865595 | true
粉紫色渐变发光花字 | 7403773847754902810 | true
清新粉色立体花字 | 7442237073668508978 | true
粉黄立体花字 | 7494574052934241560 | true
粉色渐隐字 | 7404309195387882786 | true
梦幻粉色渐变立体花字 | 7198021796891757882 | true
蓝紫色花字 | 7252148714372943136 | true
圣诞落雪-粉 | 7447461222691261731 | true
芭比花字 | 7259354579664375077 | true
花字 | 7532077639864208665 | true
国庆旅行-粉 | 7283431566179585343 | true
粉色渐变仿3d立体花字 | 7371338640280161545 | true
文艺粉色渐变花字 | 7197315212834377016 | true
闪烁浅粉 | 7363797275652443455 | true
粉粉描边 | 7127678663583157517 | true
立体粉色描边 | 7434113204139117850 | true
透明果冻粉 | 7483781507337817406 | true
合欢红 黑白描边 | 7278851099656768805 | true
紫粉色星光发光花字 | 7406010312467434779 | true
仿3d粉色 | 7347229028467608869 | true
红白色炫彩花字 | 7517639254835612937 | true
春节-兔彩头-粉色 | 7187770600503512381 | true
磨砂 | 7362836205475548470 | true
清新粉色立体描边花字 | 7404359079063244067 | true
粉白描边立体节日花字 | 7404870544413281536 | true
花朵形状花字 | 7343590343138446604 | true
粉色渐变波点纹理花字 | 7405224954368642319 | true
紫底橙边渐变色立体花字 | 7270134110692085029 | true
粉蓝弥散渐变立体花字 | 7535298048642108697 | true
粉色花字 | 7362188947243404596 | true
黄粉渐变立体花字 | 7312854311854148890 | true
粉色花字 | 7362367983555005733 | true
粉色渐变发光花字 | 7366060800315788570 | true
粉白色渐变立体花字 | 7404520184062430491 | true
黑粉甜酷渐变花字 | 7406172056645078299 | true
粉色水彩花字 | 7362058534923554111 | true
芭比白色描边 | 7260824497358409020 | true
纯色系花字 | 7244717011618532640 | true
镭射粉边厚投影 | 7260778139385695549 | true
立体渐变花字（综艺） | 7403951797972339979 | true
白色综艺感花字 | 7241938590169713923 | true
粉色 立体 白色 蒸汽波 像素风 | 7114574351407533342 | true
粉色黑边花字 | 7284091009229704487 | true
粉色蜡笔花字 | 7324622240555765046 | true
粉色 | 7481670126689946942 | true
粉色渐变花字 | 7404035812284779827 | true
粉色渐变发光 | 7406638428864924954 | true
白芭比花字 | 7405198458337889586 | true
粉蓝闪闪花字 | 7505772084703022361 | true
立体紫粉 | 7537151663212268825 | true
国庆旅行-手绘粉白 | 7283169557890501924 | true
粉色立体节日女神节 | 7337558715559611686 | true
高级美式配色花字 | 7263270863359724856 | true
可爱粉黄渐变立体花字 | 7403763886584777984 | true
白粉色仿3D立体花字 | 7371118955500555571 | true
粉紫色气球花字 | 7470023899539967257 | true
黄粉圆底心星点缀花字 | 7404876152554278154 | true
黑色描边深粉色渐变 | 7311627613137620278 | true
蛋糕卷 | 7541231272509574424 | true
渐变粉色花字 | 7400688551689555210 | true
芭比粉 | 7263379569594436900 | true
粉蓝彩色渐变立体花字 | 7296704810148007219 | true
涂鸦字 | 7361330845342371113 | true
粉色闪闪花字 | 7459711214587776318 | true
紫色描边花字 | 7402071915386408203 | true
甜酷芭比粉色立体花字 | 7403721451993304370 | true
粉色千层浪漫花字 | 7402123078743919923 | true
爱心背景字 | 7328249466295733544 | true
粉色紫色渐变立体 | 7406377074849566003 | true
芭比黄色描边 | 7260816673165364541 | true
粉紫色多层渐变立体花字 | 7403767866266324261 | true
粉色y2k风花字 | 7403755765573471500 | true
红字黄边立体字 | 7408393528163716404 | true
紫色渐变花字 | 7400336012813159699 | true
粉红色描边花字 | 7260309891452013883 | true
粉色黄边红底立体字体 | 7284083822910655756 | true
粉色渐变双色描边花字 | 7265636585973009704 | true
粉色樱花花字 | 7405756302271483155 | true
粉绿纹理综艺花字 | 7546485148498431256 | true
春日辣妹 | 7345309219098201370 | true
粉蓝色立体字效 | 7523240490314173721 | true
粉黑色描边甜酷花字 | 7404713728219925801 | true
粉色渐变透明花字 | 7405254623050599732 | true
多层描边粉紫色渐变花字 | 7404706418848271670 | true
糖果 | 7522895833600380222 | true
粉色少女 | 7266702065966107959 | true
皇冠字 | 7340848509379251468 | true
粉紫色花字 | 7251733111518579979 | true
纹理花字 | 7297042051802172698 | true
粉色花字 | 7405086290414144777 | true
粉色渐变发光花字 多层描边 | 7328707180419386676 | true
橘色渐变镂空描边花字 | 7405929528134077734 | true
亮绿色拼接花字 | 7404493990520802598 | true
绿色渐变花字 | 7403996884856999194 | true
亮绿色综艺花字 | 7268270899432852799 | true
运动-潮流运动-渐变描边 | 7160596905548942622 | true
白色立体花字 | 7473670543162641689 | true
生鲜 绿色 花字 | 7278133287623707965 | true
青色渐变立体花字 | 7371122063710391561 | true
复古绿色渐变立体花字 | 7187772431149305143 | true
绿色立体花字 | 7475754844909882649 | true
绿色蓝色描边花字 | 7404747598109609228 | true
黄绿渐变立体字 | 7406966103861169408 | true
浅绿渐变立体花字 | 7298613319999540507 | true
绿巨人花字 | 7294165467973897526 | true
渐变青色花字 | 7348241222261050663 | true
黑加绿花字 | 7281934860015406391 | true
白绿色字体重复花字 | 7265646083169193231 | true
潮酷简约渐变绿色花字 | 7388017961174404415 | true
草绿色渐变花字 | 7283056755100208443 | true
高饱和撞色渐变立体花字 | 7404080787638799651 | true
运动立体 | 7473821452597316926 | true
综艺活泼亮色花字 | 7291929593328504100 | true
绿色花字 | 7472017607768673598 | true
tiffany波纹面 | 7398445914676874505 | true
黄色渐变立体花字 | 7473921287983795481 | true
清新绿色描边花字 | 7400209808361622825 | true
绿色质感花字   绿色金属质感反光花字 | 7334624542985391411 | true
绿色阴影描边花字 | 7239898171730595110 | true
绿色纹理 | 7367570395483983143 | true
薄荷绿拼贴花字 | 7344963566241336639 | true
港风 | 7346463952278244618 | true
简约绿色镂空花字 | 7404093067151658274 | true
绿色黑边花字 | 7260286417681599784 | true
花字-金属立体绿 | 7137931766576205093 | true
绿色描边花字 | 7259935584053972284 | true
白字蓝绿渐变描边花字 | 7372039427452865819 | true
浅绿渐变立体花字 | 7298573318259477770 | true
绿色清新条纹渐变立体花字 | 7405127816867597605 | true
绿色渐变立体花字 | 7298614541112397083 | true
浅绿色渐变花字 | 7367605728321801509 | true
渐变绿色花字 | 7252153542847319307 | true
黄绿色纹理花字 | 7404768610100497700 | true
绿色描边花字 | 7407443209355332864 | true
黑板绿色复古简单极简风格标题 | 7327621248937151785 | true
简约渐变花字 | 7236568168368491814 | true
圣诞青字 | 7174293913962827016 | true
黑色纹理立体花字 | 7310093916974419210 | true
浅绿渐变立体花字 | 7298617654846295305 | true
黄绿描边花字 | 7411774424355065088 | true
立体 白色 蒸汽波 像素风 黄绿色黄色绿色 | 7114570857992703269 | true
绿色渐变立体花字 | 7345749275839597874 | true
港风 | 7347215675548634406 | true
综艺绿色描边花字 | 7254739710776593724 | true
描边纸纹花字 | 7342427659030383883 | true
绿色紫色 | 7397647341706104090 | true
绿色 | 7366841667820752140 | true
绿色立体花字 | 7431507395127282954 | true
绿色条纹渐变发光花字 | 7406004095309450546 | true
绿色渐变花字 | 7274503640545627404 | true
绿色描边 | 7361014988858789120 | true
蓝绿色立体花字 | 7405962322373578024 | true
清新花字 | 7368761827230092595 | true
双十一黄绿立体 | 7430467479744335142 | true
绿色渐变阴影花字 | 7344956185780456743 | true
复古绿色立体花字 | 7405561923728690458 | true
绿色渐变立体字 | 7404854087830867234 | true
蓝绿色运动风渐变花字 | 7405128752167963914 | true
国庆旅行-手绘字 | 7283122934682504460 | true
蓝绿色纹理渐变立体花字 | 7273732632578493755 | true
白色立体花字 | 7431502293394099506 | true
青色纹理花字 | 7348234501983636799 | true
粉绿色渐变多层立体花字 | 7474572068676357401 | true
黄蓝渐变立体花字 | 7312852084502564146 | true
三色渐变发光字 | 7406256498252188968 | true
圣诞-复古绿点 | 7305827683798224191 | true
绿色剪纸纹理 | 7360585289733098771 | true
亲子-绿色饼干立体字 | 7203615859544182053 | true
绿色紫色花字 | 7293142782896590114 | true
仿3d水波纹薄荷 | 7347236230674844937 | true
浅绿渐变立体花字 | 7298600104972307722 | true
好物推荐-眼前一黑 | 7272324394641280319 | true
绿字描边绿草茵茵经典风格花字 | 7430436359287868682 | true
青团花字 | 7348238901154221323 | true
清新配色哈密瓜色 | 7266049922468695353 | true
青绿色渐变白描边花字 | 7349548116372180260 | true
蓝黄渐变绿色描边花字 | 7430785639781567753 | true
青色 | 7369021564211318028 | true
绿色国风 | 7389681541141597478 | true
晕染绿 | 7357047867233602855 | true
格子蓝绿 | 7351694267858865462 | true
绿色花字 | 7348986730529262899 | true
绿色纸张拼贴背景综艺花字 | 7404139316554779914 | true
复古花字 | 7280818803355700499 | true
立体花字 | 7346213993691794699 | true
花字 | 7344606077083864357 | true
音乐-杂点绿色 | 7272741033979546943 | true
绿色荧光细黑描边字 | 7403935407680834851 | true
格子绿 | 7351681114013994252 | true
运动-潮流运动-绿蓝色纸纹 | 7160596892773027079 | true
绿白渐变花字 | 7239892464302034214 | true
浅绿渐变立体花字 | 7298617928423902502 | true
圣诞-圣诞快乐 | 7312358171530595623 | true
双色描边 | 7360990469402283298 | true
绿色花字 | 7351302410180005157 | true
绿色渐变黑边字 | 7406991694668795163 | true
小荷漫漫 | 7523990414601260350 | true
白字绿边带格纹 | 7406685269446905125 | true
紫绿渐变立体花字 | 7312853585660857637 | true
绿色水晶立体渐变花字 | 7406011060521667866 | true
港风复古墨绿圆边花字 | 7404043957887372571 | true
清新豆绿色  白字绿底花字 | 7334619118340951322 | true
绿色 | 7366841083415874835 | true
青色纹理花字 | 7348239399705972009 | true
草绿色花字 | 7281933472610929981 | true
绿色粉描边花字 | 7241410366796811555 | true
绿色背景圈花字 | 7330397394950966568 | true
白绿多层渐变投影花字 | 7405130126477757722 | true
绿色立体花字 | 7279301469516434747 | true
圣诞-圣诞色渐变 | 7312427317089848617 | true
黄绿色渐变圆形纹理底白色花字 | 7330567349382286644 | true
绿色同系花字 | 7279304624253701434 | true
纸纹花字 | 7343445448100810025 | true
绿色立体花字 | 7298262240036146458 | true
伪三维拼贴纹理薄荷绿花字 | 7343820951823355170 | true
绿色渐变花字 | 7367375630180076850 | true
复古圆底花字 | 7345386966076165412 | true
蓝绿色渐变多层投影立体花字 | 7404137941632552202 | true
小清新绿色立体花字 | 7243593806409436474 | true
格子布纹花字 | 7260765133243288887 | true
绿色渐变白边花字 | 7404510647829957914 | true
毛毡薄荷绿花字 | 7346195217466363148 | true
古朴青 | 7224819211233676556 | true
绿色时尚 | 7280421022845668669 | true
青色 | 7370971660947705099 | true
绿色手绘涂鸦花字 | 7359509585222208778 | true
绿色渐变立体描边花字 | 7404713810730241319 | true
绿色渐变立体花字 | 7406323483690470696 | true
浅绿色白边花字 | 7282316784424865078 | true
黄绿格 | 7351685926277352723 | true
浅绿渐变立体花字 | 7298573839447903498 | true
麻将花字 | 7304160131338571044 | true
绿色描边立体花字 | 7405636378769313065 | true
综艺花字 | 7244834053323492611 | true
清风土黄花边可爱花字 | 7231522690144685315 | true
复古质感肌理花字 | 7404777605955734793 | true
韩综艺术 | 7245959768349691195 | true
清新点亮朦胧立体花字 | 7338390981055761704 | true
紫色立体文字 | 7405124477803171124 | true
赛博朋克故障字 | 7347627316031311115 | true
紫色渐变描边花字 | 7265622486312652047 | true
紫色多重描边字 | 7407080664236870964 | true
紫色渐变立体字 | 7406236406151925007 | true
蓝紫渐变花字 黑白描边花字 | 7241956897010552124 | true
紫色花字 | 7430766119671139595 | true
618紫色渐变立体字效 | 7507256223939530009 | true
紫色彩虹字 | 7236965265383230760 | true
紫色描边花字 | 7402066866572741927 | true
赛博故障风荧光花字 | 7405948653761744137 | true
故障风花字 | 7349028882974018835 | true
紫色立体字 | 7406657094851562792 | true
橙紫立体花字 | 7475389169183837502 | true
紫色蓝边立体花字 | 7389866725287709979 | true
紫红色描边立体花字 | 7424524996350905612 | true
紫色花字 | 7352837737730592015 | true
蓝紫渐变立体花字 | 7312852437327547658 | true
蓝粉纯色花字 | 7265657776012004648 | true
综艺潮流淡紫色渐变白边立体花字 | 7388023559047761191 | true
粉紫渐变立体花字 | 7312836005227302195 | true
紫色渐变投影字 | 7404055341010390324 | true
紫色立体发光花字 | 7430666396389969164 | true
蓝紫色渐变描边立体花字 | 7405053909191904566 | true
紫色闪烁花字 | 7265615178446720256 | true
白色立体描边花字 | 7405043787539549452 | true
星空 | 7241714501995875639 | true
星空 | 7231020400791129400 | true
白色描边立体花字 | 7405191566295420199 | true
渐变花字 | 7243961568067603744 | true
紫色渐变立体描边花字 | 7404673172978650431 | true
颜色渐变花字 | 7278520644478782775 | true
紫色渐变立体花字 | 7406011763457576201 | true
紫玫瑰 | 7481958256655486233 | true
多彩文字 | 7249741698094468412 | true
黄紫色描边花字 | 7274825472574262528 | true
紫红渐变透明字 | 7406974135018048820 | true
紫绿立体 | 7127673746902502670 | true
蓝紫色黑边花字 | 7252144476603403524 | true
发光粉赛博故障风立体花字 | 7405967249992879410 | true
科技花字 | 7351302252562337062 | true
星空之恋 | 7267344857406967096 | true
紫色渐变花字 | 7265636153896750336 | true
紫绿描边 | 7127822319824735519 | true
万圣节主题色描边花字 | 7404469048517414153 | true
星空花字 | 7399634464659279131 | true
浅紫色花字 | 7281948081925475644 | true
紫色立体字 | 7406649743616740642 | true
紫色渐变双色描边花字 | 7265635918487293219 | true
紫色立体花字 | 7244842014347545889 | true
简约双层描边渐变紫色花字 | 7434403828629245223 | true
紫色骷髅立体花字 | 7424527557699079487 | true
紫色花字音符纹理 | 7351056144141487375 | true
紫粉纯色花字 | 7265645422692109568 | true
紫色花字 | 7279303499140107581 | true
蓝紫渐变花字 | 7231341549659917625 | true
纯色紫色 | 7259998381869763851 | true
简约紫色花字 | 7268274152124075299 | true
粉色渐变立体花字 | 7296422791732071717 | true
紫色描边立体发光花字 | 7405210233917787446 | true
渐变花字 | 7289731248933850429 | true
粉紫渐变黑边边花字 | 7231466623775903032 | true
粉色渐变花字 | 7231026233994235173 | true
渐变花字 | 7289731761637002551 | true
国庆旅行-手绘紫 | 7283154062273465612 | true
紫色格子花字 | 7312021669739007232 | true
可爱莫兰迪粉紫花字 | 7254765522745675046 | true
白色斑点透明字体 | 7400682062262406426 | true
紫色花字 | 7430746445961022759 | true
浅紫星空花字 | 7231693783568551208 | true
粉紫纯色花字 | 7265651955123359011 | true
紫色格子立体花字 | 7231341416465714490 | true
圆点浅紫花字 | 7231001538473233723 | true
潮酷 黑色紫光 | 7020634468826238244 | false
可爱紫色立体花字 | 6927160254996172047 | false
清新白色蓝色描边花字 | 6926825801383939336 | false
紫色渐变立体花字 | 6896144127935696136 | false
梦幻渐变紫边白色发光花字 | 6896137661153643784 | false
潮酷紫色闪闪花字 | 6926827744189828359 | false
清新紫色立体字 | 6896143915192306958 | false
蓝紫渐变花字 | 7127655008715279647 | false
紫色投影立体字 | 6896144180993625357 | false
清新粉紫色立体花字 | 6896137727012506887 | false
```


---

## 附录 C 文字入场动画（145 条）

- 挂载位置：materials.material_animations[*].animations[*]
- 识别字段：type=in, material_type=sticker
- 草稿实际使用编号：effect_id + resource_id
- 免费 67 条，VIP 78 条
```text
name | effect_id | resource_id | is_vip | default_duration_sec
冲屏位移 | 1643884 | 7078181271393800711 | false | 0.5
卡拉OK | 1558840 | 6771294855785091588 | false | 0.5
变色输入 | 77035159 | 7397306443147252233 | false | 0.8
右上弹入 | 1621978 | 7074854080388010532 | false | 0.5
右下擦开 | 1715294 | 7088576340361744903 | false | 0.5
向上擦除 | 1644272 | 6774625910067827212 | false | 0.5
向上滑动 | 1644267 | 6763470111253729803 | false | 0.5
向上翻转 | 8945307 | 7194703971498332727 | false | 0.5
向上重叠 | 1639676 | 7077500533040222756 | false | 0.5
向上露出 | 5925717 | 7163514358935327268 | false | 0.5
向下擦除 | 1644273 | 6774626192990409224 | false | 0.5
向下滑动 | 1644268 | 6724921985282871816 | false | 0.5
向下露出 | 5925716 | 7163514502128865823 | false | 0.5
向下飞入 | 1719670 | 7088942186561016356 | false | 0.5
向右擦除 | 1644271 | 6771288500240126478 | false | 0.5
向右滑动 | 1644266 | 6724920136056181256 | false | 0.5
向右缓入 | 1488722 | 7043778124760224292 | false | 0.5
向右集合 | 1661186 | 7081206983461704199 | false | 0.5
向右露出 | 5925714 | 7163514730525495839 | false | 0.5
向左擦除 | 1644270 | 6774626830038077960 | false | 0.5
向左滑动 | 1644277 | 6763470195894784525 | false | 0.5
向左露出 | 5925715 | 7163514612690719269 | false | 0.5
圆形扫描 | 1644280 | 6840689010034086407 | false | 0.5
复古打字机 | 17639720 | 7253888335163167291 | false | 0.8
居中打字 | 20303987 | 7265222187286532667 | false | 0.5
左上弹入 | 1646760 | 7078586233030447629 | false | 0.5
左移弹动 | 35176342 | 7313890082040058406 | false | 1
开幕 | 1644279 | 6835571502050447879 | false | 0.5
弹入 | 1644313 | 6887482184844710413 | false | 0.5
弹弓 | 1644305 | 6862897343176380942 | false | 0.5
弹性伸缩 | 1644311 | 6872642189260755463 | false | 0.5
弹簧 | 1644312 | 6884154692398486023 | false | 0.5
彩色映射 | 1476514 | 7039655272222036516 | false | 0.5
打字机 I | 1644275 | 6724920249654710791 | false | 0.5
打字机 II | 1644276 | 6724920636403094028 | false | 0.5
打字机 III | 1644335 | 6724920521462387207 | false | 0.5
打字机IV | 14235879 | 7237409385092223525 | false | 2
扭曲模糊 | 1722114 | 7089261793406620197 | false | 0.5
拖尾 | 15259479 | 7244102915239973432 | false | 0.5
收拢 | 1644261 | 6779879712261935619 | false | 0.5
放大 | 1644264 | 6724919499042066958 | false | 0.5
故障打字机 | 1644308 | 6870061463243854350 | false | 0.5
旋入 | 1644265 | 6763873859402732039 | false | 0.5
日出 | 1644269 | 6779084126457696776 | false | 0.5
晕开 | 1714696 | 7088531060341871141 | false | 0.5
模糊 | 1644338 | 6923094735116571150 | false | 0.5
水墨晕开 | 22734325 | 7278295995362841145 | false | 1.2
水平翻转 | 1644340 | 7051512227353858590 | false | 0.5
波浪弹入 | 1644316 | 6917178744775905806 | false | 0.5
渐显 | 1644304 | 6724916044072227332 | false | 0.5
溶解 | 1644310 | 6872642398095151629 | false | 0.5
滑动上升 | 22226771 | 7275687883011265083 | false | 1.5
生长 | 1644307 | 6869302248103481869 | false | 0.5
甩出 | 15261071 | 7244102679851438650 | false | 0.9
站起 | 20324364 | 7265288917279052344 | false | 0.8
缩小 | 1644263 | 6724921217721045515 | false | 0.5
缩小 II | 1644341 | 7041836555903701540 | false | 0.5
羽化向右擦开 | 1644314 | 6897084405781631496 | false | 0.5
羽化向左擦开 | 1644315 | 6897084292908716557 | false | 0.5
翻动 | 32283659 | 7308278898330964489 | false | 1
轻微放大 | 1644262 | 6763469998330483213 | false | 0.5
逐字旋转 | 3114660 | 7111643562676064805 | false | 0.5
逐字显影 | 1644339 | 7038882772450021896 | false | 0.5
逐字翻转 | 3138860 | 7112241904216969765 | false | 0.5
闪动 | 1644322 | 7035902226602136071 | false | 0.5
随机弹跳 | 1644321 | 7021831463867781662 | false | 0.5
随机飞入 | 1644309 | 6872642542765085191 | false | 0.5
乱码故障 | 40877554 | 7325648367747338802 | true | 1
二段缩放 | 14394713 | 7238519092997526074 | true | 0.9
便利贴 | 31819229 | 7307207886843679283 | true | 0.8
倒数 | 35401566 | 7314303157360661018 | true | 1.8
兔子弹跳 | 8398145 | 7187785892382118461 | true | 0.5
冰雪飘动 | 35395178 | 7314291622525538843 | true | 1.5
发光模糊 | 1644342 | 7054482687297327630 | true | 0.5
发光闪入 | 32278776 | 7308272157442707978 | true | 1.8
叠影并入 | 19101418 | 7259634012774208059 | true | 1
向上弹入 | 3704299 | 7123116334677758501 | true | 0.5
向下溶解 | 1644318 | 7028458557058060831 | true | 0.5
向右模糊 II | 17830700 | 7254503374622560828 | true | 0.5
向左模糊 | 3147126 | 7112368349257929230 | true | 0.5
吸入 | 3576973 | 7120438380453696031 | true | 0.3
呐喊声波 | 9432429 | 7199943069385364005 | true | 0.5
喷绘 | 3563651 | 7120131223036367367 | true | 0.5
圆柱体滚动 | 7548913 | 7179035729043919397 | true | 1.2
圣诞帽弹跳 | 6492065 | 7169419861158793759 | true | 0.5
圣诞树弹跳II | 7080877 | 7174706243267727930 | true | 0.5
弹入跳动 | 8058189 | 7184797276181631546 | true | 0.5
弹性伸缩 II | 32279178 | 7308272646913790490 | true | 0.5
心动瞬间 | 44271866 | 7332519885999706663 | true | 1.65
慢速放大 | 10063675 | 7205177922280231479 | true | 60
打字光标 | 14235878 | 7237411357514011192 | true | 2
抖动甩入 | 29825712 | 7301945752278798885 | true | 0.5
折叠 | 3779439 | 7125298122011447816 | true | 0.5
描边填充 | 32278219 | 7308269965453300262 | true | 0.9
放大震动 | 20801300 | 7267849370727354936 | true | 0.5
故障闪动 | 15261571 | 7244101806710592057 | true | 2
新年打字机 | 21711818 | 7272754730684650045 | true | 1
旋转缩放 | 15140845 | 7243633588493619773 | true | 1.6
旋转飞入 | 1644274 | 6775803763652301326 | true | 0.5
星光闪闪 | 32665781 | 7309036302962266675 | true | 1.5
星光闪闪 II | 38428077 | 7319873264375829001 | true | 1
星星弹跳 | 31799385 | 7307189517562155547 | true | 1.1
模糊发光 | 29690460 | 7301535952101446170 | true | 1.8
模糊滚动 | 20154968 | 7264501462187643450 | true | 0.8
模糊缩小 | 27144470 | 7294147761765618186 | true | 1.5
汇聚 | 5529369 | 6986931575199896094 | true | 0.5
波浪弹跳 | 37303562 | 7317536986691015218 | true | 1
流光扩散 | 35505526 | 7314566361642963493 | true | 2
滚入 | 1644320 | 7026674824537707038 | true | 0.5
激光雕刻 | 15261101 | 7244102612700631589 | true | 3
爱心弹跳 | 1644337 | 6845191009861636616 | true | 0.5
玩雪 | 30904546 | 7304943429962699290 | true | 60
环绕滑入 | 19562189 | 7261858654561767973 | true | 1
生长 II | 10659499 | 7210312869282320933 | true | 0.8
电光 | 27769111 | 7296051582246851109 | true | 1.5
电光 II | 28928614 | 7299364098788037171 | true | 1
碰碰车 | 47157536 | 7338602211041088027 | true | 0.6
空翻 | 1644306 | 6865175746420150792 | true | 0.5
缤纷冲屏 | 3894473 | 7116829842271638053 | true | 2
缩放 III | 10743073 | 7211036012401660473 | true | 1.6
翻页II | 6599721 | 7170343439832191519 | true | 1.2
背景滑入 | 31601883 | 7306794354255860250 | true | 1.5
色散拖影 | 48159236 | 7340513927651922458 | true | 1.1
螺旋上升 | 1644278 | 6799873891352187406 | true | 0.5
跃进 | 11996999 | 7220685840442200634 | true | 1.2
跳跳捣蛋鬼 | 9503089 | 7200340219109839419 | true | 1.8
跳跳糖 | 42866461 | 7329815894933115432 | true | 1.267
辉光 | 18786330 | 7258179345192063525 | true | 1
辉光扫描 | 36927710 | 7316878401590006323 | true | 1.8
逐字弹跳 | 9195301 | 7197615431673188921 | true | 0.5
逐字旋入 | 13137035 | 7229520427196879421 | true | 1.5
金粉飘落 | 43242964 | 7330561002922054196 | true | 2
镂空跳入 | 33984693 | 7311620091060163082 | true | 1.2
闪烁集合 | 20805754 | 7267886380439573029 | true | 1.5
随机上升 | 13720553 | 7233662263805088314 | true | 1.5
随机弹跳 II | 3241034 | 7114189305781686797 | true | 0.5
随机打字机 | 1644317 | 6926718978064650760 | true | 0.5
随机落下 | 13416707 | 7231443875406025275 | true | 1.2
随机集合 | 12416139 | 7223959789175312954 | true | 2.5
雪光模糊 | 35545508 | 7314614905196253705 | true | 1.2
音符弹跳 | 1644336 | 6841115718172283406 | true | 0.5
顶出 | 20880936 | 7268221856618910264 | true | 1.1
预览打字 | 20853726 | 7268152375536259639 | true | 0.8
飞入 | 1644319 | 7029231035007111710 | true | 0.5
鼠标点击 | 53149407 | 7350128013637325353 | true | 1.65
```


---

## 附录 D 文字出场动画（97 条）

- 挂载位置：materials.material_animations[*].animations[*]
- 识别字段：type=out, material_type=sticker
- 草稿实际使用编号：effect_id + resource_id
- 免费 51 条，VIP 46 条
```text
name | effect_id | resource_id | is_vip | default_duration_sec
右上弹出 | 1631524 | 7076006676951732767 | false | 0.5
右下擦除 | 1729286 | 7090146831836910110 | false | 0.5
向上擦除 | 1644609 | 6774625752794010115 | false | 0.5
向上溶解 | 1644655 | 7026619708627489293 | false | 0.5
向上滑动 | 1644605 | 6763873533115240968 | false | 0.5
向下擦除 | 1644610 | 6774626081791021576 | false | 0.5
向下滑动 | 1644606 | 6724919284893487619 | false | 0.5
向右擦除 | 1644615 | 6783908820176343566 | false | 0.5
向右滑动 | 1644614 | 6724920744431587853 | false | 0.5
向右缓出 | 1451688 | 7023684632591733284 | false | 0.5
向左擦除 | 1644608 | 6774626748177846791 | false | 0.5
向左滑动 | 1644613 | 6763873602476446221 | false | 0.5
向左解散 | 1674332 | 7083752251742753287 | false | 0.5
圆形扫描 | 1644617 | 6840698265277567496 | false | 0.5
居中打字 | 20304017 | 7265222263174074937 | false | 0.5
展开 | 1644599 | 6779879836916650509 | false | 0.5
左上弹出 | 1646758 | 7078587337998864926 | false | 0.5
左移弹动 | 35176386 | 7313890212529050138 | false | 1
弹出 | 1644648 | 6887482090351235592 | false | 0.5
弹弓 | 1644618 | 6862897350478664200 | false | 0.5
弹性伸缩 | 1644646 | 6872642084977775118 | false | 0.5
弹簧 | 1644647 | 6884154487246688776 | false | 0.5
打字机 I | 1644611 | 6763469696260903435 | false | 0.5
打字机 II | 1644612 | 6763469767555682823 | false | 0.5
打字机 III | 1644664 | 6763469838368117256 | false | 0.5
扭曲模糊 | 1729226 | 7090122015603954189 | false | 0.5
拖尾 | 15260277 | 7244102819731477049 | false | 0.5
放大 | 1644603 | 6724919767200698884 | false | 0.5
放大 II | 1644666 | 7042278078415901192 | false | 0.5
故障打字机 | 1644643 | 6870061326698287624 | false | 0.5
旋出 | 1644604 | 6763873732143354376 | false | 0.5
日落 | 1644607 | 6779084194392838670 | false | 0.5
晕开 | 1727994 | 7090059095134179877 | false | 0.5
模糊 | 1644652 | 6923094772907250189 | false | 0.5
水墨晕开 | 22734371 | 7278296130432012857 | false | 1.2
水平翻转 | 1644667 | 7052633346936934942 | false | 0.5
波浪弹出 | 1644651 | 6917178803521327630 | false | 0.5
渐隐 | 1644600 | 6724919382104871427 | false | 0.5
溶解 | 1644645 | 6872642354898014728 | false | 0.5
滑动下落 | 21330850 | 7270726693277405733 | false | 1.5
生长 | 1644642 | 6869302139584254477 | false | 0.5
缩小 | 1644602 | 6724921351385125387 | false | 0.5
羽化向右擦除 | 1644649 | 6897085341811872270 | false | 0.5
羽化向左擦除 | 1644650 | 6897085246206906893 | false | 0.5
翻动 | 32283993 | 7308279288061497865 | false | 1
躺下 | 20324365 | 7265288999470633509 | false | 0.8
轻微放大 | 1644601 | 6763469915518145032 | false | 0.5
闪动 | 1644658 | 7039245189638001183 | false | 0.5
闭幕 | 1644616 | 6834511218552607239 | false | 0.5
随机弹跳 | 1644665 | 7026617357300666893 | false | 0.5
随机飞出 | 1644644 | 6872642497013617159 | false | 0.5
二段缩放 | 14394793 | 7238519014866031162 | true | 1.5
发光闪出 | 32281161 | 7308275717505028617 | true | 1.8
叠影并出 | 19101496 | 7259634082760364603 | true | 1
向上飞出 | 1730928 | 7090139631861109278 | true | 0.5
向下弹出 | 3859743 | 7127158940151845390 | true | 0.5
向下翻转 | 9282213 | 7198395913948107301 | true | 0.5
向左模糊 | 3176752 | 7112703727336690189 | true | 0.5
向左模糊 II | 17830676 | 7254503584732025381 | true | 0.5
吸出 | 3647465 | 7121986743141667358 | true | 0.3
喷绘 | 3563649 | 7120131305303446029 | true | 0.5
复古打字机 | 17250228 | 7252619798108967484 | true | 0.8
弹出跳动 | 8058215 | 7184797189627974200 | true | 0.5
弹性伸缩 II | 32281815 | 7308276711039177225 | true | 0.5
打字光标 | 14235852 | 7237411511755346491 | true | 2
打字机IV | 14235853 | 7237411448303915557 | true | 2
折叠 | 3769517 | 7124961998919438884 | true | 0.5
描边填充 | 32279531 | 7308273254127374874 | true | 0.9
收缩震动 | 20877442 | 7268214314022998588 | true | 0.5
故障 | 1789138 | 7091567288385540622 | true | 0.5
故障闪动 | 15261509 | 7244102414377161276 | true | 2
旋转缩放 | 15140857 | 7243633648237285949 | true | 1.6
旋转飞出 | 1644639 | 6775804032318444045 | true | 0.5
模糊发光 | 29690520 | 7301536173959156274 | true | 1.8
模糊滚动 | 20154980 | 7264501549240422949 | true | 0.8
波浪弹跳 | 37396324 | 7317637880799564297 | true | 1
消散 | 5323563 | 7155790075794559525 | true | 0.5
滚出 | 1644656 | 7023684709737566728 | true | 0.5
激光雕刻 | 15261103 | 7244102529573720635 | true | 1.2
炸开 | 4577477 | 7142816577971294734 | true | 0.5
炸开 II | 4834739 | 7148309755121898015 | true | 0.5
炸开 Ⅲ | 32280237 | 7308274161992864266 | true | 1.2
环绕滑出 | 19562193 | 7261858590808347193 | true | 1
甩回 | 15261069 | 7244102747698500156 | true | 0.6
空翻 | 1644641 | 6865176065514410503 | true | 0.5
螺旋下降 | 1644640 | 6799874105710481927 | true | 0.5
逐字旋出 | 13137113 | 7229520513586958908 | true | 1.5
逐字旋转 | 3129838 | 7112021029085516319 | true | 0.5
逐字翻转 | 3139394 | 7112274846326723086 | true | 0.5
逐字虚影 | 1644657 | 7034717113130422791 | true | 0.5
镂空跳出 | 34383204 | 7312331703903588902 | true | 1.2
闪烁散开 | 20860262 | 7268169968204649020 | true | 1
随机弹跳 II | 3241116 | 7114191629346411016 | true | 0.5
随机打字机 | 1644653 | 6926719087158497806 | true | 0.5
顶出 | 20882164 | 7268231069768356408 | true | 1.1
预览打字 | 20878188 | 7268216065337856572 | true | 0.8
飞出 | 1644654 | 7029522072724312612 | true | 0.5
```


---

## 附录 E 文字循环动画（93 条）

- 挂载位置：materials.material_animations[*].animations[*]
- 识别字段：type=loop, material_type=sticker
- 草稿实际使用编号：effect_id + resource_id
- 免费 41 条，VIP 52 条
```text
name | effect_id | resource_id | is_vip | default_duration_sec
VHS | 77851352 | 7399879467457319463 | false | 2
上弧 | 1626238 | 7075224569421763079 | false | 0.5
刷屏 | 32284703 | 7308280358691148315 | false | 0.5
发光模糊多行 | 77132594 | 7397688001356108339 | false | 0.8
吹泡泡 | 1644539 | 7045155566003425823 | false | 0.5
吹泡泡 II | 1644528 | 7052257626897256968 | false | 0.5
呐喊 | 4002167 | 7119024816480326157 | false | 0.5
复古涂鸦 | 77997810 | 7400234025392017956 | false | 1
字体变换 | 78763194 | 7402185694732358170 | false | 0.8
弹幕滚动 | 1644518 | 6790247082155315719 | false | 0.5
彩虹 | 990096 | 6908592625406710280 | false | 0.5
彩虹-情人节 | 1012617 | 6916820108211917325 | false | 0.5
彩虹-新年 | 1012618 | 6916820045519655432 | false | 0.5
彩虹-马卡龙 | 1022790 | 6921528300573561358 | false | 0.5
扫光 | 1520868 | 7051843475892867598 | false | 0.5
投影颤抖 II | 1599696 | 7070332370963927559 | false | 0.5
折叠 | 1567212 | 7064823078542381581 | false | 0.5
拼贴纹理 | 77918388 | 7399983060806013479 | false | 0.8
描边粉笔 | 77851433 | 7399879712140431883 | false | 2
摇摆 | 1644515 | 6724920869363126795 | false | 0.5
摇荡 | 1644523 | 6840710593289130503 | false | 0.5
故障闪动 | 1644524 | 6857714281136263687 | false | 0.5
旋转 | 1644510 | 6763900973946507784 | false | 0.5
晃动 | 1644520 | 6790246693674684942 | false | 0.5
爆闪 | 32284413 | 7308279705252139530 | false | 0.5
环绕 | 1644542 | 6980916124976157220 | false | 0.5
翻转 | 1644511 | 6763897586328801805 | false | 0.5
色差故障 | 1644522 | 6835878163575214605 | false | 0.5
蓝黄滑动 | 77383265 | 7398492769628459539 | false | 2
超强晃动 | 1568854 | 7065208406633615909 | false | 0.5
超强晃动 II | 1597286 | 7069965879437431303 | false | 0.5
超强波浪 | 872098 | 6857036499389518349 | false | 0.5
超强波浪 II | 1568964 | 7065219379687854623 | false | 0.5
跳动 | 1644512 | 6724920002958332420 | false | 0.5
轻微跳动 | 1644525 | 6884155832838132231 | false | 0.5
钟摆 | 1644516 | 6724921579517514248 | false | 0.5
闪烁 | 1644514 | 6724921437930394120 | false | 0.5
雨刷 | 1644521 | 6799874389669057037 | false | 0.5
频闪边框 | 32284883 | 7308280718302384690 | false | 0.5
颤抖 | 1644509 | 6764189482871689742 | false | 0.5
颤抖 III | 1598082 | 7070036604429013535 | false | 0.5
加字符 | 93688629 | 7441532971082846758 | true | 0.8
喷涌 | 4175399 | 7134190113780666887 | true | 0.5
喷绘 | 2999942 | 7110160318529016350 | true | 0.5
圆形涂鸦 | 22362181 | 7276420462131810874 | true | 0.8
声波震动 | 14518651 | 7239526343833031223 | true | 2
字幕滚动 | 1644519 | 6790246884683289102 | true | 0.5
尾巴摇摆 | 10967121 | 7212897307782550053 | true | 1.6
弹幕 | 2795622 | 7107592133472686606 | true | 0.5
弹幕 II | 1826548 | 7096375845773644318 | true | 0.5
强调三遍 | 3966601 | 7129767866894651917 | true | 0.5
彩色切换 | 30322872 | 7303430211519910451 | true | 1.5
彩色火焰 | 32283417 | 7308278472541999654 | true | 0.5
影像叠加 | 8882439 | 7193989785319379515 | true | 0.5
心跳 | 10650869 | 7210283971316290085 | true | 1.5
急了 | 4200435 | 7134634461588623909 | true | 2.4
悸动 | 13139395 | 7229526981807706680 | true | 1.2
情绪加载 | 3983735 | 7130142075995034119 | true | 2.2
扩音器 | 22619881 | 7277870806552547895 | true | 1.2
扭动 | 3733565 | 7123093247672455711 | true | 0.5
投影颤抖 | 1599698 | 7070332284934558245 | true | 0.5
抖动故障 | 23998441 | 7283103017526628921 | true | 0.8
拉住 | 12135594 | 7221747595884892731 | true | 1.2
拉开 | 12390761 | 7223675733606928957 | true | 60
排队入场 | 12628547 | 7225496399817740855 | true | 1
摇摆 I | 1520478 | 6908281696253121038 | true | 0.5
放大缩小 | 12453543 | 7224077152587616805 | true | 0.5
放大镜 | 21635790 | 7272339163142165050 | true | 0.8
文字泛光 | 3740251 | 7124226995231134239 | true | 0.5
波浪 | 1644517 | 6724927688047333891 | true | 0.5
波浪 II | 1576246 | 7067046171381862919 | true | 0.5
波浪 III | 1583302 | 7067812686557352456 | true | 0.5
流光 | 32283005 | 7308277700492268042 | true | 1.6
涂鸦手绘 | 22361305 | 7276407256965452346 | true | 0.5
涂鸦手绘 II | 22361304 | 7276407576625943100 | true | 0.5
渐变拖尾 | 32282151 | 7308277117622424090 | true | 0.8
漂浮 | 11017729 | 7213291988500615738 | true | 1.5
漩涡 | 1936778 | 7099419657290912286 | true | 0.5
环形滚动 | 7564487 | 7179135028343870012 | true | 1.2
环绕 II | 3240866 | 7114181846086193701 | true | 0.5
甜甜圈 | 1600378 | 7070415354656199181 | true | 0.5
福袋炸开 | 1531460 | 7047088638932292127 | true | 1.5
空间翻转 I | 5965291 | 7163896186972148261 | true | 1.5
空间翻转 II | 5966503 | 7163901901589713444 | true | 1.1
空间翻转 III | 5964737 | 7163892769176424991 | true | 0.5
竖向渐变 | 87963946 | 7430669972088558090 | true | 2.2
翻页I | 6443365 | 7168819879183651359 | true | 1.2
调皮 | 1644527 | 6917143282690560526 | true | 0.5
逐字放大 | 1644526 | 6908592686781960717 | true | 0.5
错位 | 15140783 | 7243633488249754173 | true | 3
随机弹跳 | 1644538 | 7045150354672980516 | true | 0.5
颤抖 II | 1446098 | 6986920909927879199 | true | 0.5
飘起 | 10749797 | 7211060597352305189 | true | 3
```


---

## 附录 F 滤镜清单（1052 条）

- 挂载位置：materials.effects[type=filter]
- 草稿实际使用编号：effect_id + resource_id
- params 是草稿最终参数名与数值范围；如果走外部接口，通常会先把 0-100 映射到这里的 min/max
- 免费 250 条，VIP 802 条
```text
name | effect_id | resource_id | is_vip | params
1980 | 7127828208690433311 | 7127828208690433311 | false | -
ABG | 7127679308897832206 | 7127679308897832206 | false | -
Ditto | 7195816046077496635 | 7195816046077496635 | false | -
KE1 | 7127819154018536741 | 7127819154018536741 | false | -
KV5D | 7127578859217620254 | 7127578859217620254 | false | -
Lofi II | 7232216810031025468 | 7232216810031025468 | false | -
VHS III | 7127669764905782542 | 7127669764905782542 | false | -
三洋VPC | 7127669338089311495 | 7127669338089311495 | false | -
书意 | 7368493100127292723 | 7368493100127292723 | false | effects_adjust_filter(default=1,min=0,max=1)
亢奋 | 7166472327801097476 | 7166472327801097476 | false | -
亮夏 | 7505804389395877120 | 7505804389395877120 | false | effects_adjust_filter(default=1,min=0,max=1)
亮肤 | 7127655008715230495 | 7127655008715230495 | false | -
仲夏绿光 | 7127675970252754189 | 7127675970252754189 | false | -
似锦 | 7188014191834418493 | 7188014191834418493 | false | -
低保真 | 7304170509661506843 | 7304170509661506843 | false | -
侘寂灰 | 7127609569416711455 | 7127609569416711455 | false | -
元气新年 | 7457859598221987110 | 7457859598221987110 | false | effects_adjust_filter(default=1,min=0,max=1)
克洛伊 | 7366640728493002018 | 7366640728493002018 | false | effects_adjust_filter(default=1,min=0,max=1)
冬日烧烤 | 7449704838763466035 | 7449704838763466035 | false | effects_adjust_filter(default=1,min=0,max=1)
冬漫 | 7302324323270872346 | 7302324323270872346 | false | -
冬离 | 7300786822068571418 | 7300786822068571418 | false | -
冰火 | 7303812389177265447 | 7303812389177265447 | false | -
冰肌 | 7199089344756370743 | 7199089344756370743 | false | -
冷气机 | 7263359186883366155 | 7263359186883366155 | false | -
冷白 | 7127614731187178783 | 7127614731187178783 | false | -
冷蓝 | 7127618237117877518 | 7127618237117877518 | false | -
净白肤 | 7411580367452376361 | 7411580367452376361 | false | effects_adjust_filter(default=1,min=0,max=1)
凛冬 | 7449996162343390473 | 7449996162343390473 | false | effects_adjust_filter(default=1,min=0,max=1)
凝黛 | 7298279202350976282 | 7298279202350976282 | false | effects_adjust_filter(default=1,min=0,max=1)
初恋 | 7195812984306814267 | 7195812984306814267 | false | -
千玺IXU | 7127824119294364959 | 7127824119294364959 | false | -
千里江山 | 7208495854938901793 | 7208495854938901793 | false | -
千金妝 | 7370585884078443802 | 7370585884078443802 | false | effects_adjust_filter(default=1,min=0,max=1)
卡露尔 | 7301224597033192716 | 7301224597033192716 | false | -
即刻春光 | 7127675868641594654 | 7127675868641594654 | false | -
原木 | 7127675195812351239 | 7127675195812351239 | false | -
去黄增质 | 7438854064458239258 | 7438854064458239258 | false | effects_adjust_filter(default=1,min=0,max=1)
去黄提亮 | 7438853477616340250 | 7438853477616340250 | false | effects_adjust_filter(default=1,min=0,max=1)
古早韩系 | 7462953965160893723 | 7462953965160893723 | false | effects_adjust_filter(default=1,min=0,max=1)
古早韩风 | 7473168869222370571 | 7473168869222370571 | false | effects_adjust_filter(default=1,min=0,max=1)
古罗马 | 7242212640498568503 | 7242212640498568503 | false | -
古风影视 | 7404104823563472137 | 7404104823563472137 | false | effects_adjust_filter(default=1,min=0,max=1)
告白 | 7437136821512949007 | 7437136821512949007 | false | effects_adjust_filter(default=1,min=0,max=1)
喜市 | 7185440129442417931 | 7185440129442417931 | false | -
喜庆胶片 | 7451265649273261363 | 7451265649273261363 | false | effects_adjust_filter(default=1,min=0,max=1)
四喜 | 7312102522733268251 | 7312102522733268251 | false | -
圣诞灯光 | 7429295645669756195 | 7429295645669756195 | false | effects_adjust_filter(default=1,min=0,max=1)
圣诞灯光II | 7429295455953046818 | 7429295455953046818 | false | effects_adjust_filter(default=1,min=0,max=1)
圣诞灯光III | 7429296137275755810 | 7429296137275755810 | false | effects_adjust_filter(default=1,min=0,max=1)
复古工业 | 7127608212483820837 | 7127608212483820837 | false | -
夏日小美好 | 7494125821032975642 | 7494125821032975642 | false | effects_adjust_filter(default=1,min=0,max=1)
夏日清凉 | 7505632228659973416 | 7505632228659973416 | false | effects_adjust_filter(default=1,min=0,max=1)
夏日辣妹 | 7502729392179776779 | 7502729392179776779 | false | effects_adjust_filter(default=1,min=0,max=1)
夏日风吟 | 7127684611802418445 | 7127684611802418445 | false | -
大唐盛世 | 7493423027670109449 | 7493423027670109449 | false | effects_adjust_filter(default=1,min=0,max=1)
奈良 | 7351684015906147621 | 7351684015906147621 | false | -
奥本海默 | 7271142654505766183 | 7271142654505766183 | false | -
奶杏 | 7297134192100379938 | 7297134192100379938 | false | -
奶油 | 7127618513048571173 | 7127618513048571173 | false | -
奶油肤 | 7463296170950020403 | 7463296170950020403 | false | effects_adjust_filter(default=1,min=0,max=1)
奶绿 | 7127684319300029733 | 7127684319300029733 | false | -
姜饼红 | 7127624030135389471 | 7127624030135389471 | false | -
威尼之都 | 7406553962922429735 | 7406553962922429735 | false | effects_adjust_filter(default=1,min=0,max=1)
安愉 | 7190242827543022880 | 7190242827543022880 | false | -
宫崎漫夏 | 7500223670678228262 | 7500223670678228262 | false | effects_adjust_filter(default=1,min=0,max=1)
富士CC II | 7268561903721401641 | 7268561903721401641 | false | -
寻荷 | 7295362817874480425 | 7295362817874480425 | false | -
小镇 | 7127654151688965384 | 7127654151688965384 | false | -
山系 | 7127662738884545806 | 7127662738884545806 | false | -
巧克力 | 7363220647767592243 | 7363220647767592243 | false | -
布兰卡 | 7242208887883992381 | 7242208887883992381 | false | -
布朗 | 7273777590102527290 | 7273777590102527290 | false | -
希望 | 7271141541521968396 | 7271141541521968396 | false | -
幽蓝 | 7330441280016715062 | 7330441280016715062 | false | effects_adjust_filter(default=1,min=0,max=1)
彩果 | 7175101541198679353 | 7175101541198679353 | false | -
彩檐 | 7226234868059917628 | 7226234868059917628 | false | -
影叙 | 7349953761059638555 | 7349953761059638555 | false | -
微澜 | 7338406163848940840 | 7338406163848940840 | false | effects_adjust_filter(default=1,min=0,max=1)
德古拉 | 7127678346472819982 | 7127678346472819982 | false | -
快照I | 7143537677655100709 | 7143537677655100709 | false | -
忽风 | 7330123964305378586 | 7330123964305378586 | false | -
情感电影 | 7505461557237730598 | 7505461557237730598 | false | effects_adjust_filter(default=1,min=0,max=1)
情绪电影 | 7420000959759224118 | 7420000959759224118 | false | effects_adjust_filter(default=1,min=0,max=1)
扫街 | 7376146305736822028 | 7376146305736822028 | false | effects_adjust_filter(default=1,min=0,max=1)
探店博主III | 7411911267859860746 | 7411911267859860746 | false | effects_adjust_filter(default=1,min=0,max=1)
摩卡灰 | 7437011056653847808 | 7437011056653847808 | false | effects_adjust_filter(default=1,min=0,max=1)
敦刻尔克 | 7127568601921408293 | 7127568601921408293 | false | -
料理 | 7127656350833806622 | 7127656350833806622 | false | -
新年电影 | 7445550576210873663 | 7445550576210873663 | false | effects_adjust_filter(default=1,min=0,max=1)
新闪 | 7342395072199019803 | 7342395072199019803 | false | effects_adjust_filter(default=1,min=0,max=1)
日出 | 7325383700240256296 | 7325383700240256296 | false | -
日系奶油 | 7127664177870671135 | 7127664177870671135 | false | -
日落橘 | 7127669630667066655 | 7127669630667066655 | false | -
日落飞车 | 7505662247407013135 | 7505662247407013135 | false | effects_adjust_filter(default=1,min=0,max=1)
旧乐园 | 7239977329668263227 | 7239977329668263227 | false | -
旧时代I | 7232218563270954300 | 7232218563270954300 | false | -
明晰 | 7367715162964446516 | 7367715162964446516 | false | effects_adjust_filter(default=1,min=0,max=1)
星云 | 7127672042069036319 | 7127672042069036319 | false | -
春日绿妍 | 7463345622440037658 | 7463345622440037658 | false | effects_adjust_filter(default=1,min=0,max=1)
昭和夏 | 7505660075252485376 | 7505660075252485376 | false | effects_adjust_filter(default=1,min=0,max=1)
晴好春日 | 7468552996008299791 | 7468552996008299791 | false | effects_adjust_filter(default=1,min=0,max=1)
晴沐 | 7342503492311076137 | 7342503492311076137 | false | effects_adjust_filter(default=1,min=0,max=1)
晴研 | 7472763263684578572 | 7472763263684578572 | false | effects_adjust_filter(default=1,min=0,max=1)
晴颜 | 7297968738131873035 | 7297968738131873035 | false | -
暖食 | 7127653100269210916 | 7127653100269210916 | false | -
暗夜 | 7127823728070659358 | 7127823728070659358 | false | -
暗调氛围 | 7463118934061993242 | 7463118934061993242 | false | effects_adjust_filter(default=1,min=0,max=1)
暗雅 | 7127656352410848548 | 7127656352410848548 | false | -
暮光 | 7242211155131862332 | 7242211155131862332 | false | -
暮色 | 7127594686541237535 | 7127594686541237535 | false | -
月升之国 | 7127819487419567373 | 7127819487419567373 | false | -
月夜 | 7143532202112912670 | 7143532202112912670 | false | -
未央 | 7340282260312182050 | 7340282260312182050 | false | effects_adjust_filter(default=1,min=0,max=1)
朱栗 | 7299055174880988479 | 7299055174880988479 | false | effects_adjust_filter(default=1,min=0,max=1)
松果棕 | 7127669342325443854 | 7127669342325443854 | false | -
林间 | 7127663793827564808 | 7127663793827564808 | false | -
柠檬青 | 7127676358766923016 | 7127676358766923016 | false | -
梵时 | 7341767383259942155 | 7341767383259942155 | false | effects_adjust_filter(default=1,min=0,max=1)
棕咖 | 7273779209934245179 | 7273779209934245179 | false | -
棕宥 | 7332348414933421366 | 7332348414933421366 | false | effects_adjust_filter(default=1,min=0,max=1)
棠梨 | 7329819965920398604 | 7329819965920398604 | false | -
椰林 | 7252674515287788856 | 7252674515287788856 | false | -
椿和 | 7341032461234654475 | 7341032461234654475 | false | effects_adjust_filter(default=1,min=0,max=1)
椿来 | 7347729407181704498 | 7347729407181704498 | false | -
樱粉 | 7127632545272925470 | 7127632545272925470 | false | -
比佛利 | 7127657040348040479 | 7127657040348040479 | false | -
气泡水 | 7127619120761212168 | 7127619120761212168 | false | -
江浙沪 | 7127838224344435981 | 7127838224344435981 | false | -
治愈萌宠 | 7454497262480231718 | 7454497262480231718 | false | effects_adjust_filter(default=1,min=0,max=1)
泥金 | 7208495760520842529 | 7208495760520842529 | false | -
活力夏 | 7493764749054709001 | 7493764749054709001 | false | effects_adjust_filter(default=1,min=0,max=1)
流光金属 | 7127675565779307789 | 7127675565779307789 | false | -
浅岛 | 7281163331245821239 | 7281163331245821239 | false | -
浪漫烟火 | 7446098658942078258 | 7446098658942078258 | false | effects_adjust_filter(default=1,min=0,max=1)
浮生 | 7340687187194678569 | 7340687187194678569 | false | effects_adjust_filter(default=1,min=0,max=1)
海浪梦境 | 7401018435674688787 | 7401018435674688787 | false | effects_adjust_filter(default=1,min=0,max=1)
海街日记 | 7127615915004366116 | 7127615915004366116 | false | -
海雾 | 7189595107610447163 | 7189595107610447163 | false | -
海鸥DC | 7127830050786823437 | 7127830050786823437 | false | -
深沉 | 7414897963752770828 | 7414897963752770828 | false | effects_adjust_filter(default=1,min=0,max=1)
深秋 | 7295596083101633842 | 7295596083101633842 | false | -
深褐 | 7127615347703811336 | 7127615347703811336 | false | -
清冷 | 7405602958748028186 | 7405602958748028186 | false | effects_adjust_filter(default=1,min=0,max=1)
清冷冬日 | 7449939213430082867 | 7449939213430082867 | false | effects_adjust_filter(default=1,min=0,max=1)
清新 | 7469310117079420211 | 7469310117079420211 | false | effects_adjust_filter(default=1,min=0,max=1)
清新漫和 | 7480517561486953779 | 7480517561486953779 | false | effects_adjust_filter(default=1,min=0,max=1)
清明上河 | 7208495962887621899 | 7208495962887621899 | false | -
清晰明亮 | 7433813603758722342 | 7433813603758722342 | false | effects_adjust_filter(default=1,min=0,max=1)
清晰烟花 | 7448652759869525287 | 7448652759869525287 | false | effects_adjust_filter(default=1,min=0,max=1)
清澈 | 7359419156619332902 | 7359419156619332902 | false | -
清透自然 | 7482047649831570726 | 7482047649831570726 | false | effects_adjust_filter(default=1,min=0,max=1)
温述 | 7351580023742090535 | 7351580023742090535 | false | -
港历 | 7346017304909581587 | 7346017304909581587 | false | -
港风 | 7127830945243090184 | 7127830945243090184 | false | -
演唱会 | 7396701250764426546 | 7396701250764426546 | false | effects_adjust_filter(default=1,min=0,max=1)
漫夏 | 7366616947703991571 | 7366616947703991571 | false | effects_adjust_filter(default=1,min=0,max=1)
漫彩 | 7177269429972045089 | 7177269429972045089 | false | -
漫春 | 7332866997128105228 | 7332866997128105228 | false | effects_adjust_filter(default=1,min=0,max=1)
漫步 | 7263357613050563852 | 7263357613050563852 | false | -
漫谷 | 7312002825054211378 | 7312002825054211378 | false | -
烈焰红 | 7409669784155000090 | 7409669784155000090 | false | effects_adjust_filter(default=1,min=0,max=1)
烘培 | 7127675183246200072 | 7127675183246200072 | false | -
烟岚 | 7341204799590763788 | 7341204799590763788 | false | effects_adjust_filter(default=1,min=0,max=1)
烟火增色 | 7446098755905965338 | 7446098755905965338 | false | effects_adjust_filter(default=1,min=0,max=1)
烟花增强 | 7444905127871270181 | 7444905127871270181 | false | effects_adjust_filter(default=1,min=0,max=1)
烟霞 | 7143533042978524424 | 7143533042978524424 | false | -
熔金 | 7143575737881120037 | 7143575737881120037 | false | -
燃力 | 7248571956860079395 | 7248571956860079395 | false | -
牛皮纸 | 7127822013074263310 | 7127822013074263310 | false | -
珠光蓝 | 7127657509501914399 | 7127657509501914399 | false | -
珠落 | 7213575938615872823 | 7213575938615872823 | false | -
疼痛文学 | 7453868314482298122 | 7453868314482298122 | false | effects_adjust_filter(default=1,min=0,max=1)
病娇 | 7291179909718740259 | 7291179909718740259 | false | -
白皙 | 7127668617147141413 | 7127668617147141413 | false | -
盐岚 | 7359223280714239268 | 7359223280714239268 | false | -
矿野 | 7281162649314889015 | 7281162649314889015 | false | -
砂红 | 7300758676732677427 | 7300758676732677427 | false | -
砾绀 | 7340915058542759219 | 7340915058542759219 | false | effects_adjust_filter(default=1,min=0,max=1)
空灵 | 7353555308448419098 | 7353555308448419098 | false | -
空谷 | 7143532176313699620 | 7143532176313699620 | false | -
竹绢 | 7208496463293320480 | 7208496463293320480 | false | -
米棕 | 7221477781043973413 | 7221477781043973413 | false | -
粉瓷 | 7127667757998411044 | 7127667757998411044 | false | -
粉肤 | 7296493947625557286 | 7296493947625557286 | false | -
粹光 | 7373693828328475941 | 7373693828328475941 | false | effects_adjust_filter(default=1,min=0,max=1)
素肌 | 7127671162758270245 | 7127671162758270245 | false | -
红绿 | 7127622617699290399 | 7127622617699290399 | false | -
绝对红 | 7127667361456426248 | 7127667361456426248 | false | -
绿妍 | 7127675252410223909 | 7127675252410223909 | false | -
美味 | 7414142998075690279 | 7414142998075690279 | false | effects_adjust_filter(default=1,min=0,max=1)
老友记 | 7127669912050420999 | 7127669912050420999 | false | -
胡桃木 | 7127830961621847310 | 7127830961621847310 | false | -
自然 | 7127821314198342943 | 7127821314198342943 | false | -
自然清晰 | 7412691247992671497 | 7412691247992671497 | false | effects_adjust_filter(default=1,min=0,max=1)
自由 | 7271143155544739108 | 7271143155544739108 | false | -
臻金 | 7306726303594564904 | 7306726303594564904 | false | -
花园 | 7226990672190950713 | 7226990672190950713 | false | -
花椿 | 7127539889553427719 | 7127539889553427719 | false | -
花火 | 7175071186185964812 | 7175071186185964812 | false | -
花火夜焰 | 7460022261144177957 | 7460022261144177957 | false | effects_adjust_filter(default=1,min=0,max=1)
花花世界 | 7505429510930730275 | 7505429510930730275 | false | effects_adjust_filter(default=1,min=0,max=1)
落日 | 7166494058305670432 | 7166494058305670432 | false | -
落日海岛 | 7369501986401570099 | 7369501986401570099 | false | effects_adjust_filter(default=1,min=0,max=1)
落日飞车 | 7350133636890463498 | 7350133636890463498 | false | -
落牧 | 7375415880118783295 | 7375415880118783295 | false | effects_adjust_filter(default=1,min=0,max=1)
蒸汽波 | 7127671519450320159 | 7127671519450320159 | false | -
薄荷 | 7343782317820857641 | 7343782317820857641 | false | effects_adjust_filter(default=1,min=0,max=1)
褪色 | 7127668404764380447 | 7127668404764380447 | false | -
西野 | 7331590962696834313 | 7331590962696834313 | false | -
西餐 | 7127668806398315806 | 7127668806398315806 | false | -
谧歌 | 7301212776532380966 | 7301212776532380966 | false | -
贝松绿 | 7127668616991952158 | 7127668616991952158 | false | -
质感暗调 | 7127653798155209997 | 7127653798155209997 | false | -
质感电影 | 7395858604311596299 | 7395858604311596299 | false | effects_adjust_filter(default=1,min=0,max=1)
赛博朋克 | 7127657979838516494 | 7127657979838516494 | false | -
赤陀 | 7226251886360300837 | 7226251886360300837 | false | -
赫本 | 7127663117508660517 | 7127663117508660517 | false | -
赫石 | 7302823953406446899 | 7302823953406446899 | false | -
轻食 | 7127621137705618724 | 7127621137705618724 | false | -
达芬妮 | 7300602459356040484 | 7300602459356040484 | false | effects_adjust_filter(default=1,min=0,max=1)
迈阿密 | 7127684611450178823 | 7127684611450178823 | false | -
酷白 | 7127676762514885919 | 7127676762514885919 | false | -
金属 | 7127654151688949000 | 7127654151688949000 | false | -
闪光灯 | 7364705637931994405 | 7364705637931994405 | false | -
闪胶回忆 | 7452726092126833959 | 7452726092126833959 | false | effects_adjust_filter(default=1,min=0,max=1)
闻香识人 | 7127823728267775263 | 7127823728267775263 | false | -
阿尔菲 | 7299130097632627979 | 7299130097632627979 | false | effects_adjust_filter(default=1,min=0,max=1)
雪鹿 | 7302796570947243264 | 7302796570947243264 | false | -
雾瓷 | 7169239634076060960 | 7169239634076060960 | false | -
青春古早 | 7505676110412254527 | 7505676110412254527 | false | effects_adjust_filter(default=1,min=0,max=1)
青橙 | 7127615575865478430 | 7127615575865478430 | false | -
青橙电影 | 7401896022214970650 | 7401896022214970650 | false | effects_adjust_filter(default=1,min=0,max=1)
青红夜 | 7281575818621455628 | 7281575818621455628 | false | -
音乐节 | 7405834787132280079 | 7405834787132280079 | false | effects_adjust_filter(default=1,min=0,max=1)
风铃 | 7211001257996127547 | 7211001257996127547 | false | -
香松 | 7175094003493309757 | 7175094003493309757 | false | -
高清4K电影 | 7452548610971012379 | 7452548610971012379 | false | effects_adjust_filter(default=1,min=0,max=1)
高清冬日 | 7450317804554685708 | 7450317804554685708 | false | effects_adjust_filter(default=1,min=0,max=1)
高清明亮 | 7434564801990266162 | 7434564801990266162 | false | effects_adjust_filter(default=1,min=0,max=1)
高清润白 | 7404503340576410906 | 7404503340576410906 | false | effects_adjust_filter(default=1,min=0,max=1)
高清烟火 | 7446098482013768970 | 7446098482013768970 | false | effects_adjust_filter(default=1,min=0,max=1)
高清福气 | 7460008665286855973 | 7460008665286855973 | false | effects_adjust_filter(default=1,min=0,max=1)
高饱和 | 7127653121966230814 | 7127653121966230814 | false | -
鬼魅 | 7291201164027252024 | 7291201164027252024 | false | -
鲜亮食光 | 7441227246326582537 | 7441227246326582537 | false | effects_adjust_filter(default=1,min=0,max=1)
鲜美年味 | 7460115630973340940 | 7460115630973340940 | false | effects_adjust_filter(default=1,min=0,max=1)
黑胶唱片 | 7221805176410180921 | 7221805176410180921 | false | -
黑莓 | 7175100298610871610 | 7175100298610871610 | false | -
黑豹 | 7202475126485503236 | 7202475126485503236 | false | -
默片 | 7127655037026848031 | 7127655037026848031 | false | -
160C | 7190249807682800954 | 7190249807682800954 | true | -
2077 | 7131347316111314189 | 7131347316111314189 | true | -
400H | 7190236487152127269 | 7190236487152127269 | true | -
4K画质 | 7477802799862992138 | 7477802799862992138 | true | effects_adjust_filter(default=1,min=0,max=1)
4K画质电影 | 7478641636092775743 | 7478641636092775743 | true | effects_adjust_filter(default=1,min=0,max=1)
4K高品质 | 7480203423095213362 | 7480203423095213362 | true | effects_adjust_filter(default=1,min=0,max=1)
800Z | 7190237757552348471 | 7190237757552348471 | true | -
8K画质 | 7478895015901613375 | 7478895015901613375 | true | effects_adjust_filter(default=0.8,min=0,max=1)
90s | 7131366613823114503 | 7131366613823114503 | true | -
City Walk | 7263360572404550931 | 7263360572404550931 | true | -
EOS3 | 7200697197002886404 | 7200697197002886404 | true | -
FXN | 7332480052392774975 | 7332480052392774975 | true | -
GR正片 | 7168098796860148995 | 7168098796860148995 | true | -
GR绿 | 7168121440141708576 | 7168121440141708576 | true | -
GR蓝 | 7168097661160131879 | 7168097661160131879 | true | -
IG白 | 7221479156318489893 | 7221479156318489893 | true | -
INS暗 | 7223645151820877093 | 7223645151820877093 | true | -
INS暗调 | 7473409650746985779 | 7473409650746985779 | true | effects_adjust_filter(default=1,min=0,max=1)
KONICA | 7200712753324035339 | 7200712753324035339 | true | -
KU4 | 7127669605199318280 | 7127669605199318280 | true | -
PENTAX | 7200999937960627459 | 7200999937960627459 | true | -
Pocket3 | 7493462285889899803 | 7493462285889899803 | true | -
Y3K | 7398034408139230490 | 7398034408139230490 | true | effects_adjust_filter(default=1,min=0,max=1)
iPhone6s | 7393943544089627930 | 7393943544089627930 | true | effects_adjust_filter(default=1,min=0,max=1)
ins古早味 | 7547377459126209827 | 7547377459126209827 | true | effects_adjust_filter(default=1,min=0,max=1)
miu系II | 7395097767388990756 | 7395097767388990756 | true | effects_adjust_filter(default=1,min=0,max=1)
万圣 | 7426749131344841995 | 7426749131344841995 | true | effects_adjust_filter(default=1,min=0,max=1)
不要抬头 | 7202480720843984131 | 7202480720843984131 | true | -
丝滑皮肤 | 7495673180904885516 | 7495673180904885516 | true | effects_adjust_filter(default=1,min=0,max=1)
中性 | 7127621445806525704 | 7127621445806525704 | true | -
中性II | 7312646907908607244 | 7312646907908607244 | true | -
中性奶杏 | 7385203623703137575 | 7385203623703137575 | true | effects_adjust_filter(default=1,min=0,max=1)
乐游 | 7193982146363673856 | 7193982146363673856 | true | -
云暖 | 7314883649999015231 | 7314883649999015231 | true | -
京都 | 7127679758581697822 | 7127679758581697822 | true | -
亭竹 | 7302325291634920755 | 7302325291634920755 | true | -
亮丽 | 7413406043608272154 | 7413406043608272154 | true | effects_adjust_filter(default=1,min=0,max=1)
人生之事 | 7148844086869396743 | 7148844086869396743 | true | -
仲夏夜 | 7281166048273943867 | 7281166048273943867 | true | -
仿撕拉片 | 7503844955467648283 | 7503844955467648283 | true | effects_adjust_filter(default=1,min=0,max=1)
伊豆 | 7195781682492984636 | 7195781682492984636 | true | -
伤感故事电影 | 7516859499404119296 | 7516859499404119296 | true | effects_adjust_filter(default=1,min=0,max=1)
伤感电影 | 7498948996816194843 | 7498948996816194843 | true | effects_adjust_filter(default=1,min=0,max=1)
余晖 | 7278616064018107707 | 7278616064018107707 | true | -
佳能G12 | 7485292050917657906 | 7485292050917657906 | true | -
佳能G7X II | 7291597100389862707 | 7291597100389862707 | true | -
佳能G7X III | 7291595038688136474 | 7291595038688136474 | true | -
佳能清透感 | 7605630861400083763 | 7605630861400083763 | true | effects_adjust_filter(default=1,min=0,max=1)
俏皮萌宠 | 7394713676789353737 | 7394713676789353737 | true | effects_adjust_filter(default=1,min=0,max=1)
俱乐部 | 7239235794744003851 | 7239235794744003851 | true | -
倾森 | 7332714336315526409 | 7332714336315526409 | true | effects_adjust_filter(default=1,min=0,max=1)
假日海滩 | 7405115979107274020 | 7405115979107274020 | true | effects_adjust_filter(default=1,min=0,max=1)
假日电影感 | 7517179906292190501 | 7517179906292190501 | true | effects_adjust_filter(default=1,min=0,max=1)
偏振镜 | 7551730483399314751 | 7551730483399314751 | true | effects_adjust_speed(default=1,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1); effects_adjust_sharpen(default=0.7,min=0,max=1); effects_adjust_soft(default=0.9,min=0,max=1)
傍晚 | 7226990270053649725 | 7226990270053649725 | true | -
元宵祈福 | 7467923122545544499 | 7467923122545544499 | true | effects_adjust_filter(default=1,min=0,max=1)
元气春颜 | 7480473626207145254 | 7480473626207145254 | true | effects_adjust_filter(default=1,min=0,max=1)
元气焕肤 | 7475923492119006473 | 7475923492119006473 | true | effects_adjust_filter(default=1,min=0,max=1)
元气粉肌 | 7472748943953169727 | 7472748943953169727 | true | effects_adjust_filter(default=1,min=0,max=1)
光流 | 7233732009070300473 | 7233732009070300473 | true | effects_adjust_filter(default=1,min=0,max=1)
冬日亮肤 | 7446310234596904246 | 7446310234596904246 | true | effects_adjust_filter(default=1,min=0,max=1)
冬日清寒 | 7594740512435801380 | 7594740512435801380 | true | effects_adjust_filter(default=1,min=0,max=1)
冬日物语 | 7444960658178821414 | 7444960658178821414 | true | effects_adjust_filter(default=1,min=0,max=1)
冬日胶卷 | 7447359984167406863 | 7447359984167406863 | true | effects_adjust_filter(default=1,min=0,max=1)
冬禧 | 7190250133672578316 | 7190250133672578316 | true | -
冬绪电影 | 7570270935157148968 | 7570270935157148968 | true | effects_adjust_filter(default=1,min=0,max=1)
冬雪电影感 | 7566134950601297167 | 7566134950601297167 | true | effects_adjust_filter(default=1,min=0,max=1)
冰夏 | 7258221827485486393 | 7258221827485486393 | true | -
冰清玉洁 | 7433451697764158747 | 7433451697764158747 | true | effects_adjust_filter(default=1,min=0,max=1)
冰清蓝 | 7494313060480388389 | 7494313060480388389 | true | effects_adjust_filter(default=1,min=0,max=1)
冰瀑 | 7196927862056701240 | 7196927862056701240 | true | -
冰茶 | 7131399016771800357 | 7131399016771800357 | true | -
冰蓝印染 | 7585168530518134067 | 7585168530518134067 | true | effects_adjust_filter(default=1,min=0,max=1)
冰雪白 | 7462637393783360809 | 7462637393783360809 | true | effects_adjust_filter(default=1,min=0,max=1)
冷叙 | 7159132840179895590 | 7159132840179895590 | true | -
冷墨 | 7300751893813366053 | 7300751893813366053 | true | -
冷月夜 | 7281165355353951543 | 7281165355353951543 | true | -
冷萃 | 7177729481300364548 | 7177729481300364548 | true | -
冷调CCD | 7434467628422270220 | 7434467628422270220 | true | -
冷调微曝 | 7528075579602554150 | 7528075579602554150 | true | effects_adjust_filter(default=1,min=0,max=1)
冷透 | 7127824802819116302 | 7127824802819116302 | true | -
净白 | 7127667352782572807 | 7127667352782572807 | true | -
净透 | 7127666004477414687 | 7127666004477414687 | true | -
凛冬电影感 | 7569645361694870818 | 7569645361694870818 | true | effects_adjust_filter(default=1,min=0,max=1)
初雪电影感 | 7564852301807078694 | 7564852301807078694 | true | effects_adjust_filter(default=1,min=0,max=1)
加州落日 | 7498004563954322726 | 7498004563954322726 | true | effects_adjust_filter(default=1,min=0,max=1)
动漫小镇 | 7604510820105522468 | 7604510820105522468 | true | effects_adjust_filter(default=1,min=0,max=1)
劲闯 | 7248568097660013864 | 7248568097660013864 | true | -
北海道II | 7563691938076003622 | 7563691938076003622 | true | effects_adjust_filter(default=1,min=0,max=1)
千禧潮酷 | 7513608221735554330 | 7513608221735554330 | true | effects_adjust_filter(default=1,min=0,max=1)
半衫 | 7145391402661334280 | 7145391402661334280 | true | -
南法午后 | 7436724426416131347 | 7436724426416131347 | true | effects_adjust_filter(default=1,min=0,max=1)
原生肤 | 7366582938638503187 | 7366582938638503187 | true | effects_adjust_filter(default=1,min=0,max=1)
原生自然 | 7473037215426153728 | 7473037215426153728 | true | effects_adjust_filter(default=1,min=0,max=1)
原野 | 7271281225115897140 | 7271281225115897140 | true | -
去灰 | 7453118140151647538 | 7453118140151647538 | true | effects_adjust_filter(default=1,min=0,max=1)
去灰II | 7226991425160858937 | 7226991425160858937 | true | -
去灰高清 | 7436400247540141348 | 7436400247540141348 | true | effects_adjust_filter(default=1,min=0,max=1)
去雾 | 7564322465548274968 | 7564322465548274968 | true | effects_adjust_filter(default=1,min=0,max=1)
去黄 | 7302338306849656127 | 7302338306849656127 | true | -
去黄韩系 | 7598448281483529510 | 7598448281483529510 | true | effects_adjust_filter(default=1,min=0,max=1)
反差富士 | 7403222365217295667 | 7403222365217295667 | true | effects_adjust_filter(default=1,min=0,max=1)
反差色 | 7542896143949106472 | 7542896143949106472 | true | effects_adjust_filter(default=1,min=0,max=1)
发光CCD | 7434468515576319295 | 7434468515576319295 | true | effects_adjust_filter(default=1,min=0,max=1)
叠阳 | 7148961858320354573 | 7148961858320354573 | true | -
古早像素 | 7470614335644077375 | 7470614335644077375 | true | effects_adjust_filter(default=1,min=0,max=1)
古早回忆 | 7449798505385790746 | 7449798505385790746 | true | effects_adjust_filter(default=1,min=0,max=1)
古早回忆录 | 7594878732377099556 | 7594878732377099556 | true | effects_adjust_filter(default=1,min=0,max=1)
古早复古 | 7457910812439596339 | 7457910812439596339 | true | effects_adjust_filter(default=1,min=0,max=1)
古早宝丽来 | 7586692127833328896 | 7586692127833328896 | true | effects_adjust_filter(default=1,min=0,max=1)
古早感胶片 | 7576707005788867875 | 7576707005788867875 | true | effects_adjust_filter(default=1,min=0,max=1)
古早时光 | 7560702007405792552 | 7560702007405792552 | true | effects_adjust_filter(default=1,min=0,max=1)
古早画质 | 7557963448068361510 | 7557963448068361510 | true | effects_adjust_filter(default=1,min=0,max=1)
古早记忆 | 7366562482812456255 | 7366562482812456255 | true | -
古早高曝 | 7596354290730552622 | 7596354290730552622 | true | effects_adjust_filter(default=1,min=0,max=1)
古罗马电影 | 7596692097164479807 | 7596692097164479807 | true | effects_adjust_filter(default=1,min=0,max=1)
古都 | 7127615616525126949 | 7127615616525126949 | true | -
史诗电影 | 7591041766158109952 | 7591041766158109952 | true | effects_adjust_filter(default=1,min=0,max=1)
吉宵 | 7190241639070174503 | 7190241639070174503 | true | -
向晚 | 7226254370084490554 | 7226254370084490554 | true | effects_adjust_filter(default=1,min=0,max=1)
味蕾 | 7281166220794055997 | 7281166220794055997 | true | -
和歌山 | 7210651068324285754 | 7210651068324285754 | true | -
哈苏I | 7291596720956329266 | 7291596720956329266 | true | -
哈苏II | 7291560741885480250 | 7291560741885480250 | true | -
哈苏蓝 | 7361792059109313811 | 7361792059109313811 | true | effects_adjust_filter(default=1,min=0,max=1)
哥谭 | 7337928347118275890 | 7337928347118275890 | true | -
喜气新春 | 7593257815104359706 | 7593257815104359706 | true | effects_adjust_filter(default=1,min=0,max=1)
围炉暖食 | 7586719222160543017 | 7586719222160543017 | true | effects_adjust_filter(default=1,min=0,max=1)
国民旧照 | 7511971221785922826 | 7511971221785922826 | true | effects_adjust_filter(default=1,min=0,max=1)
国风电影 | 7409572381775138067 | 7409572381775138067 | true | effects_adjust_filter(default=1,min=0,max=1)
圣善夜 | 7175100386007584060 | 7175100386007584060 | true | -
圣诞回忆录 | 7447162094572686592 | 7447162094572686592 | true | effects_adjust_filter(default=1,min=0,max=1)
圣诞愿景 | 7428162298436537627 | 7428162298436537627 | true | effects_adjust_filter(default=1,min=0,max=1)
圣诞拍立得 | 7438160882837835018 | 7438160882837835018 | true | effects_adjust_filter(default=1,min=0,max=1)
圣诞胶片 | 7446290147697528076 | 7446290147697528076 | true | effects_adjust_filter(default=1,min=0,max=1)
圣诞萌宠 | 7582150382516718894 | 7582150382516718894 | true | effects_adjust_filter(default=1,min=0,max=1)
圣诞闪胶II | 7446329592119332108 | 7446329592119332108 | true | effects_adjust_filter(default=1,min=0,max=1)
圣诞闪胶III | 7446329549283020068 | 7446329549283020068 | true | effects_adjust_filter(default=1,min=0,max=1)
城市赏月II | 7405206230550973731 | 7405206230550973731 | true | effects_adjust_filter(default=1,min=0,max=1)
增色 | 7283013745788357925 | 7283013745788357925 | true | -
增色II | 7411476796526300452 | 7411476796526300452 | true | effects_adjust_filter(default=1,min=0,max=1)
增质CCD | 7500847387959708978 | 7500847387959708978 | true | effects_adjust_filter(default=1,min=0,max=1)
增质去雾 | 7565956901322706226 | 7565956901322706226 | true | effects_adjust_filter(default=1,min=0,max=1)
墨林 | 7271284653816843554 | 7271284653816843554 | true | -
墨色胶卷 | 7580008561884040473 | 7580008561884040473 | true | effects_adjust_filter(default=1,min=0,max=1)
复古电影感 | 7479800436778732863 | 7479800436778732863 | true | effects_adjust_filter(default=1,min=0,max=1)
复古蓝调 | 7449048492665834779 | 7449048492665834779 | true | effects_adjust_filter(default=1,min=0,max=1)
夏威夷 | 7159140854601469223 | 7159140854601469223 | true | -
夏日粉 | 7261469707138518283 | 7261469707138518283 | true | -
夏日紫霞 | 7508030199255026970 | 7508030199255026970 | true | effects_adjust_filter(default=1,min=0,max=1)
多巴胺 | 7237441824611224889 | 7237441824611224889 | true | -
夜拍闪曝 | 7494135245709610275 | 7494135245709610275 | true | effects_adjust_filter(default=1,min=0,max=1)
夜拍高光 | 7462637606052941095 | 7462637606052941095 | true | -
夜景人像增强 | 7493208490832317705 | 7493208490832317705 | true | effects_adjust_filter(default=1,min=0,max=1)
夜景去雾 | 7525110001959030042 | 7525110001959030042 | true | effects_adjust_filter(default=1,min=0,max=1)
夜景增色II | 7411477748130139403 | 7411477748130139403 | true | effects_adjust_filter(default=1,min=0,max=1)
夜焰 | 7185289606600953092 | 7185289606600953092 | true | -
夜雾 | 7168110568673479948 | 7168110568673479948 | true | -
大吉岭 | 7175076362997288230 | 7175076362997288230 | true | -
大疆4Pro | 7534412681785183540 | 7534412681785183540 | true | effects_adjust_filter(default=1,min=0,max=1)
大疆电影感 | 7512706064693988645 | 7512706064693988645 | true | effects_adjust_filter(default=1,min=0,max=1)
大雪纷飞 | 7569682767080901897 | 7569682767080901897 | true | effects_adjust_filter(default=1,min=0,max=1)
奥林巴斯 | 7361792068475325735 | 7361792068475325735 | true | -
奥罗拉 | 7269236283019463972 | 7269236283019463972 | true | effects_adjust_filter(default=1,min=0,max=1)
奶呼萌宠 | 7395972887133441307 | 7395972887133441307 | true | effects_adjust_filter(default=1,min=0,max=1)
奶昔 | 7172169921726565670 | 7172169921726565670 | true | -
奶油II | 7474592762331942184 | 7474592762331942184 | true | effects_adjust_filter(default=1,min=0,max=1)
奶油柔肤 | 7482412177760996646 | 7482412177760996646 | true | effects_adjust_filter(default=1,min=0,max=1)
奶油白 | 7398438142321134898 | 7398438142321134898 | true | effects_adjust_filter(default=1,min=0,max=1)
奶油白肤 | 7459030855810387251 | 7459030855810387251 | true | effects_adjust_filter(default=1,min=0,max=1)
奶油美食 | 7480210942026927423 | 7480210942026927423 | true | effects_adjust_filter(default=1,min=0,max=1)
奶油风萌宠 | 7510488117430734118 | 7510488117430734118 | true | effects_adjust_filter(default=1,min=0,max=1)
好莱坞I | 7226994281414692155 | 7226994281414692155 | true | effects_adjust_filter(default=1,min=0,max=1)
好莱坞II | 7226995248814165308 | 7226995248814165308 | true | -
好莱坞III | 7312617341710372107 | 7312617341710372107 | true | -
好莱坞IV | 7312647197462367524 | 7312647197462367524 | true | -
嬉皮士 | 7131431284403981605 | 7131431284403981605 | true | -
子弹列车 | 7202480777387445507 | 7202480777387445507 | true | -
安塞尔灰调 | 7581301466128780569 | 7581301466128780569 | true | effects_adjust_filter(default=1,min=0,max=1)
安藤调 | 7607806312822443289 | 7607806312822443289 | true | effects_adjust_filter(default=1,min=0,max=1)
安西娅 | 7270142995712773415 | 7270142995712773415 | true | -
宝丽来SX70 | 7600301036787600667 | 7600301036787600667 | true | effects_adjust_filter(default=1,min=0,max=1)
家宴 | 7330584144524643595 | 7330584144524643595 | true | effects_adjust_filter(default=1,min=0,max=1)
宿营 | 7127822311708691726 | 7127822311708691726 | true | -
富士CC I | 7268561936344780086 | 7268561936344780086 | true | -
富士NC I | 7159156535640296737 | 7159156535640296737 | true | -
富士NC II | 7159408376378559747 | 7159408376378559747 | true | -
富士NC III | 7159134459088899339 | 7159134459088899339 | true | -
富士NN | 7447157317457513743 | 7447157317457513743 | true | -
富士XT5 | 7535108076081335606 | 7535108076081335606 | true | effects_adjust_filter(default=1,min=0,max=1)
富士x100 | 7394357532912782629 | 7394357532912782629 | true | effects_adjust_filter(default=1,min=0,max=1)
富士电影 | 7497919307628825866 | 7497919307628825866 | true | effects_adjust_filter(default=1,min=0,max=1)
富士蓝 | 7246720031118101816 | 7246720031118101816 | true | -
富士蓝II | 7226994246471945530 | 7226994246471945530 | true | -
富士青 | 7226994214029184313 | 7226994214029184313 | true | -
富春山居 | 7208496124779302177 | 7208496124779302177 | true | -
小清新 | 7482421927462653220 | 7482421927462653220 | true | effects_adjust_filter(default=1,min=0,max=1)
小美好 | 7468493795479276835 | 7468493795479276835 | true | effects_adjust_filter(default=1,min=0,max=1)
小麦色 | 7362076973981584691 | 7362076973981584691 | true | -
尘杏 | 7131630640646081822 | 7131630640646081822 | true | -
尘烟 | 7148958479326153991 | 7148958479326153991 | true | -
山晴 | 7246723856222719269 | 7246723856222719269 | true | -
山本 | 7156638423191784735 | 7156638423191784735 | true | -
山海诗篇 | 7603667447308389657 | 7603667447308389657 | true | effects_adjust_filter(default=1,min=0,max=1)
岚夏 | 7260771472107441471 | 7260771472107441471 | true | -
岩灰 | 7221472488079904060 | 7221472488079904060 | true | -
川秋电影感 | 7561143628266065204 | 7561143628266065204 | true | effects_adjust_filter(default=1,min=0,max=1)
川野 | 7361032844484857142 | 7361032844484857142 | true | -
市井 | 7145394707156323591 | 7145394707156323591 | true | -
幽海 | 7262350396566342975 | 7262350396566342975 | true | -
底特律 | 7336763348492553499 | 7336763348492553499 | true | effects_adjust_filter(default=1,min=0,max=1)
庙会 | 7185309693131148555 | 7185309693131148555 | true | -
弥晖 | 7148812815246134541 | 7148812815246134541 | true | -
强曝光 | 7568386153783512335 | 7568386153783512335 | true | effects_adjust_filter(default=1,min=0,max=1)
彩光 | 7127824109093866760 | 7127824109093866760 | true | -
影忆 | 7379137689599167779 | 7379137689599167779 | true | effects_adjust_filter(default=1,min=0,max=1)
影石4k | 7604153795639135497 | 7604153795639135497 | true | effects_adjust_filter(default=1,min=0,max=1)
影部 | 7168136171673963787 | 7168136171673963787 | true | -
往事 | 7530879877180919049 | 7530879877180919049 | true | effects_adjust_filter(default=1,min=0,max=1)
徕卡I | 7268562944093408523 | 7268562944093408523 | true | -
徕卡II | 7268563047776587020 | 7268563047776587020 | true | -
徕卡Q2 | 7500447762404724018 | 7500447762404724018 | true | effects_adjust_filter(default=1,min=0,max=1)
徕卡银盐 | 7601116367005175067 | 7601116367005175067 | true | effects_adjust_filter(default=1,min=0,max=1)
心动夏 | 7261461692096220428 | 7261461692096220428 | true | -
忆山 | 7271278427309755688 | 7271278427309755688 | true | effects_adjust_filter(default=1,min=0,max=1)
忆时 | 7266325161433910591 | 7266325161433910591 | true | -
快照II | 7143760738765655310 | 7143760738765655310 | true | -
怀旧 | 7494564488704806198 | 7494564488704806198 | true | effects_adjust_filter(default=1,min=0,max=1)
怦然心动 | 7195889899738909990 | 7195889899738909990 | true | -
恍光 | 7237446176629345593 | 7237446176629345593 | true | effects_adjust_filter(default=1,min=0,max=1)
情感故事电影 | 7509005376835079439 | 7509005376835079439 | true | effects_adjust_filter(default=1,min=0,max=1)
情辉 | 7329826553477565705 | 7329826553477565705 | true | -
慕斯 | 7261185427703418169 | 7261185427703418169 | true | -
扬帆远航 | 7487297020743404810 | 7487297020743404810 | true | effects_adjust_filter(default=1,min=0,max=1)
拐杖糖 | 7175093825659079991 | 7175093825659079991 | true | -
捕风 | 7248566556593098024 | 7248566556593098024 | true | -
摩登 | 7131219052021779719 | 7131219052021779719 | true | -
撕拉拍立得 | 7502647335218941220 | 7502647335218941220 | true | effects_adjust_filter(default=1,min=0,max=1)
攀岩 | 7195930274918567180 | 7195930274918567180 | true | -
文艺少女 | 7409360036096527670 | 7409360036096527670 | true | effects_adjust_filter(default=1,min=0,max=1)
新中式电影感 | 7493945636518104360 | 7493945636518104360 | true | effects_adjust_filter(default=1,min=0,max=1)
新宿 | 7210646550974876984 | 7210646550974876984 | true | -
新年喜市 | 7449639936292031781 | 7449639936292031781 | true | effects_adjust_filter(default=1,min=0,max=1)
新年欢愉 | 7452802706139352370 | 7452802706139352370 | true | effects_adjust_filter(default=1,min=0,max=1)
新年电影感 | 7582425874620747008 | 7582425874620747008 | true | effects_adjust_filter(default=1,min=0,max=1)
新年红 | 7449639891694112010 | 7449639891694112010 | true | effects_adjust_filter(default=1,min=0,max=1)
新年红气 | 7586522353278962984 | 7586522353278962984 | true | effects_adjust_filter(default=1,min=0,max=1)
新年顺意 | 7603025037431541027 | 7603025037431541027 | true | effects_adjust_filter(default=1,min=0,max=1)
新颜 | 7188018091496951077 | 7188018091496951077 | true | -
日光吻 | 7226985203540053305 | 7226985203540053305 | true | -
日出增色 | 7526422478206356787 | 7526422478206356787 | true | effects_adjust_filter(default=1,min=0,max=1)
日出时刻 | 7551097988878273826 | 7551097988878273826 | true | effects_adjust_filter(default=1,min=0,max=1)
日料寿司 | 7507632191380229402 | 7507632191380229402 | true | effects_adjust_filter(default=1,min=0,max=1)
日漫增色 | 7493804773515316491 | 7493804773515316491 | true | effects_adjust_filter(default=1,min=0,max=1)
日漫清新 | 7439037715825413413 | 7439037715825413413 | true | effects_adjust_filter(default=1,min=0,max=1)
日系增色 | 7472373777469328667 | 7472373777469328667 | true | effects_adjust_filter(default=1,min=0,max=1)
日系春和 | 7473805992308837659 | 7473805992308837659 | true | effects_adjust_filter(default=1,min=0,max=1)
日落增色 | 7468875753661173004 | 7468875753661173004 | true | effects_adjust_filter(default=1,min=0,max=1)
日落时刻 | 7496524092779105551 | 7496524092779105551 | true | effects_adjust_filter(default=1,min=0,max=1)
日落晚霞 | 7528332870654414142 | 7528332870654414142 | true | effects_adjust_filter(default=1,min=0,max=1)
旧时代II | 7232217903536409893 | 7232217903536409893 | true | -
旧时来信 | 7366562830486621459 | 7366562830486621459 | true | -
旧曲 | 7266320092386938124 | 7266320092386938124 | true | effects_adjust_filter(default=1,min=0,max=1)
旧金山 | 7159161900389977382 | 7159161900389977382 | true | -
时尚极简 | 7549604752934325556 | 7549604752934325556 | true | effects_adjust_filter(default=1,min=0,max=1)
旷野 | 7275698024892943655 | 7275698024892943655 | true | effects_adjust_filter(default=1,min=0,max=1)
旷野自然 | 7501717343156981046 | 7501717343156981046 | true | effects_adjust_filter(default=1,min=0,max=1)
旷野蓝 | 7131513310733765918 | 7131513310733765918 | true | -
明亮春味 | 7485240505257807138 | 7485240505257807138 | true | effects_adjust_filter(default=1,min=0,max=1)
明亮焕晴 | 7470840671763565864 | 7470840671763565864 | true | effects_adjust_filter(default=1,min=0,max=1)
明媚春景 | 7482055184554806566 | 7482055184554806566 | true | effects_adjust_filter(default=1,min=0,max=1)
明媚春色 | 7611007721336311046 | 7611007721336311046 | true | effects_adjust_filter(default=1,min=0,max=1)
明媚自然 | 7480823852470177034 | 7480823852470177034 | true | effects_adjust_filter(default=1,min=0,max=1)
明媚透亮 | 7506413750665121060 | 7506413750665121060 | true | effects_adjust_filter(default=1,min=0,max=1)
春和 | 7327596304173944127 | 7327596304173944127 | true | effects_adjust_filter(default=1,min=0,max=1)
春喜 | 7325335963318750515 | 7325335963318750515 | true | -
春天淡彩 | 7479295356488977679 | 7479295356488977679 | true | effects_adjust_filter(default=1,min=0,max=1)
春忆胶卷 | 7483069698981104947 | 7483069698981104947 | true | effects_adjust_filter(default=1,min=0,max=1)
春日序 | 7477922252470652198 | 7477922252470652198 | true | effects_adjust_filter(default=1,min=0,max=1)
春日樱 | 7493076668009958668 | 7493076668009958668 | true | effects_adjust_filter(default=0.8,min=0,max=1)
春日清晰 | 7477594530104085770 | 7477594530104085770 | true | effects_adjust_filter(default=1,min=0,max=1)
春日清透 | 7485293187616066831 | 7485293187616066831 | true | -
春日温柔 | 7477942092459773193 | 7477942092459773193 | true | effects_adjust_filter(default=1,min=0,max=1)
春日美食III | 7486868815364492554 | 7486868815364492554 | true | effects_adjust_filter(default=1,min=0,max=1)
春日花田 | 7611799763343789318 | 7611799763343789318 | true | effects_adjust_filter(default=1,min=0,max=1)
春日花间 | 7472064159065132325 | 7472064159065132325 | true | effects_adjust_filter(default=1,min=0,max=1)
春日韩胶 | 7481494936836197641 | 7481494936836197641 | true | effects_adjust_filter(default=1,min=0,max=1)
春桃肤 | 7483917188638772517 | 7483917188638772517 | true | effects_adjust_filter(default=1,min=0,max=1)
春橙肤 | 7481693425218194725 | 7481693425218194725 | true | effects_adjust_filter(default=1,min=0,max=1)
春游踏青 | 7493581083628408102 | 7493581083628408102 | true | effects_adjust_filter(default=1,min=0,max=1)
春禧电影感 | 7594482003286838564 | 7594482003286838564 | true | effects_adjust_filter(default=1,min=0,max=1)
春风 | 7148963827239963918 | 7148963827239963918 | true | -
昭和 | 7195780237790154042 | 7195780237790154042 | true | -
晚宴 | 7302041028205333786 | 7302041028205333786 | true | effects_adjust_filter(default=1,min=0,max=1)
晚柠 | 7262634564428778752 | 7262634564428778752 | true | -
晚樱 | 7127609541839129886 | 7127609541839129886 | true | -
晨旭 | 7279062968501832972 | 7279062968501832972 | true | effects_adjust_filter(default=1,min=0,max=1)
普林斯顿 | 7127615578705104135 | 7127615578705104135 | true | -
景明 | 7329530921755888915 | 7329530921755888915 | true | effects_adjust_filter(default=1,min=0,max=1)
晴冬暖阳 | 7571508644982902059 | 7571508644982902059 | true | effects_adjust_filter(default=1,min=0,max=1)
晴天 | 7420253131079961868 | 7420253131079961868 | true | effects_adjust_filter(default=1,min=0,max=1)
晴天亮丽 | 7454234032570764581 | 7454234032570764581 | true | effects_adjust_filter(default=1,min=0,max=1)
晴天增色 | 7454234028141497610 | 7454234028141497610 | true | effects_adjust_filter(default=1,min=0,max=1)
晴天灿烂 | 7486890449207151891 | 7486890449207151891 | true | effects_adjust_filter(default=1,min=0,max=1)
晴好 | 7281163707227344189 | 7281163707227344189 | true | -
晴好风光 | 7475397942715632922 | 7475397942715632922 | true | effects_adjust_filter(default=1,min=0,max=1)
晴山质感 | 7542495542429879562 | 7542495542429879562 | true | effects_adjust_filter(default=1,min=0,max=1)
晴春 | 7346542846863887635 | 7346542846863887635 | true | effects_adjust_filter(default=1,min=0,max=1)
晴春奶蓝 | 7485769123176254770 | 7485769123176254770 | true | effects_adjust_filter(default=1,min=0,max=1)
晴朗 | 7434746357233028390 | 7434746357233028390 | true | effects_adjust_filter(default=1,min=0,max=1)
晴海 | 7363996374083407140 | 7363996374083407140 | true | -
晴秋 | 7410233668351937846 | 7410233668351937846 | true | effects_adjust_filter(default=1,min=0,max=1)
晴空 | 7127558139058179342 | 7127558139058179342 | true | -
晴空漫游 | 7477810373060611338 | 7477810373060611338 | true | effects_adjust_filter(default=1,min=0,max=1)
晴肤 | 7365842976691604763 | 7365842976691604763 | true | effects_adjust_filter(default=1,min=0,max=1)
晴谷 | 7307191907514420491 | 7307191907514420491 | true | -
晶莹雪肤 | 7592615852252335394 | 7592615852252335394 | true | effects_adjust_filter(default=1,min=0,max=1)
晶透 | 7199095242476293435 | 7199095242476293435 | true | -
智能光线 | 7451897248885099795 | 7451897248885099795 | true | effects_adjust_filter(default=1,min=0,max=1)
暖晨 | 7312646382395936010 | 7312646382395936010 | true | -
暖阳冬日 | 7572802123021290787 | 7572802123021290787 | true | effects_adjust_filter(default=1,min=0,max=1)
暖雾晨光 | 7595404603575782707 | 7595404603575782707 | true | effects_adjust_filter(default=1,min=0,max=1)
暖食增色 | 7533181577170373934 | 7533181577170373934 | true | effects_adjust_filter(default=1,min=0,max=1)
暖黄 | 7127830631601458440 | 7127830631601458440 | true | -
暗光提亮 | 7446318175991368997 | 7446318175991368997 | true | -
暗匣 | 7159163878822153483 | 7159163878822153483 | true | -
暗夜明肤 | 7328364126449765671 | 7328364126449765671 | true | -
暗影 | 7291203298630159676 | 7291203298630159676 | true | -
暗曛 | 7281163501047991608 | 7281163501047991608 | true | -
暗蓝电影 | 7596691154008132915 | 7596691154008132915 | true | effects_adjust_filter(default=1,min=0,max=1)
暗蓝电影感 | 7596940217177705779 | 7596940217177705779 | true | effects_adjust_filter(default=1,min=0,max=1)
暗调发光 | 7413717074037525769 | 7413717074037525769 | true | effects_adjust_filter(default=1,min=0,max=1)
暗调古风 | 7505272278574206219 | 7505272278574206219 | true | effects_adjust_filter(default=1,min=0,max=1)
暗调复古电影 | 7494530599202327846 | 7494530599202327846 | true | effects_adjust_filter(default=1,min=0,max=1)
暗调电影 | 7402945560623336758 | 7402945560623336758 | true | effects_adjust_filter(default=1,min=0,max=1)
暗调纪实电影 | 7493536391431785752 | 7493536391431785752 | true | effects_adjust_filter(default=1,min=0,max=1)
暗调阴郁 | 7596555533230902579 | 7596555533230902579 | true | effects_adjust_filter(default=1,min=0,max=1)
暗部漫游 | 7595398794410347826 | 7595398794410347826 | true | effects_adjust_filter(default=1,min=0,max=1)
暗金 | 7511619145864187136 | 7511619145864187136 | true | effects_adjust_filter(default=1,min=0,max=1)
暗银 | 7177725752513793284 | 7177725752513793284 | true | -
暗银II | 7223630575888780602 | 7223630575888780602 | true | -
暗黑玫瑰 | 7562034253412715811 | 7562034253412715811 | true | effects_adjust_filter(default=1,min=0,max=1)
暮信 | 7279061785922080055 | 7279061785922080055 | true | -
暮川 | 7262351934785408267 | 7262351934785408267 | true | effects_adjust_filter(default=1,min=0,max=1)
暮樱 | 7341257736983760182 | 7341257736983760182 | true | effects_adjust_filter(default=1,min=0,max=1)
暮涛 | 7145394582933572878 | 7145394582933572878 | true | -
暮色约会 | 7332396398157090089 | 7332396398157090089 | true | -
曼波 | 7233734975839898940 | 7233734975839898940 | true | -
月吟 | 7168108694285159719 | 7168108694285159719 | true | -
月辉 | 7476109983688576290 | 7476109983688576290 | true | effects_adjust_filter(default=1,min=0,max=1)
朦胧气质棕 | 7493920442613288219 | 7493920442613288219 | true | effects_adjust_filter(default=1,min=0,max=1)
木葵 | 7233731121610100020 | 7233731121610100020 | true | -
末世天使 | 7506099780947430668 | 7506099780947430668 | true | effects_adjust_filter(default=1,min=0,max=1)
杏铃 | 7295630593063193865 | 7295630593063193865 | true | -
松绿 | 7246723559047941433 | 7246723559047941433 | true | -
果酥 | 7160594387594972446 | 7160594387594972446 | true | -
柏林 | 7530690874699713842 | 7530690874699713842 | true | effects_adjust_filter(default=1,min=0,max=1)
柔光 | 7395596262252334373 | 7395596262252334373 | true | effects_adjust_filter(default=1,min=0,max=1)
柔焦 | 7345412316621442354 | 7345412316621442354 | true | -
柔雾感 | 7480785731015691539 | 7480785731015691539 | true | effects_adjust_filter(default=1,min=0,max=1)
柠青 | 7127653798272683278 | 7127653798272683278 | true | -
柯达金200 | 7517685395102977334 | 7517685395102977334 | true | effects_adjust_filter(default=1,min=0,max=1)
栖海 | 7349928965869538570 | 7349928965869538570 | true | -
栩栩 | 7177259623819316519 | 7177259623819316519 | true | -
格金 | 7348301778909252879 | 7348301778909252879 | true | -
桃木 | 7252673818035064124 | 7252673818035064124 | true | -
桃粉 | 7297131749346135331 | 7297131749346135331 | true | -
桐影 | 7275699191253339455 | 7275699191253339455 | true | -
梦境 | 7127675251604917517 | 7127675251604917517 | true | -
梦幻夏 | 7377370067798985993 | 7377370067798985993 | true | -
梦核紫 | 7261463763344248103 | 7261463763344248103 | true | -
梨花白 | 7470438095998029066 | 7470438095998029066 | true | effects_adjust_filter(default=1,min=0,max=1)
梨花白皙 | 7611013816964500788 | 7611013816964500788 | true | effects_adjust_filter(default=1,min=0,max=1)
棕榈 | 7252676190073392444 | 7252676190073392444 | true | -
森山 | 7242215081663008056 | 7242215081663008056 | true | -
森林徒步 | 7524262165273005321 | 7524262165273005321 | true | effects_adjust_filter(default=1,min=0,max=1)
森秋 | 7274575376095923497 | 7274575376095923497 | true | -
森绿 | 7510128089511349555 | 7510128089511349555 | true | -
樱晴 | 7274246029824806155 | 7274246029824806155 | true | -
樱花粉肤 | 7467985496988241204 | 7467985496988241204 | true | effects_adjust_filter(default=1,min=0,max=1)
橘光 | 7127675251961384205 | 7127675251961384205 | true | -
橘海 | 7278615838628924733 | 7278615838628924733 | true | -
橙蓝 | 7127561047048850718 | 7127561047048850718 | true | -
欧若淡彩 | 7479295334930205952 | 7479295334930205952 | true | effects_adjust_filter(default=1,min=0,max=1)
殷粉 | 7169357894868061478 | 7169357894868061478 | true | -
毕业胶片 | 7510863205011393844 | 7510863205011393844 | true | effects_adjust_filter(default=1,min=0,max=1)
气色 | 7417468417852099894 | 7417468417852099894 | true | effects_adjust_filter(default=1,min=0,max=1)
气色透亮 | 7527311213869403402 | 7527311213869403402 | true | effects_adjust_filter(default=1,min=0,max=1)
氧气春日 | 7471717864001506587 | 7471717864001506587 | true | effects_adjust_filter(default=1,min=0,max=1)
氧气甜白 | 7470913918186163468 | 7470913918186163468 | true | effects_adjust_filter(default=1,min=0,max=1)
水光红润 | 7546838732532436224 | 7546838732532436224 | true | effects_adjust_filter(default=1,min=0,max=1)
水墨意境 | 7592199246766542104 | 7592199246766542104 | true | effects_adjust_filter(default=1,min=0,max=1)
沙漫 | 7148776798715776292 | 7148776798715776292 | true | -
沙砾 | 7160580722774920461 | 7160580722774920461 | true | -
沙龙暖调 | 7604669372958788900 | 7604669372958788900 | true | effects_adjust_filter(default=1,min=0,max=1)
治愈奶萌 | 7535396553368948018 | 7535396553368948018 | true | effects_adjust_filter(default=1,min=0,max=1)
法式少女 | 7480196177611230514 | 7480196177611230514 | true | effects_adjust_filter(default=1,min=0,max=1)
法式甜粉 | 7480196167372999973 | 7480196167372999973 | true | effects_adjust_filter(default=1,min=0,max=1)
法餐 | 7127655700532186398 | 7127655700532186398 | true | -
洋气新年 | 7452802627991129380 | 7452802627991129380 | true | effects_adjust_filter(default=1,min=0,max=1)
洛丽塔粉 | 7476109684169133362 | 7476109684169133362 | true | effects_adjust_filter(default=1,min=0,max=1)
浅空 | 7297910428703657227 | 7297910428703657227 | true | effects_adjust_filter(default=1,min=0,max=1)
浅绿微曝 | 7589518503460310296 | 7589518503460310296 | true | effects_adjust_filter(default=1,min=0,max=1)
浅茶 | 7221481120083283257 | 7221481120083283257 | true | -
浅草 | 7195783041376111932 | 7195783041376111932 | true | -
浓咖 | 7526564908188568866 | 7526564908188568866 | true | effects_adjust_filter(default=1,min=0,max=1)
浓调电影 | 7608956042701065487 | 7608956042701065487 | true | effects_adjust_filter(default=1,min=0,max=1)
浓郁增色 | 7578511090758192384 | 7578511090758192384 | true | effects_adjust_filter(default=1,min=0,max=1)
浓郁日落 | 7591499629557075251 | 7591499629557075251 | true | effects_adjust_filter(default=1,min=0,max=1)
浓郁电影感 | 7602322655651400970 | 7602322655651400970 | true | effects_adjust_filter(default=1,min=0,max=1)
浓郁秋意 | 7562593990671895808 | 7562593990671895808 | true | effects_adjust_filter(default=1,min=0,max=1)
浓郁胶卷 | 7499121362351574282 | 7499121362351574282 | true | effects_adjust_filter(default=1,min=0,max=1)
浪漫质感 | 7537336415810489619 | 7537336415810489619 | true | effects_adjust_filter(default=1,min=0,max=1)
浪语 | 7376495406487801139 | 7376495406487801139 | true | effects_adjust_filter(default=1,min=0,max=1)
海上冲浪 | 7527721135824211243 | 7527721135824211243 | true | effects_adjust_filter(default=1,min=0,max=1)
海山 | 7281162426219859255 | 7281162426219859255 | true | -
海松 | 7145394304377163045 | 7145394304377163045 | true | -
海水正蓝 | 7361398032753020201 | 7361398032753020201 | true | effects_adjust_filter(default=1,min=0,max=1)
海盐 | 7473034636436852031 | 7473034636436852031 | true | effects_adjust_filter(default=1,min=0,max=1)
海盐蓝 | 7495702685765651775 | 7495702685765651775 | true | effects_adjust_filter(default=1,min=0,max=1)
海边胶片 | 7497887075627257114 | 7497887075627257114 | true | effects_adjust_filter(default=1,min=0,max=1)
润光 | 7199093300526173501 | 7199093300526173501 | true | -
涩谷 | 7210645355136961852 | 7210645355136961852 | true | -
淡奶油 | 7127668617101020423 | 7127668617101020423 | true | -
深蓝电影感 | 7607867444048317706 | 7607867444048317706 | true | effects_adjust_filter(default=1,min=0,max=1)
清冷国风 | 7493171130753174835 | 7493171130753174835 | true | effects_adjust_filter(default=1,min=0,max=1)
清冷情绪感 | 7602661089280560394 | 7602661089280560394 | true | effects_adjust_filter(default=1,min=0,max=1)
清冷暗黑 | 7398191077364124955 | 7398191077364124955 | true | effects_adjust_filter(default=1,min=0,max=1)
清冷破碎III | 7415242837555416330 | 7415242837555416330 | true | effects_adjust_filter(default=1,min=0,max=1)
清新感 | 7493819626330017078 | 7493819626330017078 | true | effects_adjust_filter(default=1,min=0,max=1)
清新明亮 | 7429759193361435955 | 7429759193361435955 | true | effects_adjust_filter(default=1,min=0,max=1)
清新春日 | 7463798716542111030 | 7463798716542111030 | true | effects_adjust_filter(default=1,min=0,max=1)
清新晴空 | 7456482453444726026 | 7456482453444726026 | true | effects_adjust_filter(default=1,min=0,max=1)
清新暖食 | 7481862972801879346 | 7481862972801879346 | true | effects_adjust_filter(default=1,min=0,max=1)
清新氧晴 | 7459675263652220171 | 7459675263652220171 | true | effects_adjust_filter(default=1,min=0,max=1)
清新绿妍 | 7436078162217274687 | 7436078162217274687 | true | effects_adjust_filter(default=1,min=0,max=1)
清新花妍 | 7478775634630659378 | 7478775634630659378 | true | effects_adjust_filter(default=1,min=0,max=1)
清新质感 | 7456482275618835763 | 7456482275618835763 | true | effects_adjust_filter(default=1,min=0,max=1)
清新透亮 | 7439995840799722815 | 7439995840799722815 | true | effects_adjust_filter(default=1,min=0,max=1)
清新雪肤 | 7441124539016219943 | 7441124539016219943 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰 | 7447719105563610404 | 7447719105563610404 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰ll | 7127669764792634637 | 7127669764792634637 | true | -
清晰严冬 | 7449939197223243058 | 7449939197223243058 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰净透 | 7483183184826420519 | 7483183184826420519 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰增强 | 7436068361622129929 | 7436068361622129929 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰增色 | 7428650549572144411 | 7428650549572144411 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰增质 | 7441960726274559282 | 7441960726274559282 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰提升 | 7443101069539953931 | 7443101069539953931 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰电影 | 7435151579029769511 | 7435151579029769511 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰画质 | 7441541255760284939 | 7441541255760284939 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰自然 | 7473805985388317978 | 7473805985388317978 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰花朵 | 7493197626645531928 | 7493197626645531928 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰萌宠 | 7503810545670311206 | 7503810545670311206 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰质感 | 7442390492307836186 | 7442390492307836186 | true | effects_adjust_filter(default=1,min=0,max=1)
清晰透亮 | 7440517981374893327 | 7440517981374893327 | true | effects_adjust_filter(default=1,min=0,max=1)
清透II | 7472986633399225635 | 7472986633399225635 | true | effects_adjust_filter(default=1,min=0,max=1)
清透光感 | 7493540929874218281 | 7493540929874218281 | true | effects_adjust_filter(default=1,min=0,max=1)
清透感 | 7496156231392873767 | 7496156231392873767 | true | effects_adjust_filter(default=1,min=0,max=1)
清透春日 | 7614215952338636058 | 7614215952338636058 | true | effects_adjust_filter(default=1,min=0,max=1)
清透美食 | 7403664041945681191 | 7403664041945681191 | true | effects_adjust_filter(default=1,min=0,max=1)
清透萌宠 | 7473126624322391308 | 7473126624322391308 | true | effects_adjust_filter(default=1,min=0,max=1)
港风复古 | 7493874443639377164 | 7493874443639377164 | true | effects_adjust_filter(default=1,min=0,max=1)
港风夜景 | 7408952560549104923 | 7408952560549104923 | true | effects_adjust_filter(default=1,min=0,max=1)
港风电影 | 7493845947546455307 | 7493845947546455307 | true | effects_adjust_filter(default=1,min=0,max=1)
湖畔 | 7210609383804390711 | 7210609383804390711 | true | -
漠土 | 7347670931646549282 | 7347670931646549282 | true | -
漫樱 | 7356883843376221475 | 7356883843376221475 | true | -
漫空 | 7210749292888280359 | 7210749292888280359 | true | -
漫荫 | 7210758351595048195 | 7210758351595048195 | true | -
漫银纪元 | 7571383496334150937 | 7571383496334150937 | true | effects_adjust_filter(default=1,min=0,max=1)
漱石 | 7145394477249678606 | 7145394477249678606 | true | -
潘多拉 | 7127620215290039566 | 7127620215290039566 | true | -
灯会 | 7145394908608662814 | 7145394908608662814 | true | -
灯塔 | 7262351970193640715 | 7262351970193640715 | true | effects_adjust_filter(default=1,min=0,max=1)
灰芋 | 7199460195502689574 | 7199460195502689574 | true | -
灰调中性 | 7476126948708617482 | 7476126948708617482 | true | effects_adjust_filter(default=1,min=0,max=1)
灰调日常 | 7484662695443090715 | 7484662695443090715 | true | effects_adjust_filter(default=1,min=0,max=1)
灰麻 | 7312645421271158070 | 7312645421271158070 | true | -
灿金彩带 | 7467879231914118412 | 7467879231914118412 | true | effects_adjust_filter(default=1,min=0,max=1)
炊烟 | 7194083900333755704 | 7194083900333755704 | true | -
烈日 | 7145395383475113230 | 7145395383475113230 | true | -
烈空 | 7246722333010824508 | 7246722333010824508 | true | -
烘挞 | 7160598329817091364 | 7160598329817091364 | true | -
烛光晚餐 | 7575953878076673323 | 7575953878076673323 | true | effects_adjust_filter(default=1,min=0,max=1)
烟橙 | 7131582482608164132 | 7131582482608164132 | true | -
烟火年年 | 7582992418941717823 | 7582992418941717823 | true | effects_adjust_filter(default=1,min=0,max=1)
烟火迎春 | 7595505308848360750 | 7595505308848360750 | true | effects_adjust_filter(default=1,min=0,max=1)
烟花去雾 | 7595588267978837282 | 7595588267978837282 | true | effects_adjust_filter(default=1,min=0,max=1)
烟花灿烂 | 7604545611471408390 | 7604545611471408390 | true | effects_adjust_filter(default=1,min=0,max=1)
烟花璀璨 | 7328363415313993001 | 7328363415313993001 | true | -
烟花璀璨 II | 7462635722969730323 | 7462635722969730323 | true | -
热带季风 | 7377368986276646171 | 7377368986276646171 | true | effects_adjust_filter(default=1,min=0,max=1)
热显宝丽来 | 7542376153407950095 | 7542376153407950095 | true | effects_adjust_filter(default=1,min=0,max=1)
热气腾腾 | 7463372376038755603 | 7463372376038755603 | true | effects_adjust_filter(default=1,min=0,max=1)
焕肤 | 7127674287238008078 | 7127674287238008078 | true | -
焰色 | 7131539023817936158 | 7131539023817936158 | true | -
熏柏 | 7145395127089909028 | 7145395127089909028 | true | -
燃空 | 7226265591760358713 | 7226265591760358713 | true | -
爱丽丝 | 7328694736565439807 | 7328694736565439807 | true | effects_adjust_filter(default=1,min=0,max=1)
爱之城 | 7131656881805741325 | 7131656881805741325 | true | -
爱之城II | 7337929076042222899 | 7337929076042222899 | true | -
牙白 | 7172285234296278309 | 7172285234296278309 | true | -
牛奶肌 | 7473369111490317595 | 7473369111490317595 | true | effects_adjust_filter(default=1,min=0,max=1)
牧野 | 7397751642390564134 | 7397751642390564134 | true | effects_adjust_filter(default=1,min=0,max=1)
独行侠 | 7202485617026977056 | 7202485617026977056 | true | -
猎梦 | 7148806074601164062 | 7148806074601164062 | true | -
玄影灵 | 7405509975939894567 | 7405509975939894567 | true | effects_adjust_filter(default=1,min=0,max=1)
玩趣 | 7177267248753610023 | 7177267248753610023 | true | -
琥珀 | 7295599414180138250 | 7295599414180138250 | true | -
璀璨 | 7468943213143821587 | 7468943213143821587 | true | effects_adjust_filter(default=0.8,min=0,max=1)
甜妹感 | 7486871767642950966 | 7486871767642950966 | true | effects_adjust_filter(default=1,min=0,max=1)
甜心芭比 | 7505303260148878630 | 7505303260148878630 | true | effects_adjust_filter(default=1,min=0,max=1)
田园野餐 | 7374709634088668452 | 7374709634088668452 | true | effects_adjust_filter(default=1,min=0,max=1)
电影光感 | 7575372908076338457 | 7575372908076338457 | true | effects_adjust_filter(default=1,min=0,max=1)
电影叙事感 | 7539542018494663975 | 7539542018494663975 | true | effects_adjust_filter(default=1,min=0,max=1)
电影境遇 | 7611777721500306723 | 7611777721500306723 | true | effects_adjust_filter(default=1,min=0,max=1)
电影增强 | 7439365849703550247 | 7439365849703550247 | true | effects_adjust_filter(default=1,min=0,max=1)
电影增质 | 7435151398783765799 | 7435151398783765799 | true | effects_adjust_filter(default=1,min=0,max=1)
电影大师 | 7569903362355891518 | 7569903362355891518 | true | effects_adjust_filter(default=1,min=0,max=1)
电影往事 | 7604153456365948169 | 7604153456365948169 | true | effects_adjust_filter(default=1,min=0,max=1)
电影感增强 | 7486832436819578151 | 7486832436819578151 | true | effects_adjust_filter(default=1,min=0,max=1)
电影感大片 | 7575521370369428742 | 7575521370369428742 | true | effects_adjust_filter(default=1,min=0,max=1)
电影慢镜 | 7591523217345449279 | 7591523217345449279 | true | effects_adjust_filter(default=1,min=0,max=1)
电影慢镜II | 7592642498489503026 | 7592642498489503026 | true | effects_adjust_filter(default=1,min=0,max=1)
电影柔光 | 7447126702137904420 | 7447126702137904420 | true | intensity(default=0.18,min=0,max=1)
电影校正 | 7494169971136711977 | 7494169971136711977 | true | effects_adjust_filter(default=1,min=0,max=1)
电影独白 | 7595136957605252390 | 7595136957605252390 | true | effects_adjust_filter(default=1,min=0,max=1)
电影画质 | 7472770427245448474 | 7472770427245448474 | true | effects_adjust_filter(default=1,min=0,max=1)
电影葡街 | 7589559390106062132 | 7589559390106062132 | true | effects_adjust_filter(default=1,min=0,max=1)
电影镜头 | 7591844323558165800 | 7591844323558165800 | true | effects_adjust_filter(default=1,min=0,max=1)
画报 | 7239979137404833083 | 7239979137404833083 | true | -
画质修复 | 7507148382536764682 | 7507148382536764682 | true | effects_adjust_filter(default=0.5,min=0,max=1)
画质增蓝 | 7525722154726329650 | 7525722154726329650 | true | effects_adjust_filter(default=1,min=0,max=1)
画质高清 | 7439560136630471963 | 7439560136630471963 | true | effects_adjust_filter(default=1,min=0,max=1)
登高 | 7195925533031435558 | 7195925533031435558 | true | -
白富美 | 7302336985513970963 | 7302336985513970963 | true | -
白瓷亮肤 | 7545707655537397044 | 7545707655537397044 | true | effects_adjust_filter(default=1,min=0,max=1)
白皙丝绸 | 7600637764823993650 | 7600637764823993650 | true | effects_adjust_filter(default=1,min=0,max=1)
白皙去黄 | 7531992666729352482 | 7531992666729352482 | true | effects_adjust_filter(default=1,min=0,max=1)
百川 | 7210616269597314362 | 7210616269597314362 | true | -
盐系 | 7127823742830398757 | 7127823742830398757 | true | -
石山 | 7194091413728922941 | 7194091413728922941 | true | -
砂金 | 7131655685321821477 | 7131655685321821477 | true | -
破晓 | 7348707347419712794 | 7348707347419712794 | true | -
硬朗 | 7127663097162075399 | 7127663097162075399 | true | -
硬朗男孩 | 7524592387742567689 | 7524592387742567689 | true | effects_adjust_filter(default=1,min=0,max=1)
碎芒 | 7148945136280440101 | 7148945136280440101 | true | -
碳烤 | 7363537225620983067 | 7363537225620983067 | true | -
福桔 | 7323020458050260262 | 7323020458050260262 | true | -
福气新年 | 7582612168625982739 | 7582612168625982739 | true | effects_adjust_filter(default=1,min=0,max=1)
福气新春 | 7595423045704027442 | 7595423045704027442 | true | effects_adjust_filter(default=1,min=0,max=1)
福漫 | 7602179574549761305 | 7602179574549761305 | true | effects_adjust_filter(default=1,min=0,max=1)
福运 | 7453122471810714930 | 7453122471810714930 | true | effects_adjust_filter(default=1,min=0,max=1)
禾美 | 7260770496055168310 | 7260770496055168310 | true | effects_adjust_filter(default=1,min=0,max=1)
私语 | 7127674303306419464 | 7127674303306419464 | true | -
秋叶黄 | 7542556208268348712 | 7542556208268348712 | true | effects_adjust_filter(default=1,min=0,max=1)
秋季电影感 | 7540164276858801448 | 7540164276858801448 | true | effects_adjust_filter(default=1,min=0,max=1)
秋意电影感 | 7551307375555185956 | 7551307375555185956 | true | effects_adjust_filter(default=1,min=0,max=1)
秋日物语II | 7404121905780772122 | 7404121905780772122 | true | effects_adjust_filter(default=1,min=0,max=1)
秋日自然 | 7556996788276841791 | 7556996788276841791 | true | effects_adjust_filter(default=1,min=0,max=1)
秋池 | 7145391965717253406 | 7145391965717253406 | true | -
秋波 | 7196920471043050812 | 7196920471043050812 | true | -
秋田胶片 | 7493760868576988443 | 7493760868576988443 | true | effects_adjust_filter(default=1,min=0,max=1)
科切拉 | 7502329862581996854 | 7502329862581996854 | true | effects_adjust_filter(default=1,min=0,max=1)
科幻星球 | 7501988309900528935 | 7501988309900528935 | true | effects_adjust_filter(default=1,min=0,max=1)
简餐 | 7127561998556073247 | 7127561998556073247 | true | -
粉柔撕拉片 | 7503540725334723875 | 7503540725334723875 | true | effects_adjust_filter(default=1,min=0,max=1)
粉橘 | 7131467442789846285 | 7131467442789846285 | true | -
粉白 | 7156647258342034702 | 7156647258342034702 | true | -
粉白微曝光 | 7481194247610174757 | 7481194247610174757 | true | effects_adjust_filter(default=1,min=0,max=1)
粉蓝烟花 | 7462636960557927699 | 7462636960557927699 | true | effects_adjust_filter(default=0.7,min=0,max=1)
粉霞 | 7525754134151105833 | 7525754134151105833 | true | -
素净 | 7351018816215764233 | 7351018816215764233 | true | -
素简 | 7300968790391606567 | 7300968790391606567 | true | -
紫霞时分 | 7507920355613248803 | 7507920355613248803 | true | effects_adjust_filter(default=1,min=0,max=1)
繁花似锦 | 7322666518536359204 | 7322666518536359204 | true | -
繁花如梦 | 7322665314980859177 | 7322665314980859177 | true | -
繁花璀璨 | 7322665617373351231 | 7322665617373351231 | true | -
红运 | 7325421708809096467 | 7325421708809096467 | true | -
纪实电影 | 7493535052098358590 | 7493535052098358590 | true | effects_adjust_filter(default=1,min=0,max=1)
纪实电影胶片 | 7501954865518677267 | 7501954865518677267 | true | effects_adjust_filter(default=1,min=0,max=1)
纱雾 | 7260772961462799627 | 7260772961462799627 | true | -
织乐 | 7148965677376736542 | 7148965677376736542 | true | -
经典港风 | 7449048410004507914 | 7449048410004507914 | true | effects_adjust_filter(default=1,min=0,max=1)
绿妍II | 7361401117672066345 | 7361401117672066345 | true | effects_adjust_filter(default=1,min=0,max=1)
绿野 | 7148817459095670029 | 7148817459095670029 | true | -
绿野漫旅 | 7409674961595518258 | 7409674961595518258 | true | effects_adjust_filter(default=1,min=0,max=1)
缎光肌 | 7551730848282742070 | 7551730848282742070 | true | effects_adjust_filter(default=0.175,min=0,max=1)
美味brunch | 7494869214751182121 | 7494869214751182121 | true | effects_adjust_filter(default=1,min=0,max=1)
美好春日 | 7480550244233809189 | 7480550244233809189 | true | effects_adjust_filter(default=1,min=0,max=1)
美好瞬间 | 7332345211621887251 | 7332345211621887251 | true | -
美拉德 | 7273782607257685309 | 7273782607257685309 | true | -
美食增色 | 7403664465390013735 | 7403664465390013735 | true | effects_adjust_filter(default=1,min=0,max=1)
美高 | 7239236880858877217 | 7239236880858877217 | true | -
羽梦 | 7213573482850880827 | 7213573482850880827 | true | -
聆时 | 7279063581092531510 | 7279063581092531510 | true | effects_adjust_filter(default=1,min=0,max=1)
聚焦 | 7320428711487098153 | 7320428711487098153 | true | -
背景增色 | 7538027894447131967 | 7538027894447131967 | true | effects_adjust_filter(default=1,min=0,max=1)
胶片微曝 | 7578191333169417523 | 7578191333169417523 | true | effects_adjust_filter(default=1,min=0,max=1)
胶片电影 | 7496103061845249316 | 7496103061845249316 | true | effects_adjust_filter(default=1,min=0,max=1)
自然增色 | 7477552975246937380 | 7477552975246937380 | true | effects_adjust_filter(default=1,min=0,max=1)
自然明亮 | 7439995841366035724 | 7439995841366035724 | true | effects_adjust_filter(default=1,min=0,max=1)
自然春色 | 7478210864818965779 | 7478210864818965779 | true | effects_adjust_filter(default=1,min=0,max=1)
艾丽莎 | 7269240546810400011 | 7269240546810400011 | true | -
芭比 | 7259718549634157882 | 7259718549634157882 | true | -
花容 | 7340950375127649577 | 7340950375127649577 | true | effects_adjust_filter(default=1,min=0,max=1)
花火增色 | 7446691478761508108 | 7446691478761508108 | true | effects_adjust_filter(default=1,min=0,max=1)
花间 | 7211008985187487036 | 7211008985187487036 | true | -
花食 | 7261180740283403578 | 7261180740283403578 | true | -
苍橘 | 7131605817958075685 | 7131605817958075685 | true | -
苏打气泡 | 7535720421677731098 | 7535720421677731098 | true | effects_adjust_filter(default=1,min=0,max=1)
苦尽柑来 | 7493339669950729481 | 7493339669950729481 | true | effects_adjust_filter(default=1,min=0,max=1)
苦檀 | 7145391965847162142 | 7145391965847162142 | true | -
英伦复古 | 7481337713443048755 | 7481337713443048755 | true | effects_adjust_filter(default=1,min=0,max=1)
茶卡盐湖 | 7526507478738013476 | 7526507478738013476 | true | effects_adjust_filter(default=1,min=0,max=1)
茶墨 | 7177728466354326822 | 7177728466354326822 | true | -
茶酪 | 7160603159486827783 | 7160603159486827783 | true | -
荒原风光 | 7531037440736349491 | 7531037440736349491 | true | effects_adjust_filter(default=1,min=0,max=1)
莫吉托 | 7131419324622982408 | 7131419324622982408 | true | -
莫奈睡莲 | 7584815680642551102 | 7584815680642551102 | true | effects_adjust_filter(default=1,min=0,max=1)
莫奈花园 | 7500930664041172278 | 7500930664041172278 | true | effects_adjust_filter(default=1,min=0,max=1)
菁润明肤 | 7396300458781936906 | 7396300458781936906 | true | effects_adjust_filter(default=1,min=0,max=1)
萌宠 | 7394022809317526834 | 7394022809317526834 | true | effects_adjust_filter(default=1,min=0,max=1)
落日派对 | 7374708995501739305 | 7374708995501739305 | true | effects_adjust_filter(default=1,min=0,max=1)
落日电影 | 7501223866988039434 | 7501223866988039434 | true | effects_adjust_filter(default=1,min=0,max=1)
落日粉 | 7368141858603666698 | 7368141858603666698 | true | effects_adjust_filter(default=1,min=0,max=1)
落日鎏金 | 7374251948058447158 | 7374251948058447158 | true | effects_adjust_filter(default=1,min=0,max=1)
蒸汽机 | 7232220370667883837 | 7232220370667883837 | true | -
蓝梦核 | 7237440664139484473 | 7237440664139484473 | true | -
蓝橙II | 7337929426493132058 | 7337929426493132058 | true | -
蓝灰 | 7127667757839076645 | 7127667757839076645 | true | -
蓝调 | 7127664822921022734 | 7127664822921022734 | true | -
蓝调烟火 | 7328363887542209828 | 7328363887542209828 | true | -
蓝调舞曲 | 7366562845120646463 | 7366562845120646463 | true | -
蓝都 | 7166470141494955297 | 7166470141494955297 | true | -
蓝金 | 7341300292148907327 | 7341300292148907327 | true | effects_adjust_filter(default=1,min=0,max=1)
蔚蓝海域 | 7487297018998607131 | 7487297018998607131 | true | effects_adjust_filter(default=1,min=0,max=1)
薄绿 | 7344374695053102371 | 7344374695053102371 | true | effects_adjust_filter(default=1,min=0,max=1)
薄荷奶绿 | 7478775705195547930 | 7478775705195547930 | true | effects_adjust_filter(default=1,min=0,max=1)
薰草 | 7199455696017018151 | 7199455696017018151 | true | -
藤宅 | 7159133894975999244 | 7159133894975999244 | true | -
街头 | 7263357855678467364 | 7263357855678467364 | true | -
褪色胶卷 | 7502716416567545099 | 7502716416567545099 | true | effects_adjust_filter(default=1,min=0,max=1)
西冷 | 7131899038625975559 | 7131899038625975559 | true | -
西西里 | 7131488780451663140 | 7131488780451663140 | true | -
西部峡谷 | 7595798301719694654 | 7595798301719694654 | true | effects_adjust_filter(default=1,min=0,max=1)
西雅图 | 7159175960414194982 | 7159175960414194982 | true | -
诗诺 | 7330543523042708790 | 7330543523042708790 | true | effects_adjust_filter(default=1,min=0,max=1)
诗野 | 7385930407901990153 | 7385930407901990153 | true | effects_adjust_filter(default=1,min=0,max=1)
贝果 | 7131656881805856013 | 7131656881805856013 | true | -
质感增蓝 | 7493589321014906162 | 7493589321014906162 | true | effects_adjust_filter(default=1,min=0,max=1)
质感新中式 | 7493945660903787803 | 7493945660903787803 | true | effects_adjust_filter(default=1,min=0,max=1)
质感晴春 | 7482408418578271514 | 7482408418578271514 | true | effects_adjust_filter(default=1,min=0,max=1)
赏味 | 7127608379056459015 | 7127608379056459015 | true | -
超清4K | 7452918022752275762 | 7452918022752275762 | true | effects_adjust_filter(default=1,min=0,max=1)
超清电影 | 7437195358075145484 | 7437195358075145484 | true | effects_adjust_filter(default=1,min=0,max=1)
超清电影卷 | 7475289663381540150 | 7475289663381540150 | true | effects_adjust_filter(default=1,min=0,max=1)
超清画质 | 7460107425375472935 | 7460107425375472935 | true | effects_adjust_filter(default=1,min=0,max=1)
超白 | 7302338645938261287 | 7302338645938261287 | true | -
超透白皙 | 7554056334228917514 | 7554056334228917514 | true | effects_adjust_filter(default=1,min=0,max=1)
超高清 | 7471501720732863753 | 7471501720732863753 | true | effects_adjust_filter(default=1,min=0,max=1)
越岭 | 7193989203930123554 | 7193989203930123554 | true | -
越野 | 7195931118166609190 | 7195931118166609190 | true | -
轻古早 | 7592592527794998580 | 7592592527794998580 | true | effects_adjust_filter(default=1,min=0,max=1)
轻氧夏 | 7522455016272121124 | 7522455016272121124 | true | effects_adjust_filter(default=1,min=0,max=1)
轻肤III | 7387063538507975974 | 7387063538507975974 | true | effects_adjust_filter(default=1,min=0,max=1)
轻胶少女 | 7368463117287804197 | 7368463117287804197 | true | effects_adjust_filter(default=1,min=0,max=1)
过期电影卷 | 7361791960652238143 | 7361791960652238143 | true | -
运动质感 | 7515060642705952011 | 7515060642705952011 | true | effects_adjust_filter(default=1,min=0,max=1)
迷幻 | 7233731748545203493 | 7233731748545203493 | true | -
迷雾 | 7160594413847203085 | 7160594413847203085 | true | -
逆光拯救 | 7503403496117521690 | 7503403496117521690 | true | effects_adjust_filter(default=0.7,min=0,max=1)
逆光提亮 | 7524288987129810214 | 7524288987129810214 | true | effects_adjust_filter(default=1,min=0,max=1)
透氧肌肤 | 7486780026029870386 | 7486780026029870386 | true | effects_adjust_filter(default=1,min=0,max=1)
通透 | 7530582568769522980 | 7530582568769522980 | true | effects_adjust_filter(default=1,min=0,max=1)
通透暖食 | 7409674549467352374 | 7409674549467352374 | true | effects_adjust_filter(default=1,min=0,max=1)
通透氧感 | 7506758417143450890 | 7506758417143450890 | true | effects_adjust_filter(default=1,min=0,max=1)
邂逅 | 7271145889119440147 | 7271145889119440147 | true | -
郁金香 | 7343831195924303123 | 7343831195924303123 | true | effects_adjust_filter(default=1,min=0,max=1)
都卡 | 7341296364598480178 | 7341296364598480178 | true | effects_adjust_filter(default=1,min=0,max=1)
都城 | 7148817291583474980 | 7148817291583474980 | true | -
都市 | 7312646683672825100 | 7312646683672825100 | true | -
都市电影II | 7406976302122618123 | 7406976302122618123 | true | effects_adjust_filter(default=1,min=0,max=1)
酚蓝 | 7131322091839753502 | 7131322091839753502 | true | -
酷感辣妹 | 7506178551725542696 | 7506178551725542696 | true | effects_adjust_filter(default=1,min=0,max=1)
酷绿 | 7281165120980454713 | 7281165120980454713 | true | -
醒春 | 7211006465358843196 | 7211006465358843196 | true | -
里昂 | 7131643870714006821 | 7131643870714006821 | true | -
野林 | 7395470918245502234 | 7395470918245502234 | true | effects_adjust_filter(default=1,min=0,max=1)
野趣 | 7193983160231742772 | 7193983160231742772 | true | -
金姜 | 7233733326517832995 | 7233733326517832995 | true | -
金粉飘落 | 7456773992901397787 | 7456773992901397787 | true | effects_adjust_filter(default=1,min=0,max=1)
铅绿 | 7131509679246675208 | 7131509679246675208 | true | -
银蓝 | 7145394266209127694 | 7145394266209127694 | true | -
镜粉 | 7145390299370638600 | 7145390299370638600 | true | -
闪星 | 7346450662185569555 | 7346450662185569555 | true | -
闪耀派对 | 7471169568484953363 | 7471169568484953363 | true | effects_adjust_filter(default=1,min=0,max=1)
阳光肤 | 7234795543178775868 | 7234795543178775868 | true | -
阴天拯救 | 7361399516454604071 | 7361399516454604071 | true | effects_adjust_filter(default=1,min=0,max=1)
陶瓷肌 | 7234793127867878712 | 7234793127867878712 | true | -
随性 | 7271140658071588132 | 7271140658071588132 | true | -
雀染 | 7145394848361729288 | 7145394848361729288 | true | -
雅西卡 | 7569903893891714329 | 7569903893891714329 | true | effects_adjust_filter(default=1,min=0,max=1)
雨皂 | 7145678373530946824 | 7145678373530946824 | true | -
雨空 | 7196917591909109052 | 7196917591909109052 | true | -
雪地胶片 | 7431914829876694324 | 7431914829876694324 | true | effects_adjust_filter(default=1,min=0,max=1)
雪地胶片II | 7431914902177991970 | 7431914902177991970 | true | effects_adjust_filter(default=1,min=0,max=1)
雪地胶片III | 7431914955747691810 | 7431914955747691810 | true | effects_adjust_filter(default=1,min=0,max=1)
雪挞 | 7262376135202327871 | 7262376135202327871 | true | -
雪白肤III | 7426223181205146890 | 7426223181205146890 | true | effects_adjust_filter(default=1,min=0,max=1)
雪白透亮 | 7564026160212987190 | 7564026160212987190 | true | effects_adjust_filter(default=1,min=0,max=1)
雾都 | 7312646650202262820 | 7312646650202262820 | true | -
雾野 | 7127823362356727077 | 7127823362356727077 | true | -
青提 | 7131290518838938887 | 7131290518838938887 | true | -
青春照 | 7513077194952936767 | 7513077194952936767 | true | effects_adjust_filter(default=1,min=0,max=1)
青春胶片 | 7510888042761096459 | 7510888042761096459 | true | effects_adjust_filter(default=1,min=0,max=1)
青森 | 7145390299106381086 | 7145390299106381086 | true | -
青橙电影感 | 7478335987777572137 | 7478335987777572137 | true | effects_adjust_filter(default=1,min=0,max=1)
青灰 | 7127671508264078599 | 7127671508264078599 | true | -
青蒲 | 7145393992673414407 | 7145393992673414407 | true | -
青黄 | 7127541821332409630 | 7127541821332409630 | true | -
青黄II | 7337932621046910262 | 7337932621046910262 | true | -
韦斯 | 7226989951911562553 | 7226989951911562553 | true | -
韩女古早 | 7538333322636741903 | 7538333322636741903 | true | effects_adjust_filter(default=1,min=0,max=1)
韩式古早 | 7592591080688864546 | 7592591080688864546 | true | effects_adjust_filter(default=1,min=0,max=1)
韩系INS | 7407460599929572627 | 7407460599929572627 | true | effects_adjust_filter(default=1,min=0,max=1)
风味 | 7330579916272012580 | 7330579916272012580 | true | effects_adjust_filter(default=1,min=0,max=1)
风铃II | 7356885346841349410 | 7356885346841349410 | true | effects_adjust_filter(default=1,min=0,max=1)
风铃蓝 | 7261466919688015140 | 7261466919688015140 | true | -
飒意 | 7248568718265978112 | 7248568718265978112 | true | -
食光II | 7478181967532543259 | 7478181967532543259 | true | effects_adjust_filter(default=1,min=0,max=1)
食色 | 7131644140340776205 | 7131644140340776205 | true | -
香浓 | 7330588808666156307 | 7330588808666156307 | true | effects_adjust_filter(default=1,min=0,max=1)
驮月 | 7145394213339860261 | 7145394213339860261 | true | -
高晴画质 | 7486890470149246219 | 7486890470149246219 | true | effects_adjust_filter(default=1,min=0,max=1)
高清 | 7447039744229428534 | 7447039744229428534 | true | effects_adjust_filter(default=1,min=0,max=1)
高清4k电影 | 7454130417562553651 | 7454130417562553651 | true | effects_adjust_filter(default=1,min=0,max=1)
高清II | 7325426821267295551 | 7325426821267295551 | true | -
高清中性灰 | 7476126917280730378 | 7476126917280730378 | true | effects_adjust_filter(default=1,min=0,max=1)
高清亮粉 | 7474611627338239282 | 7474611627338239282 | true | effects_adjust_filter(default=1,min=0,max=1)
高清修复 | 7471501728546966835 | 7471501728546966835 | true | effects_adjust_filter(default=1,min=0,max=1)
高清修复III | 7402847660165713190 | 7402847660165713190 | true | effects_adjust_filter(default=1,min=0,max=1)
高清冷冬 | 7446737538967932186 | 7446737538967932186 | true | effects_adjust_filter(default=1,min=0,max=1)
高清圣诞 | 7446290162922818870 | 7446290162922818870 | true | effects_adjust_filter(default=1,min=0,max=1)
高清增强 | 7426668776491453707 | 7426668776491453707 | true | effects_adjust_filter(default=1,min=0,max=1)
高清增色 | 7440518219409968384 | 7440518219409968384 | true | effects_adjust_filter(default=1,min=0,max=1)
高清增质 | 7436815358410886435 | 7436815358410886435 | true | effects_adjust_filter(default=1,min=0,max=1)
高清寒冬 | 7449684693982743817 | 7449684693982743817 | true | effects_adjust_filter(default=1,min=0,max=1)
高清影视 | 7437098009827036455 | 7437098009827036455 | true | effects_adjust_filter(default=1,min=0,max=1)
高清感 | 7414810241453280549 | 7414810241453280549 | true | effects_adjust_filter(default=1,min=0,max=1)
高清感II | 7414810073731435785 | 7414810073731435785 | true | effects_adjust_filter(default=1,min=0,max=1)
高清感III | 7414810202706447625 | 7414810202706447625 | true | effects_adjust_filter(default=1,min=0,max=1)
高清提亮 | 7439995842477428004 | 7439995842477428004 | true | effects_adjust_filter(default=1,min=0,max=1)
高清提升 | 7443710725773675803 | 7443710725773675803 | true | effects_adjust_filter(default=1,min=0,max=1)
高清春日 | 7476104906924100915 | 7476104906924100915 | true | effects_adjust_filter(default=1,min=0,max=1)
高清晴天 | 7442389591140748570 | 7442389591140748570 | true | effects_adjust_filter(default=1,min=0,max=1)
高清晴日 | 7448290256476065035 | 7448290256476065035 | true | effects_adjust_filter(default=1,min=0,max=1)
高清暖调 | 7431187754379136266 | 7431187754379136266 | true | effects_adjust_filter(default=1,min=0,max=1)
高清润颜 | 7428629277110848768 | 7428629277110848768 | true | effects_adjust_filter(default=1,min=0,max=1)
高清漫晴 | 7442344329114422565 | 7442344329114422565 | true | effects_adjust_filter(default=1,min=0,max=1)
高清焕晴 | 7471955373340101927 | 7471955373340101927 | true | effects_adjust_filter(default=1,min=0,max=1)
高清电影 | 7413062310580800831 | 7413062310580800831 | true | effects_adjust_filter(default=1,min=0,max=1)
高清电影卷 | 7452946862581058853 | 7452946862581058853 | true | effects_adjust_filter(default=1,min=0,max=1)
高清画质 | 7465342226118266162 | 7465342226118266162 | true | effects_adjust_filter(default=1,min=0,max=1)
高清绿妍 | 7451808659320900891 | 7451808659320900891 | true | effects_adjust_filter(default=1,min=0,max=1)
高清美食 | 7435865312907676978 | 7435865312907676978 | true | effects_adjust_filter(default=1,min=0,max=1)
高清自然 | 7469688503262039334 | 7469688503262039334 | true | effects_adjust_filter(default=1,min=0,max=1)
高清质感 | 7433451928773807397 | 7433451928773807397 | true | effects_adjust_filter(default=1,min=0,max=1)
高清雪景 | 7444960692853148955 | 7444960692853148955 | true | effects_adjust_filter(default=1,min=0,max=1)
高清雪肤 | 7447397442603076899 | 7447397442603076899 | true | effects_adjust_filter(default=1,min=0,max=1)
高清鲜明 | 7435675065498275081 | 7435675065498275081 | true | effects_adjust_filter(default=1,min=0,max=1)
高清黑白 | 7429744855724641545 | 7429744855724641545 | true | effects_adjust_filter(default=1,min=0,max=1)
高清默冬 | 7450134286071631141 | 7450134286071631141 | true | effects_adjust_filter(default=1,min=0,max=1)
高级影视 | 7513959933310749991 | 7513959933310749991 | true | effects_adjust_filter(default=1,min=0,max=1)
高级质感 | 7525074000846802227 | 7525074000846802227 | true | effects_adjust_filter(default=1,min=0,max=1)
高街 | 7145394469666376991 | 7145394469666376991 | true | -
高质感电影 | 7528823226357665050 | 7528823226357665050 | true | effects_adjust_filter(default=1,min=0,max=1)
魅影 | 7175076304058895619 | 7175076304058895619 | true | -
魔都 | 7166480345666260263 | 7166480345666260263 | true | -
鲜亮 | 7127615338035858702 | 7127615338035858702 | true | -
鲜明 | 7320434750018047251 | 7320434750018047251 | true | -
鲜明II | 7361400073533820196 | 7361400073533820196 | true | effects_adjust_filter(default=1,min=0,max=1)
鲜明增色 | 7463798839258909963 | 7463798839258909963 | true | effects_adjust_filter(default=1,min=0,max=1)
鲜美 | 7330581892510649636 | 7330581892510649636 | true | effects_adjust_filter(default=1,min=0,max=1)
鲜艳增色 | 7497157143502654732 | 7497157143502654732 | true | effects_adjust_filter(default=1,min=0,max=1)
鲜花增彩 | 7494505446158503179 | 7494505446158503179 | true | effects_adjust_filter(default=1,min=0,max=1)
鲜花增色 | 7493083101426453796 | 7493083101426453796 | true | effects_adjust_filter(default=0.8,min=0,max=1)
鲜花增艳 | 7493457725431631142 | 7493457725431631142 | true | effects_adjust_filter(default=1,min=0,max=1)
鲜花自然 | 7610447734406941994 | 7610447734406941994 | true | effects_adjust_filter(default=1,min=0,max=1)
鲜萃食光 | 7580047192463969560 | 7580047192463969560 | true | effects_adjust_filter(default=1,min=0,max=1)
鸿运新春 | 7595835595054730542 | 7595835595054730542 | true | effects_adjust_filter(default=1,min=0,max=1)
鹅冠 | 7308714123913612607 | 7308714123913612607 | true | -
麋鹿 | 7430673747708792075 | 7430673747708792075 | true | effects_adjust_filter(default=1,min=0,max=1)
黄昏 | 7272330168717430075 | 7272330168717430075 | true | -
黑冰 | 7131522303082466597 | 7131522303082466597 | true | -
黑暗神话 | 7408496787398446362 | 7408496787398446362 | true | -
黑曜 | 7223712396769119545 | 7223712396769119545 | true | -
黑白记忆 | 7533265997478808841 | 7533265997478808841 | true | effects_adjust_filter(default=1,min=0,max=1)
黑金 | 7414902721733479699 | 7414902721733479699 | true | effects_adjust_filter(default=1,min=0,max=1)
黑金红 | 7341266486536768831 | 7341266486536768831 | true | effects_adjust_filter(default=1,min=0,max=1)
黛瓦 | 7226247580018019644 | 7226247580018019644 | true | -
龙舌兰 | 7252674245396942139 | 7252674245396942139 | true | -
```


---

## 附录 G 视频场景特效（1097 条）

- 挂载位置：materials.video_effects[type=video_effect]
- 草稿实际使用编号：effect_id + resource_id
- 作为片段附加效果时通常走 extra_material_refs；作为独立特效轨时走 effect segment.material_id
- 免费 635 条，VIP 462 条
```text
name | effect_id | resource_id | is_vip | params
1998 | 1183068 | 6981791065204331044 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
70s | 634717 | 6706773500792689165 | false | effects_adjust_speed(default=0.33,min=0,max=1)
90s画质 | 634889 | 6760946510910722564 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=0.63,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.58,min=0,max=1); effects_adjust_vertical_chromatic(default=0.51,min=0,max=1)
CCD闪光 | 4007303 | 7130585796020539941 | false | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.65,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_filter(default=0.95,min=0,max=1)
DV录制框 | 934600 | 6878115805498708493 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=0.2,min=0,max=1)
DV界面 | 1164160 | 6974600764027048462 | false | -
I Lose You | 972753 | 6899746903735407117 | false | effects_adjust_speed(default=0.33,min=0,max=1)
I Love You | 972754 | 6899746786294895112 | false | effects_adjust_speed(default=0.33,min=0,max=1)
JVC | 2254788 | 7102302420310430215 | false | effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.35,min=0,max=1); effects_adjust_filter(default=0.9,min=0,max=1)
List边框 | 1181892 | 6981463637676266020 | false | -
MV封面 | 1033288 | 6925314612204147214 | false | effects_adjust_blur(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
New Year | 1483460 | 7041771617315197453 | false | effects_adjust_size(default=0.16,min=0,max=1); effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=0.339,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
PS边框 | 884226 | 6860306184595837448 | false | -
RGB描边 | 1025970 | 6922698007653650957 | false | effects_adjust_speed(default=0.67,min=0,max=1); effects_adjust_horizontal_shift(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
VCR | 931458 | 6876012864679711245 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_sharpen(default=0.3,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
X-Signal | 634719 | 6709706971638927875 | false | effects_adjust_speed(default=0.33,min=0,max=1)
X开幕 | 1162978 | 6974024838000153096 | false | effects_adjust_speed(default=0.33,min=0,max=1)
betamax | 14578173 | 7239937281937642041 | false | effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_blur(default=0.65,min=0,max=1); effects_adjust_sharpen(default=0.25,min=0,max=1); effects_adjust_distortion(default=0.4,min=0,max=1); effects_adjust_texture(default=0.55,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1)
emoji钻石 | 1647776 | 7078694071245476366 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_speed(default=0.548,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
ins界面 | 635133 | 6761646727142314509 | false | -
ins风放大镜 | 1380488 | 6992465511455920676 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1)
kirakira | 693883 | 6706773500142555656 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_number(default=0.33,min=0,max=1)
ktv灯光 | 634197 | 6771299914891661832 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
ktv灯光 II | 1054906 | 6934938159763427876 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
windows弹窗关闭 | 1169934 | 6976562270071427598 | false | effects_adjust_speed(default=0.33,min=0,max=1)
windows弹窗打开 | 1169728 | 6976538396290191880 | false | effects_adjust_speed(default=0.33,min=0,max=1)
丁达尔光线 | 768190 | 6834008866137575950 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
万圣emoji | 1405514 | 7021363005052948999 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
万圣夜 | 951616 | 6888280327949652493 | false | effects_adjust_blur(default=0.25,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
三屏 | 635029 | 6706773500209664515 | false | -
三格漫画 | 635007 | 6795825532668744206 | false | -
下雨 | 635039 | 6734619419890160131 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
不对劲 | 1068128 | 6940134524642660895 | false | -
不规则黑框 | 898673 | 6865921530488951309 | false | effects_adjust_background_animation(default=1,min=0,max=1)
两屏 | 635025 | 6706773500796867075 | false | -
中枪了 | 1100950 | 6950894972291781127 | false | -
乌鸦飞过 | 1113160 | 6955028776094798366 | false | -
九屏 | 635011 | 6719657094741496333 | false | -
九屏跑马灯 | 635031 | 6726773973683540491 | false | -
五彩纸屑 | 1535868 | 7055567263029531143 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_rotate(default=0.8,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1)
五彩缤纷 | 1543542 | 7055594981683106312 | false | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_rotate(default=0.8,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1)
亮片 | 634129 | 6715209448521994755 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
人鱼滤镜 | 634199 | 6766876614862049795 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.75,min=0,max=1); effects_adjust_range(default=1,min=0,max=1)
仙女变身 | 634173 | 6746483363567112707 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
仙女变身 II | 634171 | 6747515070114173447 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
仙女棒 | 35504704 | 7314565034586149403 | false | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
仙尘闪闪 | 1133662 | 6963476143370408485 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
低像素 | 703237 | 6810945511005098509 | false | effects_adjust_texture(default=1,min=0,max=1)
低像素 II | 703239 | 6811399125544735245 | false | effects_adjust_texture(default=1,min=0,max=1)
倒计时 II | 1521390 | 7051887173276013093 | false | effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
像素画 | 1663132 | 7081557169539125791 | false | effects_adjust_color(default=0.8,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_size(default=0.755,min=0,max=1); effects_adjust_number(default=0.688,min=0,max=1); effects_adjust_background_animation(default=0,min=0,max=1)
像素纹理 | 634785 | 6763903685983474189 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
光斑虚化 | 28151372 | 7297154514262430259 | false | effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_range(default=0,min=0,max=1)
光斑飘落 | 972749 | 6899747276718084622 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
光晕 | 634095 | 6714239617916211716 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
光晕 II | 634093 | 6709701759398318604 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
全剧终 | 634079 | 6710109932122804750 | false | -
六屏 | 635013 | 6719657243039502851 | false | -
关月亮 | 634277 | 6774656266833760780 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.33,min=0,max=1)
冰冷实验室 | 1398372 | 7019265849047388680 | false | effects_adjust_range(default=1,min=0,max=1); effects_adjust_intensity(default=0.267,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
冰霜 | 966514 | 6896417042090430989 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
冰霜 II | 1499080 | 7047048873897890334 | false | effects_adjust_speed(default=0.53,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
冲击波 | 1146394 | 6967180577875169799 | false | effects_adjust_speed(default=0.33,min=0,max=1)
冲刺 | 635003 | 6790536507905020430 | false | -
冲刺 II | 635001 | 6781392637216690700 | false | -
冲刺 III | 634981 | 6774324121783243271 | false | -
冲屏闪粉 | 875969 | 6858138911487562248 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
凄凉 | 1113134 | 6955021464684728846 | false | -
几何图形 | 920550 | 6871054818241155592 | false | effects_adjust_speed(default=0.33,min=0,max=1)
刀光剑影 | 634741 | 6740539604509659662 | false | effects_adjust_speed(default=0.33,min=0,max=1)
分屏开幕 | 13525811 | 7232198317671715385 | false | effects_adjust_speed(default=0.7,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1)
初雪 I | 6940749 | 7173558688605540901 | false | effects_adjust_speed(default=0.75,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_size(default=0,min=0,max=1)
剪纸边框 | 1038710 | 6926456664228893191 | false | -
加载甜蜜 | 1031291 | 6924873263994638856 | false | effects_adjust_speed(default=0.33,min=0,max=1)
动感模糊 | 1368758 | 7009120603055591943 | false | effects_adjust_horizontal_shift(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.85,min=0,max=1)
动感色卡 | 1524680 | 7052644171240182280 | false | effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
动感荧光 | 635125 | 6755761739242934798 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
动感蓝带 | 1155430 | 6970598283378954765 | false | effects_adjust_speed(default=0.33,min=0,max=1)
单色涂鸦 | 20412423 | 7265798651019006521 | false | effects_adjust_color(default=0.3,min=0.05,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_number(default=0.57,min=0,max=0.81); effects_adjust_horizontal_shift(default=0.7,min=0,max=1); effects_adjust_background_animation(default=0.7,min=0,max=1); effects_adjust_size(default=0.1,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1); effects_adjust_range(default=0,min=0,max=1)
南瓜光斑 | 1403930 | 6992844454453318157 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
南瓜笑脸 | 951196 | 6888208083202347534 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
卷动 | 634735 | 6719657168292811278 | false | effects_adjust_speed(default=0.33,min=0,max=1)
原相机 | 635137 | 6753416178909057549 | false | -
友友商店 | 1173234 | 6977709836993565220 | false | -
反转片 I | 5114825 | 7153084450593575454 | false | effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_intensity(default=0,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
发光 | 1126104 | 6961701455262650916 | false | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_rotate(default=0.4,min=0,max=1)
取景框 | 635089 | 6712739398984667651 | false | effects_adjust_noise(default=1,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
取景框 II | 920935 | 6871187132195541517 | false | -
变形了 | 1068127 | 6940134629282157064 | false | -
变彩色 | 634053 | 6720492336788279815 | false | effects_adjust_speed(default=0.33,min=0,max=1)
变清晰 | 634019 | 6719658716750156291 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.25,min=0,max=1)
变清晰 II | 1146596 | 6948352810895282724 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
变焦推镜 | 27896191 | 7296418835429593651 | false | effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
变秋天 | 1381700 | 7012941093520020004 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
变黑白 | 634055 | 6730911849706951179 | false | effects_adjust_speed(default=0.33,min=0,max=1)
告白氛围 | 635005 | 6798021156331852295 | false | -
咔嚓 | 634073 | 6752780026900386317 | false | effects_adjust_speed(default=0.33,min=0,max=1)
哈哈弹幕 | 1106302 | 6952852858656002590 | false | -
哈苏胶片 | 1646830 | 7078598928056193566 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_noise(default=0.3,min=0,max=1)
唱片 | 1174596 | 6978764021637845541 | false | effects_adjust_intensity(default=0.5,min=0,max=1)
唱片封面 | 1196734 | 6987741974455390734 | false | -
啊啊啊啊 | 1104164 | 6951661272827957790 | false | -
噪点 | 634061 | 6706773498510971404 | false | effects_adjust_noise(default=0.5,min=0,max=1)
四屏 | 635027 | 6706773500490682888 | false | -
回弹摇摆 | 4720539 | 7146090225855369742 | false | effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0,min=0,max=1)
回忆文件夹 | 1227934 | 6998352498062791205 | false | -
回忆胶片 | 1196624 | 6987725478912070174 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1)
圆形虚线放大镜 | 1569306 | 7065242222068765198 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1)
圣诞光斑 | 634209 | 6769436675958379021 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
圣诞星光 | 634207 | 6767219683901837832 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
地狱使者 | 1406882 | 7007684840506003999 | false | effects_adjust_color(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
基础黑框 | 635127 | 6712316216905568772 | false | -
塑料封面 | 703221 | 6814664313496670728 | false | effects_adjust_texture(default=1,min=0,max=1)
塑料封面 II | 703219 | 6814664561082241550 | false | effects_adjust_texture(default=1,min=0,max=1)
塑料封面III | 703217 | 6815457699505902087 | false | effects_adjust_texture(default=1,min=0,max=1)
复古DV | 898868 | 6865959646092333576 | false | effects_adjust_blur(default=0.2,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1)
复古DV II | 909740 | 6869650937841979911 | false | effects_adjust_blur(default=0.2,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1)
复古DV III | 1194896 | 6986958810619318792 | false | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
复古DV IV | 1217306 | 6994703188611830303 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.55,min=0,max=1)
复古发光 | 1212776 | 6993267867214942733 | false | effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_range(default=0.6,min=0,max=1)
复古多格 | 926324 | 6875631945510818318 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1)
复古弹窗 I | 635103 | 6709708058852856327 | false | effects_adjust_noise(default=1,min=0,max=1)
复古弹窗 II | 635143 | 6764667280681865731 | false | -
复古漫画 | 784724 | 6847440397027774984 | false | effects_adjust_filter(default=1,min=0,max=1)
复古甜心 | 1039434 | 6926817888632312333 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
复古碎钻 | 1094804 | 6948700335481295374 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
复古蓝调 | 1648234 | 7078935944459457061 | false | effects_adjust_sharpen(default=0.63,min=0,max=1); effects_adjust_blur(default=0.35,min=0,max=1); effects_adjust_luminance(default=0.63,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
夏日冰块 | 14244311 | 7237437172733710909 | false | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.8,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1); effects_adjust_number(default=0.23,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
夏日泡泡 I | 2488948 | 7104624152044114462 | false | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=0.15,min=0,max=1); effects_adjust_speed(default=0.336,min=0,max=1)
夕阳 | 719376 | 6820595030743323149 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
夕阳 II | 720788 | 6823659895221391886 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
夕阳 III | 762382 | 6836996542310650381 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
夜蝶 | 634175 | 6748376019524129292 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
夜视框 | 635131 | 6733023209978860035 | false | -
大雪 | 635063 | 6767148963503018503 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
大雪纷飞 | 961896 | 6894517304487318024 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
天使光 | 634143 | 6721949326022545928 | false | effects_adjust_intensity(default=1,min=0,max=1)
天使降临 | 1402689 | 7020715912596558366 | false | -
失焦 | 1188938 | 6984625607376114190 | false | effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
夸夸弹幕 | 1115952 | 6956147849356644894 | false | -
夺冠 | 1194360 | 6986857922076611080 | false | effects_adjust_blur(default=0.5,min=0,max=1)
孔明灯 | 635037 | 6734215575196668428 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
孔明灯 II | 1363340 | 7008056576514724365 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1)
字幕投影 | 747802 | 6828021842695950856 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
字幕投影 II | 747910 | 6829181074954785294 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
字幕投影 III | 784366 | 6847378675894063623 | false | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.67,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
字幕投影 IV | 875967 | 6858139153020752397 | false | effects_adjust_background_animation(default=1,min=0,max=1)
定格闪烁 | 1227402 | 6998099471565328926 | false | effects_adjust_speed(default=0.8,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
小剧场 | 1113428 | 6955083477708444174 | false | -
小动物 | 1138384 | 6965381784674505246 | false | -
小花花 | 1039448 | 6926823177670627848 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
少女心 | 1209684 | 6992842225541452325 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1)
少女心事 | 1031294 | 6924872492381114894 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
少女星闪 | 703255 | 6805098811694780942 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
左右摇晃 | 6209717 | 7166435460321907207 | false | effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.25,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1)
布拉格 | 909545 | 6869626257709994510 | false | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
幻彩文字 | 634737 | 6760975890806477319 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=1,min=0,max=1)
幻影 | 634751 | 6723059630676644364 | false | effects_adjust_speed(default=1,min=0,max=1)
幻影 II | 971332 | 6898958754792870413 | false | effects_adjust_speed(default=1,min=0,max=1)
幻术摇摆 | 1038152 | 6926400232615842318 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
幻觉 | 634723 | 6709706311455478285 | false | effects_adjust_speed(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
广角 | 1700284 | 7086792017837036046 | false | effects_adjust_intensity(default=0.45,min=0,max=1)
庆祝彩带 | 1189232 | 6984685757508096520 | false | effects_adjust_speed(default=0.33,min=0,max=1)
开幕 | 631211 | 6706773534074491403 | false | -
开幕  II | 631213 | 6708899027976458760 | false | -
强锐化 | 634783 | 6711567084741988876 | false | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.62,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
录像带 | 634887 | 6706773534074475012 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.45,min=0,max=1); effects_adjust_vertical_chromatic(default=0.4,min=0,max=1)
录像带 II | 634811 | 6771299859803673101 | false | effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1)
录像带 III | 703251 | 6804357689859117581 | false | -
录制框 | 634801 | 6709725898762883595 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.67,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
录制边框 | 635121 | 6720541178044879367 | false | -
录制边框 II | 635119 | 6720541079080276484 | false | -
录制边框 III | 961624 | 6894451240382501389 | false | -
录制边框 IIII | 634063 | 6723065859260027403 | false | -
彩信 | 1418386 | 7023692066152518152 | false | effects_adjust_vertical_shift(default=0.7,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1)
彩噪画质 | 4253680 | 7135711291473138184 | false | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.15,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_blur(default=0.15,min=0,max=1); effects_adjust_sharpen(default=0.35,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1)
彩带 | 1381644 | 7012933493663470088 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
彩色描边 | 1143666 | 6966904744564494878 | false | -
彩色漫画 | 634947 | 6795430958737658382 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
彩色负片 | 1005840 | 6914995893653475847 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
彩虹光 | 634161 | 6719758141573042692 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
彩虹光 II | 634159 | 6738279134692119047 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
彩虹光晕 | 634213 | 6768721870360416782 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
彩虹射线 | 703249 | 6808837459728667144 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
彩虹幻影 | 634281 | 6756845151630397960 | false | effects_adjust_speed(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
彩虹气泡 | 634127 | 6717434470128947725 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
彩虹爱心 | 1031292 | 6924873147053249031 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
彩钻 | 1192480 | 6986188114490298888 | false | effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
心河 | 634273 | 6740821434307711496 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
心跳 | 634753 | 6723068356821258764 | false | effects_adjust_speed(default=0.33,min=0,max=1)
心跳黑框 | 634049 | 6732383404991451656 | false | effects_adjust_speed(default=0.33,min=0,max=1)
必杀技 | 634979 | 6797658471840879111 | false | effects_adjust_speed(default=0.33,min=0,max=1)
必杀技 II | 634977 | 6797346848391565831 | false | effects_adjust_speed(default=0.33,min=0,max=1)
怀旧边框 | 3222474 | 7113820806446060040 | false | effects_adjust_size(default=0.636,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); sticker(default=0.63,min=0,max=1)
怀旧边框 II | 1475190 | 7039331384183230989 | false | -
怦然心动 | 1031293 | 6924872657083044359 | false | effects_adjust_speed(default=0.33,min=0,max=1)
恐怖故事 | 952539 | 6888563496133333511 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
恐怖故事 II | 952540 | 6888562369627165191 | false | effects_adjust_background_animation(default=1,min=0,max=1)
恐怖故事 III | 952742 | 6888594040959275527 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
恐怖综艺 | 1416842 | 7023349285592764941 | false | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.802,min=0,max=1)
恭喜发财 | 1020210 | 6920164595214586381 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
恶灵冲屏 | 1413882 | 7022838857221542414 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
愛 | 756184 | 6831487239164269064 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
我酸了 | 1113430 | 6955083374054609444 | false | -
手帐边框 | 635113 | 6761336384117543438 | false | -
手电筒 | 886132 | 6860757586220683790 | false | effects_adjust_speed(default=0.33,min=0,max=1)
手绘拍摄器 | 1225274 | 6997608849750364708 | false | -
手绘边框 II | 635101 | 6723044276625740296 | false | effects_adjust_speed(default=0.33,min=0,max=1)
扫描光条 | 703271 | 6798379345783034382 | false | effects_adjust_speed(default=0.33,min=0,max=1)
抖动 | 634759 | 6706773500796867084 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.75,min=0,max=1)
折痕 | 703227 | 6810944968396378638 | false | effects_adjust_texture(default=1,min=0,max=1)
折痕 II | 1032270 | 6925250879259939336 | false | effects_adjust_texture(default=1,min=0,max=1)
折痕 III | 1032322 | 6925288456943833608 | false | effects_adjust_texture(default=1,min=0,max=1)
折痕 IV | 1032321 | 6925288650011841031 | false | effects_adjust_texture(default=1,min=0,max=1)
折痕 V | 1032418 | 6925292438391099912 | false | effects_adjust_texture(default=1,min=0,max=1)
报纸:今日热门 | 635091 | 6711575336955417095 | false | effects_adjust_texture(default=1,min=0,max=1)
摇摆 | 634743 | 6709706542674874888 | false | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1)
摇摆 II | 717392 | 6821460674577699342 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=1,min=0,max=1)
撒星星 | 768182 | 6839514681044898311 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
撒星星 II | 788728 | 6849588023714124295 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
撕纸涂鸦边框 | 1153996 | 6969851947306193416 | false | -
播放器 | 635141 | 6758630566578360845 | false | effects_adjust_blur(default=1,min=0,max=1)
播放器 II | 635139 | 6792819149945967111 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
擦拭开幕 | 773560 | 6841459176510591496 | false | effects_adjust_speed(default=0.33,min=0,max=1)
放大镜 | 1520514 | 7051836120224502308 | false | effects_adjust_color(default=1,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1)
放映机 | 1576250 | 7067049946049942030 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1); effects_adjust_intensity(default=0.339,min=0,max=1)
放映机卡顿 | 634775 | 6706773499031081483 | false | effects_adjust_speed(default=0.33,min=0,max=1)
放映机抖动 | 634787 | 6771320983065203213 | false | effects_adjust_range(default=0.25,min=0,max=1)
放映滚动 | 1155966 | 6970890075907297806 | false | -
故障 | 634797 | 6707050322696606222 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_range(default=1,min=0,max=1)
故障 II | 634795 | 6738265357825348103 | false | effects_adjust_speed(default=0.33,min=0,max=1)
故障读条 | 999316 | 6912013942097187336 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.62,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
文字闪动 | 949372 | 6886710931150082573 | false | effects_adjust_speed(default=0.33,min=0,max=1)
斑斓 | 1607458 | 7072258619646939679 | false | effects_adjust_size(default=0,min=0,max=1); effects_adjust_number(default=0.04,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
斜向模糊 | 920936 | 6871185301071467015 | false | effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.25,min=0,max=1)
新年倒数 | 1024106 | 6921952071247729165 | false | effects_adjust_blur(default=1,min=0,max=1)
新年开幕 | 995666 | 6911144014624330248 | false | effects_adjust_speed(default=0.33,min=0,max=1)
新年快乐 | 972751 | 6899747094840480269 | false | effects_adjust_speed(default=0.33,min=0,max=1)
新春杂志 | 8573753 | 7189543383222719034 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
新春祝福 | 8578565 | 7189586707035984441 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_size(default=0.625,min=0,max=1)
方形取景器 | 635099 | 6706773499031097868 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.66,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
方形开幕 | 634043 | 6729055410835165708 | false | -
旋转方块 | 1482636 | 7041504567648850445 | false | effects_adjust_size(default=0.714,min=0,max=1); effects_adjust_speed(default=0.25,min=0,max=1)
日式DV | 1146392 | 6965747262165094942 | false | -
日文字幕 | 881783 | 6858954575701873160 | false | sticker(default=1,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
日落灯 | 1020046 | 6920147678248571406 | false | sticker(default=1,min=0,max=1); effects_adjust_size(default=0.56,min=0,max=1); effects_adjust_horizontal_shift(default=0.61,min=0,max=1); effects_adjust_vertical_shift(default=0.64,min=0,max=1)
时光碎片 | 1157058 | 6971332934288544286 | false | -
时间停止 | 1095262 | 6948722700286169631 | false | -
星光 | 634117 | 6717433583289504268 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星光 II | 634113 | 6715209934738297358 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星光绽放 | 634195 | 6760243564598268420 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星光闪耀 | 1146750 | 6967255188730024455 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星光闪闪 | 920549 | 6871055398107877902 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星夜 | 1364164 | 7008149210159649294 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星星冲屏 | 634193 | 6769007480652435982 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
星星坠落 | 1171606 | 6977257384120947213 | false | effects_adjust_speed(default=0.33,min=0,max=1)
星星彩绘 | 76607736 | 7395533077130252863 | false | effects_adjust_color(default=0,min=0,max=1)
星星投影 | 741906 | 6826530141586330120 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星星灯 | 977478 | 6903072502369489422 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星星闪烁 | 634215 | 6778285088485413384 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星星闪烁 II | 755806 | 6834010357728547335 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星星闪烁 III | 920916 | 6871167583991632391 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星月童话 | 1146749 | 6967255330958873124 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星河 | 634265 | 6734498838410695175 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星河 II | 1372810 | 7010648091049071135 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1)
星火 | 634103 | 6715209198109463054 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星火 II | 986477 | 6907053209173365256 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星火炸开 | 703243 | 6808838081420988942 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星移 | 634267 | 6778284619499311623 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星空 | 635035 | 6734587005872640519 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星辰 | 634271 | 6761722814157296141 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
星辰 I | 1087622 | 6946113717100614158 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
星辰 II | 1089758 | 6946453051368542727 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1)
星辰 III | 1094800 | 6948700154874565156 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1)
星雨 | 634187 | 6766488666261950989 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
春日樱花 | 1041304 | 6927185086685123086 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
春日边框 | 1076064 | 6942800783737885198 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
晴天光线 | 635071 | 6740540037563159047 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
暗夜 | 949350 | 6886698114258833934 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_range(default=1,min=0,max=1)
暗夜归来 | 1402690 | 7020715691355410951 | false | -
暗夜彩虹 | 720808 | 6823658782090859022 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
暗夜彩虹 II | 741832 | 6824046488419570184 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
暗夜彩虹III | 741860 | 6824047157369115150 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
暗夜精灵 | 952536 | 6888573576870367751 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
暗夜蝙蝠 | 1407954 | 7021786820153184775 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
暗角 | 634057 | 6723086142658318860 | false | effects_adjust_texture(default=1,min=0,max=1)
暗黑剪影 | 949388 | 6886718600233619982 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.67,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
暗黑噪点 | 1414024 | 7022896066559218183 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1); effects_adjust_background_animation(default=0.801,min=0,max=1)
暗黑蝙蝠 | 634179 | 6749064512390828548 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.6,min=0,max=1)
曝光 | 1207064 | 6992043513365926408 | false | effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_texture(default=0.6,min=0,max=1)
曝光降低 | 634659 | 6765766949382132232 | false | effects_adjust_speed(default=0.33,min=0,max=1)
月亮投影 | 741892 | 6826529572536717837 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
月亮闪闪 | 931823 | 6876339287038628359 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
月光闪闪 | 986344 | 6906802979861434887 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.75,min=0,max=1)
望远镜 | 761578 | 6834012604759806472 | false | effects_adjust_speed(default=0.33,min=0,max=1)
未来主义 | 1185624 | 6982870068069667365 | false | -
杂志 | 703235 | 6810945952451400200 | false | effects_adjust_texture(default=1,min=0,max=1)
树影 | 703215 | 6815830852035940872 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
树影 II | 719372 | 6820591707617235464 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
格纹纸质 | 703223 | 6815834305084789262 | false | effects_adjust_texture(default=1,min=0,max=1)
格纹纸质 II | 703225 | 6815834434726531597 | false | effects_adjust_texture(default=1,min=0,max=1)
梦境 | 773088 | 6841460732639318542 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
梦境 II | 788039 | 6849235870130639368 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
梦境 III | 774964 | 6843319622385537544 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
梦境 IV | 773086 | 6841460608248844813 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_soft(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
梦幻雪花 | 961480 | 6894208129534267912 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
梦蝶 | 1406766 | 6998050316528652831 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
梦魇 | 1419974 | 7024080087163081229 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
梵高背景 | 1147066 | 6967354298275467807 | false | effects_adjust_intensity(default=0.5,min=0,max=1)
模糊 | 634025 | 6739752823140913675 | false | effects_adjust_blur(default=0.5,min=0,max=1)
模糊开幕 | 634071 | 6758752103092457991 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.25,min=0,max=1)
模糊星光 | 634255 | 6771299961171612174 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.75,min=0,max=1)
模糊星光 II | 703247 | 6806254134619017741 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
模糊闭幕 | 717394 | 6821460725517521416 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.25,min=0,max=1)
横向闭幕 | 931822 | 6876339694825640455 | false | -
横纹故障 | 703269 | 6806254428358709767 | false | effects_adjust_speed(default=0.33,min=0,max=1)
横纹故障 II | 703267 | 6815093228216259079 | false | effects_adjust_speed(default=0.33,min=0,max=1)
樱花朵朵 | 1069014 | 6940448547137393159 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
橘色负片 | 1005839 | 6914995976608420365 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
欧根纱 | 21803568 | 7273334324106105403 | false | effects_adjust_size(default=0.3,min=0,max=0.6); effects_adjust_number(default=1,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_blur(default=0.28,min=0,max=1); effects_adjust_rotate(default=0.125,min=0,max=1)
毛刺 | 634711 | 6709706457543086605 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
毛玻璃 | 1445528 | 7031846864198570532 | false | -
水墨晕染 | 634101 | 6746486938137530884 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
水彩晕染 | 634099 | 6733378866686988803 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
水波纹 | 1068390 | 6940173521905521159 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1)
水波纹投影 | 783644 | 6847018706887774727 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
水滴模糊 | 998722 | 6911935918433636871 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
水滴滚动 | 892170 | 6863328348920091144 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
油画泼墨 | 77243667 | 7398059491545059876 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0.3,min=0,max=1)
油画纹理 | 645833 | 6808442362314887693 | false | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
泡泡 | 703241 | 6806254230614053383 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
泡泡变焦 | 4118383 | 7133105682881974821 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1)
波点彩绘 | 77269362 | 7398099732884623908 | false | effects_adjust_color(default=0.7,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
波纹扭曲 | 63865672 | 7368745372081984035 | false | effects_adjust_sharpen(default=0.35,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_distortion(default=0.55,min=0,max=1)
波纹色差 | 634285 | 6709347834690277892 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1)
流动烟雾 | 18648774 | 7257495407712801317 | false | effects_adjust_size(default=0.7,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1); effects_adjust_filter(default=0.9,min=0,max=1); effects_adjust_texture(default=0.9,min=0,max=1); effects_adjust_color(default=0.9,min=0,max=1)
流星雨 | 1164794 | 6974750495415996936 | false | -
浓雾 | 635047 | 6751566830206194190 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
浪漫氛围 | 634253 | 6790533020215415304 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
浪漫氛围 II | 705081 | 6814667933684339207 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
涂鸦切割边框 | 1153998 | 6969850948969566756 | false | -
淡彩边框 | 635117 | 6753512270598246925 | false | effects_adjust_speed(default=0.33,min=0,max=1)
清新绿格子 | 1141780 | 6966132680211567135 | false | -
渐显开幕 | 634041 | 6722343568188379661 | false | effects_adjust_speed(default=0.33,min=0,max=1)
渐渐放大 | 634067 | 6730912024596845063 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.66,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
渐隐闭幕 | 634039 | 6723050814006366734 | false | effects_adjust_speed(default=0.33,min=0,max=1)
温柔细闪 | 1220300 | 6995497812221760030 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
游戏界面 | 1187140 | 6983877697524994567 | false | -
满屏问号 | 1101078 | 6950902993294201358 | false | -
漏光噪点 | 703229 | 6810944598874001934 | false | effects_adjust_texture(default=1,min=0,max=1)
火光 | 634167 | 6748623656181568011 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
火光刷过 | 705085 | 6803160938603090440 | false | effects_adjust_speed(default=0.33,min=0,max=1)
火光包围 | 705033 | 6803162714148442632 | false | effects_adjust_speed(default=0.33,min=0,max=1)
火光翻滚 | 703263 | 6809889314860700173 | false | effects_adjust_speed(default=0.33,min=0,max=1)
火光蔓延 | 703265 | 6803162375148016135 | false | effects_adjust_speed(default=0.33,min=0,max=1)
灵魂出窍 | 634709 | 6706773500784284172 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=1,min=0,max=1)
炫彩 | 634091 | 6732693992225378828 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
炫彩 II | 1145374 | 6933131104274616840 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
烟花 | 635073 | 6782461740274684424 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
烟花 II | 1373018 | 7010666068997837342 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
烟花 III | 1522424 | 7052201781241057805 | false | effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.336,min=0,max=1)
烟雾 | 634145 | 6733145063997575694 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
烟雾炸开 | 703261 | 6804317747351130638 | false | effects_adjust_speed(default=0.33,min=0,max=1)
爆炸 | 635067 | 6740540228194275844 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心Kira | 965696 | 6896058666357625351 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
爱心bling | 634133 | 6709706255105004045 | false | effects_adjust_size(default=1,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
爱心光斑 | 634135 | 6709706178340852236 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心光斑 II | 634261 | 6791647108974776839 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心光波 | 634191 | 6746014633942848007 | false | effects_adjust_speed(default=0.33,min=0,max=1)
爱心啵啵 | 1031295 | 6924869659476890125 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心射线 | 703257 | 6805099653730669070 | false | effects_adjust_speed(default=0.33,min=0,max=1)
爱心投影 | 741958 | 6828020234876621325 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心方块 | 1480898 | 7041103714647544334 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.634,min=0,max=1)
爱心暗角 | 1033842 | 6925342127807271431 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.67,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
爱心气泡 | 634235 | 6792405144655893005 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心泡泡 | 949386 | 6886709503136371207 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心爆炸 | 824444 | 6855563744123032071 | false | effects_adjust_speed(default=0.33,min=0,max=1)
爱心缤纷 | 634259 | 6790534436153725448 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心缤纷 II | 634257 | 6792092999468716558 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
爱心跳动 | 634275 | 6790547496394297863 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
爱心跳动 II | 875970 | 6858138763290219021 | false | effects_adjust_speed(default=0.33,min=0,max=1)
爱心闪烁 | 634231 | 6792109800135070222 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
牛皮纸关闭 | 1140082 | 6966139059194303013 | false | effects_adjust_speed(default=0.33,min=0,max=1)
牛皮纸打开 | 1140078 | 6966136913010889223 | false | effects_adjust_speed(default=0.33,min=0,max=1)
牛皮纸边框 I | 1140086 | 6966139444382405134 | false | -
牛皮纸边框 II | 1140085 | 6966139579912950286 | false | -
玫瑰花瓣 | 635051 | 6734619627051028996 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
玻璃破碎 | 999326 | 6912015453892121102 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
甜心投影 | 1552216 | 7058961500060258847 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_number(default=0.1,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.435,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1)
生日快乐 | 972748 | 6899747371593241096 | false | effects_adjust_speed(default=0.33,min=0,max=1)
电光包围 | 703259 | 6809889225144537613 | false | effects_adjust_speed(default=0.33,min=0,max=1)
电光漩涡 | 634975 | 6797341815377760782 | false | effects_adjust_speed(default=0.33,min=0,max=1)
电子屏 | 785074 | 6847692508449739278 | false | effects_adjust_noise(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
电影刮花 | 634789 | 6722366799003783692 | false | effects_adjust_speed(default=0.33,min=0,max=1)
电影感 | 634029 | 6719333680713568771 | false | -
电影感画幅 | 634083 | 6746135410218373646 | false | effects_adjust_range(default=0.5,min=0,max=1)
电脑桌面 | 1482288 | 7026619341839798820 | false | effects_adjust_color(default=0.1,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=0.7,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
电视关机 | 634805 | 6719656840646365707 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.6,min=0,max=1)
电视开机 | 634807 | 6719661856434164237 | false | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.6,min=0,max=1)
电视彩虹屏 | 815546 | 6852503085672043021 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
电视纹理 | 634803 | 6763933311933878791 | false | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1)
画展边框 | 768176 | 6839527903424680456 | false | -
白噪点边框 | 1155426 | 6970599572976439839 | false | -
白胶边框 | 898956 | 6865979592264389127 | false | effects_adjust_texture(default=1,min=0,max=1)
白色描边 | 1107244 | 6953169122649707045 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
白色渐显 | 634037 | 6723790385069429262 | false | effects_adjust_speed(default=0.33,min=0,max=1)
白色爱心 | 904792 | 6868556923503907342 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
白色线框 | 635109 | 6753512551536923149 | false | -
白色边框 | 1164159 | 6974602583411266079 | false | -
百叶窗 | 719380 | 6823654892872143367 | false | effects_adjust_background_animation(default=1,min=0,max=1)
百叶窗 II | 719404 | 6823656768334205454 | false | effects_adjust_background_animation(default=1,min=0,max=1)
监控 | 634941 | 6773542922030682632 | false | effects_adjust_range(default=1,min=0,max=1); effects_adjust_texture(default=0.4,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1)
盗梦空间 | 1419276 | 7024053604596060680 | false | effects_adjust_size(default=0.336,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1); effects_adjust_rotate(default=0.667,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1); effects_adjust_number(default=1,min=0,max=1)
盛世美颜 | 886130 | 6860757421283873293 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
相机网格 | 634051 | 6725730715138265612 | false | -
相纸 | 635093 | 6713856991086776835 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_soft(default=0.7,min=0,max=1)
瞬间模糊 | 979300 | 6903409009210954253 | false | effects_adjust_blur(default=1,min=0,max=1); effects_adjust_range(default=1,min=0,max=1)
破冰 | 1499079 | 7047049192832766477 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
磨砂纹理 | 634027 | 6732693826135134734 | false | effects_adjust_texture(default=1,min=0,max=1)
祝福环绕 | 40453164 | 7324617866056045106 | false | effects_adjust_color(default=0.6,min=0,max=1); effects_adjust_size(default=0.75,min=0,max=1); effects_adjust_horizontal_shift(default=0,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); sticker(default=0.5,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1); effects_adjust_background_animation(default=0.4,min=0,max=1)
福气满满 | 1024408 | 6922029632040473095 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
秋日暖黄 | 1352364 | 7005090271696261640 | false | -
空灵 | 1404120 | 7021096050899292680 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
窗格 | 634781 | 6719656757175521800 | false | effects_adjust_speed(default=0.33,min=0,max=1)
窗格光 | 719378 | 6823659309428118030 | false | effects_adjust_background_animation(default=1,min=0,max=1)
简约边框 | 1475188 | 7039329234170417701 | false | effects_adjust_color(default=1,min=0,max=1)
箭头放大镜 | 1579942 | 7067461440960991752 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.75,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1)
粉红老电视 | 770876 | 6839596824936845838 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
粉红芭比边框 | 1193772 | 6986591867999621668 | false | -
粉色闪粉 | 881784 | 6858953149974057486 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
粉黄渐变 | 1365502 | 7008413208721494559 | false | -
精灵闪粉 | 1146790 | 6967274435963261476 | false | effects_adjust_speed(default=0.33,min=0,max=1)
精细锐化 | 16609879 | 7250368600911909413 | false | effects_adjust_blur(default=0.12,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1); effects_adjust_size(default=0.08,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1)
糖果纸 | 634217 | 6782100631638249998 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
紫色波纹 | 1195758 | 6987321998036701704 | false | -
紫色负片 | 1007834 | 6915313694884762125 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
紫雾 | 948716 | 6886335679681270279 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
繁星点点 | 768166 | 6839577027939406344 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
红晕 | 1373928 | 7011032152380805640 | false | -
纵向开幕 | 931824 | 6876338988437737997 | false | -
纵向模糊 | 634137 | 6716684911840858628 | false | effects_adjust_blur(default=0.5,min=0,max=1)
纸膜边框 I | 1181888 | 6981464043542286879 | false | -
纸膜边框 II | 1181886 | 6981464169736311327 | false | -
纸质撕边 | 784032 | 6843686214025875981 | false | effects_adjust_texture(default=1,min=0,max=1)
纸质边框 | 780656 | 6844765419853582856 | false | effects_adjust_texture(default=1,min=0,max=1)
纸质边框 II | 780658 | 6844832937272152589 | false | -
纸醉金迷 | 1511534 | 7050402737174876702 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_rotate(default=0.8,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1)
细闪 | 785536 | 6847773569435308558 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
细闪 II | 959412 | 6893002658420888078 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
细闪 III | 1134290 | 6963598424113418783 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
美式 | 787752 | 6849214832856535560 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1)
美式 II | 774972 | 6843320153900323335 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
美式 III | 774968 | 6843319785522991623 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
美式 IV | 812078 | 6850006476472193543 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.62,min=0,max=1)
美式 V | 787968 | 6849225862588404237 | false | effects_adjust_size(default=1,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
美漫 | 1181360 | 6981339244547543560 | false | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
羽毛 | 634295 | 6709706658815152643 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
老照片 | 703231 | 6815764475375784462 | false | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
老照片 II | 703233 | 6815767788490068494 | false | effects_adjust_texture(default=1,min=0,max=1)
老照片 III | 719374 | 6813924503148564999 | false | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
老电影 | 635095 | 6706773498506777095 | false | effects_adjust_speed(default=0.33,min=0,max=1)
老电影 II | 898674 | 6865921078858879496 | false | effects_adjust_speed(default=0.33,min=0,max=1)
老电视卡顿 | 634771 | 6706773499052036615 | false | effects_adjust_intensity(default=1,min=0,max=1)
聚光灯 | 634081 | 6750075966053159427 | false | effects_adjust_speed(default=0.33,min=0,max=1)
聚焦 | 635083 | 6710056993287049742 | false | effects_adjust_speed(default=0.33,min=0,max=1)
胡言乱语 | 1102990 | 6951364520048595492 | false | -
胶片 | 635097 | 6708624565657932292 | false | effects_adjust_noise(default=0.2,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
胶片 II | 635087 | 6710090540643258891 | false | effects_adjust_horizontal_chromatic(default=0.55,min=0,max=1); effects_adjust_vertical_chromatic(default=0.55,min=0,max=1)
胶片 III | 773562 | 6841053178406900231 | false | effects_adjust_speed(default=0.33,min=0,max=1)
胶片 IV | 966552 | 6896439221179912718 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
胶片抖动 | 1625760 | 7075213848558440990 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1)
胶片显影 | 744244 | 6830336944111620616 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_soft(default=1,min=0,max=1)
胶片框 | 1164161 | 6974600629268255262 | false | -
胶片框 II | 1164162 | 6974600475999998477 | false | -
胶片框 III | 1196596 | 6987714956401578510 | false | effects_adjust_filter(default=1,min=0,max=1)
胶片漏光 | 705083 | 6815093106841489934 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
胶片漏光 II | 718872 | 6814743838964322829 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
胶片连拍 | 1218011 | 6994787976613990925 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
自然 | 774970 | 6843319885339038216 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
自然 II | 773090 | 6841460795394494990 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
自然 III | 775998 | 6843680748856152584 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
自然 IV | 776000 | 6843680812584407559 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
自然 V | 774966 | 6843319715499086343 | false | effects_adjust_size(default=1,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
色差 | 634059 | 6706773498561303044 | false | effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
色差开幕 | 904723 | 6868546720783929870 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.67,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1)
色差放大 | 945036 | 6883360769992299016 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1)
色差放射 | 634777 | 6716422405511713287 | false | effects_adjust_blur(default=0.25,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.55,min=0,max=1)
色差故障 | 634773 | 6706773498922013191 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.67,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
色差故障 II | 634769 | 6706773498561319428 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
色差星闪 | 982304 | 6904921853635072520 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1)
色差默片 | 634793 | 6719362972239532548 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.75,min=0,max=1)
节日彩带 | 987446 | 6907438556793278983 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
花火 | 634223 | 6767147410671014407 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
花火 II | 986478 | 6907051960180937229 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
花瓣飘落 | 635059 | 6796905369932141064 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
花瓣飞扬 | 635057 | 6796903619762328072 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
荡漾 II | 4493526 | 7140929198763282980 | false | effects_adjust_range(default=0.35,min=0,max=1); effects_adjust_intensity(default=0.35,min=0,max=1)
荡秋千 | 73935190 | 7388040405465436722 | false | -
荧光扫描 | 1482382 | 7041474808986472967 | false | effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
荧光爱心 | 634227 | 6792095053360665096 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
荧光线描 | 634945 | 6795826477590909454 | false | effects_adjust_background_animation(default=1,min=0,max=1)
荧光绿 | 875968 | 6858138988834722312 | false | effects_adjust_background_animation(default=1,min=0,max=1)
荧光蝙蝠 | 948715 | 6886339116561076749 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
荧幕噪点 | 634779 | 6706773534066086413 | false | effects_adjust_speed(default=0.33,min=0,max=1)
荧幕噪点 II | 703253 | 6803161742789579277 | false | effects_adjust_speed(default=0.33,min=0,max=1)
萤光 | 634107 | 6715209844216828420 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
萤光飞舞 | 932242 | 6877098783209951751 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
萤火 | 1357502 | 7006265184050221576 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
落叶 | 635043 | 6740863535674298888 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
落樱 | 1031296 | 6924859706661933576 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
蒸汽波 | 634147 | 6719658860539286020 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
蒸汽波投影 | 747926 | 6830351103272423949 | false | effects_adjust_background_animation(default=1,min=0,max=1)
蒸汽波路灯 | 755808 | 6829184472349413895 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
蒸汽腾腾 | 961482 | 6894200076227318286 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
蓝光扫描 | 17710554 | 7254126209540297274 | false | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1); effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_range(default=0.7,min=0,max=1)
蓝线模糊 | 1019968 | 6920136330563293704 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1)
蓝色负片 | 1005838 | 6914996050382033421 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
蓝色闪电边框 | 1201878 | 6989911842575356446 | false | -
蔡国强烟花 | 8311325 | 7187218013710455354 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.93,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
虚化 | 634065 | 6756397840785740295 | false | effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
蝙蝠Kira | 953420 | 6888977985697747463 | false | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1)
蝴蝶 | 634157 | 6706773499836404228 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
蝴蝶 II | 634155 | 6747586717672280584 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
蝴蝶光斑 | 634183 | 6748307256959308299 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
蝶舞 | 634177 | 6747946665312784910 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
表面模糊 | 15249743 | 7244073793562350140 | false | effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_sharpen(default=0.7,min=0,max=1)
裂开了 | 1082654 | 6944914067702157861 | false | -
视频分割 | 634747 | 6729023693739004419 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.67,min=0,max=1)
视频界面 | 635135 | 6752799091941446147 | false | -
诡异分割 | 1408118 | 7021800634621891109 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.63,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_background_animation(default=0.7,min=0,max=1)
负片闪烁 | 892686 | 6863353894152442375 | false | effects_adjust_speed(default=0.56,min=0,max=1)
财富满满 | 1020906 | 6920520407179072007 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
财富满满 II | 1036164 | 6925663127845474830 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
赞赞赞 | 1543072 | 7057055647472292359 | false | -
蹦迪光 | 634733 | 6716419849544798723 | false | effects_adjust_speed(default=1,min=0,max=1)
蹦迪彩光 | 634731 | 6716450942285255182 | false | effects_adjust_speed(default=0.33,min=0,max=1)
车窗 | 1381596 | 7012926200767058463 | false | -
车窗影 | 761222 | 6834006887415943694 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
轻微抖动 | 18798726 | 7258208250896585274 | false | effects_adjust_range(default=0.15,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
轻微放大 | 634077 | 6791743223522923021 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1)
边缘glitch | 634749 | 6777238992816443912 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1)
边缘加色 | 634757 | 6781315516909752844 | false | effects_adjust_intensity(default=1,min=0,max=1)
边缘加色 II | 634755 | 6790180635555140109 | false | effects_adjust_intensity(default=1,min=0,max=1)
边缘加色 III | 974844 | 6901190770473046535 | false | effects_adjust_intensity(default=1,min=0,max=1)
边缘发光 | 634069 | 6769065553207235086 | false | effects_adjust_luminance(default=0.25,min=0,max=1)
边缘荧光 | 977454 | 6903064458008990215 | false | effects_adjust_intensity(default=1,min=0,max=1)
运动一夏 | 1188619 | 6984393713208267301 | false | effects_adjust_background_animation(default=1,min=0,max=1)
迪斯科 | 634739 | 6756113382840996360 | false | effects_adjust_speed(default=0.33,min=0,max=1)
迷幻烟雾 | 634089 | 6719661667447214605 | false | effects_adjust_background_animation(default=1,min=0,max=1)
迷离 | 634721 | 6706773549362713095 | false | effects_adjust_speed(default=1,min=0,max=1)
迷雾 | 950488 | 6887505634791526926 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
逆光对焦 | 1218244 | 6992032047959118344 | false | effects_adjust_soft(default=0.7,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0.33,min=0,max=1)
选中框 | 635081 | 6712358020417851917 | false | -
邮票边框 | 1382084 | 7012988323387937293 | false | effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1)
金属背景 | 1493772 | 7044853948456374814 | false | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_noise(default=0.505,min=0,max=1); effects_adjust_intensity(default=0.71,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
金片 | 634229 | 6771299796058640908 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金片 II | 1030626 | 6924589854269379079 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金片炸开 | 972750 | 6899747182816006669 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金粉 | 631215 | 6709706378702754312 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金粉 II | 634289 | 6774672940651778573 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金粉 III | 1188618 | 6984393847467938335 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金粉撒落 | 987445 | 6907439016547717646 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金粉旋转 | 1452336 | 7033654301050278431 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金粉聚拢 | 703245 | 6806254339821146637 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
金粉闪闪 | 1453820 | 7034048554318434830 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
钻光 | 634097 | 6723824479216079368 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
钻石碎片 | 1639618 | 7077487066476450340 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1)
镜像 | 1115964 | 6956148985400660517 | false | -
镜头变焦 | 904724 | 6868546663607177736 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.3,min=0,max=1)
镭射边框 | 1480896 | 7041103833056940574 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
长虹玻璃 | 1235644 | 6992081595976913416 | false | effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=0,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
闪亮登场 | 634185 | 6760547949349966350 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
闪亮登场 II | 958186 | 6891946116212855303 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
闪光灯 Ⅰ | 777760 | 6844432942563856904 | false | effects_adjust_speed(default=0.33,min=0,max=1)
闪光震动 | 19279654 | 7260437169389441597 | false | effects_adjust_color(default=0,min=0,max=1); effects_adjust_range(default=0.58,min=0,max=1); effects_adjust_background_animation(default=0,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
闪动 | 634725 | 6717639344577843725 | false | effects_adjust_speed(default=0.33,min=0,max=1)
闪动光斑 | 634181 | 6753169731617821191 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
闪屏 | 634729 | 6758298031608566280 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
闪电 | 635069 | 6734215409513271820 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
闪白 | 634761 | 6706773500792672781 | false | effects_adjust_speed(default=0.33,min=0,max=1)
闪耀星光 | 634219 | 6784346950385799694 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
闪闪 | 909546 | 6869625970437919246 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
闪闪发光 II | 1382870 | 7013264306959553060 | false | effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1)
闪黑 | 892171 | 6863327462470717960 | false | effects_adjust_speed(default=0.33,min=0,max=1)
闪黑II | 12078089 | 7221377929467400765 | false | effects_adjust_speed(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_size(default=0.25,min=0,max=1); effects_adjust_distortion(default=0.4,min=0,max=1)
闭幕 | 634035 | 6725685146323784205 | false | -
闭幕 II | 634033 | 6729065630013592067 | false | -
随机色块 | 1427664 | 7026674824537707038 | false | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_number(default=0.3,min=0,max=1); effects_adjust_color(default=0.6,min=0,max=1)
随机色块 II | 1441868 | 7030742849134006792 | false | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_number(default=0.3,min=0,max=1); effects_adjust_color(default=0.6,min=0,max=1)
随机裁剪 | 1206444 | 6991794787464516127 | false | effects_adjust_filter(default=0.5,min=0,max=1)
隐形人 | 1400804 | 7020318315310486046 | false | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.35,min=0,max=1)
隔行扫描 | 1168118 | 6976152376457564708 | false | effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
雨滴晕开 | 635041 | 6792488562869670414 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
雪窗 | 6431703 | 7168743948528128548 | false | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
雪花 | 1441796 | 7030728702258319909 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
雪花冲屏 | 634203 | 6769435378806952455 | false | effects_adjust_speed(default=0.33,min=0,max=1)
雪花开幕 | 634045 | 6730429759425090059 | false | effects_adjust_speed(default=0.33,min=0,max=1)
雪花故障 | 785064 | 6847689727261282824 | false | effects_adjust_range(default=0.15,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.55,min=0,max=1)
雪花细闪 | 634201 | 6770604155561054734 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
零点解锁 | 6470260 | 6907054642123772430 | false | effects_adjust_blur(default=0.5,min=0,max=1)
雾气 | 635049 | 6734619830449607171 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
雾气 II | 635045 | 6740539818666627588 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
雾气光线 | 635065 | 6715209712129806851 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
震动 | 634075 | 6761645818723176968 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
霓虹投影 | 1552220 | 7058961173743407630 | false | effects_adjust_soft(default=0.8,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_blur(default=0.8,min=0,max=1); effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1)
霓虹摇摆 | 1034626 | 6925387220073320974 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1)
霓虹灯 | 742028 | 6829182808485794311 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
预警 | 1113432 | 6955083255825568264 | false | -
颤抖 | 892172 | 6863326875649839623 | false | effects_adjust_range(default=0.15,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
飘落花瓣 | 634153 | 6719658795661791747 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
飘落闪粉 | 634165 | 6720029963602366979 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
飘落闪粉 II | 634163 | 6720029866504229390 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
飘雪 | 635061 | 6732360625214722572 | false | -
飘雪 II | 635055 | 6763531573594690061 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
飞速计算 | 1102992 | 6951364383477862948 | false | -
马赛克 | 639477 | 6770564289074827784 | false | effects_adjust_blur(default=0.5,min=0,max=1)
高光瞬间 | 1113136 | 6955021144156017188 | false | -
魅力光束 | 705071 | 6814668066882851335 | false | effects_adjust_speed(default=0.33,min=0,max=1)
魔法 | 1232490 | 7000199435372204580 | false | effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_filter(default=0.802,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
魔法变身 | 1136674 | 6964608751231832613 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
魔法边框 | 1401520 | 7020407234798555655 | false | -
魔法边框 II | 1408090 | 7021795690149843463 | false | -
鱼眼 | 901430 | 6867722963865571854 | false | effects_adjust_distortion(default=0.77,min=0,max=1)
黄蓝星芒 | 1232996 | 7000312634574639653 | false | effects_adjust_background_animation(default=1,min=0,max=1)
黑白VHS | 1408072 | 7021795095900852772 | false | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.53,min=0,max=1); effects_adjust_vertical_chromatic(default=0.43,min=0,max=1)
黑白三格 | 635017 | 6719657002571665934 | false | -
黑白漫画 | 634953 | 6795826673993388551 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
黑白漫画 II | 981864 | 6904876576735760904 | false | effects_adjust_filter(default=1,min=0,max=1)
黑白线描 | 634951 | 6795430643154031111 | false | effects_adjust_background_animation(default=1,min=0,max=1)
黑线故障 | 1155300 | 6970572741116170788 | false | -
黑羽毛 | 634151 | 6716441529084285454 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
黑羽毛 II | 634149 | 6751257389422350860 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
黑胶边框 | 898866 | 6865958778265670151 | false | effects_adjust_texture(default=1,min=0,max=1)
黑色噪点 | 952514 | 6888561214125773326 | false | effects_adjust_speed(default=0.33,min=0,max=1)
黑色老电视 | 635123 | 6738276072246219277 | false | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
2024边框 | 39438457 | 7322367359967040037 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
2025气球泡泡 | 101569751 | 7460731559339889203 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
360运镜 | 87985393 | 7430701460901335603 | true | effects_adjust_speed(default=0.333,min=0,max=1)
360运镜 II | 89453641 | 7434813086239822387 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_luminance(default=0.333,min=0,max=1); effects_adjust_blur(default=0.1,min=0,max=1)
3D春联 | 101633856 | 7460821768022790665 | true | effects_adjust_speed(default=0.333,min=0,max=1)
3D环绕 | 98657836 | 7452986473306919433 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
3D环绕屏 | 89952914 | 7436018394580652553 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_size(default=0.32,min=0,max=1)
Bling飘落 | 31620429 | 7306819369571455515 | true | effects_adjust_speed(default=0.15,min=0,max=1); effects_adjust_number(default=0.45,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.9,min=0,max=1); effects_adjust_filter(default=0.45,min=0,max=1)
C300 | 12744891 | 7226241938649780793 | true | effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_soft(default=0.4,min=0,max=1); effects_adjust_noise(default=0.2,min=0,max=1); effects_adjust_sharpen(default=0.3,min=0,max=1); effects_adjust_blur(default=0.55,min=0,max=1)
IXUS | 11068675 | 7213660933942415930 | true | effects_adjust_intensity(default=0.44,min=0,max=1); effects_adjust_texture(default=0.3,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); sticker(default=1,min=0,max=1); effects_adjust_blur(default=0.15,min=0,max=1)
Ins描边 | 20434943 | 7265936765175730744 | true | effects_adjust_color(default=0.1,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.3,min=0,max=1); effects_adjust_speed(default=0.7,min=0,max=1); effects_adjust_range(default=0.7,min=0,max=1); effects_adjust_size(default=0.8,min=0,max=1); effects_adjust_number(default=0.46,min=0,max=1); effects_adjust_filter(default=0.3,min=0,max=1)
PASSION | 88353245 | 7431776147530060314 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
S形运镜 | 26271784 | 7291263159023702584 | true | effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_rotate(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_size(default=0.4,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
W830 | 12732403 | 7226197862529372731 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_sharpen(default=0.8,min=0,max=1)
一刀两断 | 26002592 | 7290460914174661177 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_size(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
丁达尔旋焦 | 59474165 | 7361697260960223759 | true | effects_adjust_texture(default=0.8,min=0,max=1); effects_adjust_filter(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.55,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1); effects_adjust_background_animation(default=0.3,min=0,max=1); effects_adjust_size(default=1,min=0,max=1)
万向镜像 | 82495223 | 7414043485189181978 | true | effects_adjust_rotate(default=0.12,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_blur(default=0.1,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
三段式黑白 | 96240756 | 7447351620641231369 | true | effects_adjust_speed(default=0.333,min=0,max=1)
上上签 | 101569718 | 7460731920393966118 | true | effects_adjust_speed(default=0.333,min=0,max=1)
下雨涟漪 | 89190637 | 7434055685576331786 | true | effects_adjust_speed(default=0.333,min=0,max=1)
丝印涂鸦 | 21210786 | 7270068054040515131 | true | effects_adjust_color(default=0.2,min=0.05,max=1); effects_adjust_intensity(default=0.25,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_number(default=0.57,min=0,max=0.81); effects_adjust_speed(default=0.43,min=0,max=0.7); effects_adjust_texture(default=0.12,min=0,max=0.5)
丝滑运镜 | 71888371 | 7382145257607008809 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.667,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
两屏分割 | 1594946 | 7069602912057430558 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_range(default=0.1,min=0,max=1)
中轴旋转 | 12495253 | 7224407224460775994 | true | effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
二次元运镜 | 97484026 | 7450031573962887731 | true | effects_adjust_speed(default=0.333,min=0,max=1)
云朵绵绵 | 24962948 | 7287143540033851964 | true | effects_adjust_size(default=0.5,min=0,max=1); sticker(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
五星好评 | 7318779 | 7176947440350663223 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_size(default=0.333,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
交叉震闪 | 26216294 | 7291135461697786423 | true | effects_adjust_color(default=0.3,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.3,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1)
仙女棒II | 96135790 | 7447044441463853594 | true | effects_adjust_speed(default=0.333,min=0,max=1)
低保真 | 29478846 | 7300933146923504178 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_noise(default=0.7,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_blur(default=0.75,min=0,max=1); effects_adjust_sharpen(default=0.2,min=0,max=1)
侧移模糊 | 26353150 | 7291553469180154423 | true | effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
信号干扰 | 96240755 | 7447351621220045338 | true | effects_adjust_speed(default=0.333,min=0,max=1)
倒带 | 57670397 | 7358381380687893027 | true | effects_adjust_speed(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.8,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1)
倒计时 | 1485906 | 7042501782014005773 | true | -
倒计时 III | 99131598 | 7454157863196299802 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_size(default=0.375,min=0,max=1)
倒计时II | 97150131 | 7449262940080837129 | true | -
假日闪闪 Ⅱ | 6940703 | 7173558602580365838 | true | effects_adjust_size(default=0.55,min=0,max=1); effects_adjust_number(default=0.15,min=0,max=1); effects_adjust_rotate(default=0.25,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_filter(default=0.65,min=0,max=1)
像素屏闪 | 14975389 | 7242581780866273850 | true | effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_background_animation(default=0.65,min=0,max=1); effects_adjust_color(default=0.15,min=0,max=1); effects_adjust_soft(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
像素扫描 | 50297398 | 7345080472545792521 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_color(default=0.3,min=0,max=1); effects_adjust_size(default=0,min=0,max=1)
像素拉伸 II | 56071748 | 7355396055397044790 | true | effects_adjust_rotate(default=0.6,min=0.2,max=1); effects_adjust_filter(default=0.7,min=0,max=1)
像素排序 | 12385973 | 7223659432419267132 | true | effects_adjust_number(default=0.94,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_noise(default=0,min=0,max=1)
像素故障 | 14523597 | 7239557281942082107 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.4,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
像素爱心 | 1552218 | 7058961362550002212 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
像素震闪 | 52648474 | 7349147660290363944 | true | effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
光线扫描 | 1500914 | 7047492648587760142 | true | effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_color(default=0.38,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1); effects_adjust_number(default=0.15,min=0,max=1)
光线拖影 | 17852396 | 7254547939194835515 | true | effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0.34,min=0,max=1)
光谱扫描 | 18636946 | 7257452387160298021 | true | effects_adjust_background_animation(default=0,min=0,max=1); effects_adjust_intensity(default=0.614,min=0,max=1); effects_adjust_luminance(default=0.642,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_range(default=0.333,min=0,max=1)
兔个好彩头 | 8571129 | 7187795247936574013 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1)
兔兔碎闪 | 8343041 | 7184326422612152887 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_number(default=0.8,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
兔年红包 | 8617039 | 7189544276651414073 | true | effects_adjust_speed(default=0.5,min=0,max=1)
全屏烟花 | 96135791 | 7447044440864068105 | true | -
全屏祝福语 | 101570129 | 7460729732548530698 | true | effects_adjust_speed(default=0.333,min=0,max=1)
全息扫描 | 15772481 | 7246746366108504636 | true | effects_adjust_luminance(default=0.75,min=0,max=1); effects_adjust_blur(default=0.26,min=0,max=1); effects_adjust_background_animation(default=0.4,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=0.57,min=0,max=1); effects_adjust_vertical_shift(default=0.6,min=0,max=1)
分区显色 | 96240753 | 7447351620641231397 | true | effects_adjust_speed(default=0.333,min=0,max=1)
分屏漏光 | 22335555 | 7276332732051886649 | true | effects_adjust_intensity(default=0.5,min=0,max=1); sticker(default=0,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
剪纸窗花 | 100675645 | 7458222774511735305 | true | effects_adjust_speed(default=0.333,min=0,max=1)
动态侦测 | 52247519 | 7348407437877056009 | true | effects_adjust_speed(default=55,min=0,max=100); effects_adjust_number(default=0.7,min=0,max=1); effects_adjust_color(default=0.98,min=0,max=1); sticker(default=0.24,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_background_animation(default=0.2,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_texture(default=0.2,min=0,max=1); effects_adjust_size(default=0.1,min=0,max=1)
动态格 | 1570398 | 7065593660921877028 | true | effects_adjust_size(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
动感光束 | 5779099 | 7162091309375689223 | true | effects_adjust_intensity(default=0.581,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_speed(default=0.8,min=0,max=1); effects_adjust_horizontal_shift(default=0.398,min=0,max=1)
动感变焦 | 47239575 | 7338707315987583488 | true | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
动感扫光 | 50636467 | 7345724656642429452 | true | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_size(default=0.25,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_color(default=0.1,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1)
动感推镜 | 43472640 | 7330964667252085248 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.6,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
动感竖线 | 47905484 | 7339899789795922468 | true | effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_range(default=0.21,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_soft(default=0.4,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1)
动感运镜 | 48296868 | 7340866533943415308 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
十字模糊 | 5508159 | 7156060838334304775 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_shift(default=1,min=0,max=1); effects_adjust_vertical_shift(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1)
十字爆闪 | 26443872 | 7291868496558821915 | true | effects_adjust_intensity(default=0.33,min=0,max=1); effects_adjust_range(default=0.33,min=0,max=1); effects_adjust_luminance(default=0.33,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1)
单向移动 | 12087461 | 7221408305871065661 | true | effects_adjust_speed(default=0.8,min=0,max=1); effects_adjust_rotate(default=0.49,min=0,max=1)
单彩渐变 | 28007443 | 7296751848508101158 | true | effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_rotate(default=0.9,min=0,max=1); effects_adjust_filter(default=0.1,min=0,max=1); effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1)
单色填充 | 3956309 | 7128329164314120717 | true | effects_adjust_range(default=0.76,min=0,max=1); effects_adjust_color(default=0.36,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
卡机 | 1498082 | 7046676785693463071 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
卡通渲染 | 57459941 | 7358012370125328937 | true | effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_color(default=0.9,min=0,max=1); effects_adjust_filter(default=0.75,min=0,max=1); effects_adjust_range(default=0.3,min=0,max=1)
卷轴打开 | 101601751 | 7460778048531468809 | true | effects_adjust_speed(default=0.5,min=0,max=1)
厚卡纸 | 101633890 | 7460821872972665381 | true | effects_adjust_speed(default=0.333,min=0,max=1)
原相机拉近 | 78211648 | 7400658188275552804 | true | effects_adjust_speed(default=0.318,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_size(default=0.78,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
原相机滤镜 | 90036897 | 7436273714724868646 | true | effects_adjust_speed(default=0.2,min=0,max=1)
原相机缩放 | 90036894 | 7436273714724868634 | true | effects_adjust_speed(default=0.333,min=0,max=1)
双重辉光 | 80799118 | 7408494348532191807 | true | effects_adjust_range(default=0.3,min=0,max=1); effects_adjust_horizontal_shift(default=0.3,min=0,max=1); effects_adjust_vertical_chromatic(default=0.7,min=0,max=1); effects_adjust_blur(default=0.8,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1)
发光 II | 51997290 | 7347959501246435850 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
发光HDR | 20444395 | 7265989852099777061 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_range(default=0.6,min=0,max=1); effects_adjust_size(default=0.45,min=0,max=1); effects_adjust_sharpen(default=0.7,min=0,max=1); effects_adjust_background_animation(default=0.9,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.15,min=0,max=1)
取景器 | 4694121 | 7145432172021682725 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.336,min=0,max=1); effects_adjust_filter(default=0.802,min=0,max=1)
变焦烟花 | 95320464 | 7445177785401741874 | true | effects_adjust_speed(default=0.333,min=0,max=1)
变色狙击 | 5418579 | 7146096867544142367 | true | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
变色闪光 | 18628864 | 7257436414965453368 | true | effects_adjust_range(default=0.65,min=0,max=1); effects_adjust_size(default=0.25,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.9,min=0,max=1); effects_adjust_blur(default=0.85,min=0,max=1)
变速推镜 | 47074578 | 7338347637009027618 | true | effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=2); effects_adjust_background_animation(default=1,min=0,max=2); effects_adjust_luminance(default=1,min=0,max=2); effects_adjust_range(default=0.7,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
变速推镜II | 53195413 | 7349154305045172736 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.7,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
可爱圣诞 | 97260688 | 7449596462645645851 | true | -
可爱涂鸦 | 20662139 | 7267137261697765943 | true | sticker(default=0.4,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_range(default=0.18,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1)
吓到失魂 | 4884447 | 7149057547792552456 | true | effects_adjust_range(default=1,min=0,max=1); effects_adjust_filter(default=0.707,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_blur(default=0.1,min=0,max=1)
哈哈镜 | 101947466 | 7461830381428281893 | true | -
噪点屏闪 | 86397729 | 7425529107548475955 | true | effects_adjust_speed(default=0.091,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
噪片映射 | 4002845 | 7130233403898597902 | true | effects_adjust_noise(default=0.343,min=0,max=1); effects_adjust_size(default=0.1,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
圆形分屏 | 28683046 | 7298664552793641522 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.1,min=0,max=1)
圆形烟花 | 95041383 | 7444470107008406066 | true | effects_adjust_speed(default=0.333,min=0,max=1)
圆形监控 | 79985522 | 7405798478032409125 | true | effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_size(default=0.4,min=0,max=1); effects_adjust_noise(default=0.8,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_filter(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
圣诞CD | 96135792 | 7447044441430299173 | true | effects_adjust_speed(default=0.333,min=0,max=1)
圣诞Kira | 95320466 | 7445177785401741850 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
圣诞日记 | 32448752 | 7308639868085604901 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_size(default=0.78,min=0,max=1); effects_adjust_filter(default=0.1,min=0,max=1); effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
圣诞明信片 | 95041382 | 7444470107041960485 | true | effects_adjust_speed(default=0.333,min=0,max=1)
圣诞边框 | 95912239 | 7446622476928307762 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_vertical_shift(default=0.003,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
圣诞限定 | 97032429 | 7448898555621675529 | true | effects_adjust_speed(default=0,min=0,max=1)
复古半调 | 80123254 | 7406210463857381925 | true | effects_adjust_texture(default=1,min=0,max=1)
复古彩虹 | 21148898 | 7269735872445026877 | true | effects_adjust_size(default=0.72,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=0.8); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_texture(default=0.9,min=0,max=1)
复古拼贴 | 20159886 | 7264510800415429177 | true | effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_texture(default=0.6,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=0.1,min=0,max=1); effects_adjust_intensity(default=0.44,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
复古撕纸 | 80123827 | 7406211198057714203 | true | -
复古电视 | 80122613 | 7406209423548355081 | true | -
复古电视机 | 96135789 | 7447044440859873802 | true | effects_adjust_speed(default=0.333,min=0,max=1)
复古紫调 | 21870120 | 7273707462107075130 | true | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_luminance(default=0.34,min=0,max=1); effects_adjust_sharpen(default=0.38,min=0,max=1); effects_adjust_intensity(default=0.26,min=0,max=1); effects_adjust_filter(default=0.56,min=0,max=1)
复古红调 | 7308411 | 7170897764744696356 | true | effects_adjust_size(default=0.8,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_blur(default=0.8,min=0,max=1); effects_adjust_sharpen(default=0.7,min=0,max=1)
复古辉光 | 92005922 | 7439255870900277811 | true | -
复古边框 | 90036896 | 7436273714729062938 | true | effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
复古连拍 | 1644374 | 7078198448045953572 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_noise(default=0.16,min=0,max=1)
复古闪闪 | 1475376 | 7039549945338139150 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_number(default=0.3,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
复古频闪 | 49278125 | 7343141676828856844 | true | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_filter(default=0.85,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
大字祝福 | 101569841 | 7460730608377926195 | true | effects_adjust_speed(default=0.333,min=0,max=1)
大爆竹 | 101483768 | 7460441486266470938 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_size(default=0,min=0,max=1)
失焦CCD | 8556597 | 7189438884340568633 | true | effects_adjust_blur(default=0.3,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_soft(default=0.3,min=0,max=1); effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1)
失焦光斑 | 23238701 | 7280121081208246845 | true | effects_adjust_size(default=0.12,min=0,max=1); effects_adjust_number(default=0.85,min=0,max=1); effects_adjust_filter(default=0.3,min=0,max=1); effects_adjust_speed(default=0.34,min=0,max=1)
夸张信号 | 96240758 | 7447351620645425691 | true | effects_adjust_speed(default=0.333,min=0,max=1)
定格祝福 | 39287043 | 7321603111791890982 | true | effects_adjust_color(default=0.55,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1); effects_adjust_speed(default=0.7,min=0,max=1)
实况开幕 | 63011918 | 7367289783153857024 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1)
密码解锁 | 77292235 | 7398180847427260963 | true | effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_size(default=0.56,min=0,max=1); effects_adjust_intensity(default=0.1,min=0,max=1); effects_adjust_luminance(default=0.2,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1)
对焦DV | 9034919 | 7195792007309038117 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1); effects_adjust_sharpen(default=0.45,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.2,min=0,max=1)
局部推镜 | 29684830 | 7301528497577529906 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.4,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
局部色彩 | 1482682 | 7041515097927193125 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
居中闪切 | 21899077 | 7273800436128158264 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_noise(default=0,min=0,max=1)
屏幕律动 | 3529421 | 7119437097697546782 | true | effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_size(default=0.333,min=0,max=1)
幻动光斑 | 46674042 | 7337641482376974883 | true | effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_size(default=0.3,min=0,max=1)
幻彩故障 | 1005744 | 6912383907191067149 | true | effects_adjust_speed(default=0.33,min=0,max=1)
幻影 I | 10969387 | 7212904257043829307 | true | effects_adjust_speed(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
幻觉 II | 87569749 | 7429260401365226021 | true | effects_adjust_speed(default=0.12,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_size(default=0.25,min=0,max=1); effects_adjust_soft(default=0.05,min=0,max=1)
广告运镜 | 89895356 | 7435897594078827034 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
弯曲故障 | 79148302 | 7403295225700946441 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_distortion(default=0.333,min=0,max=1); effects_adjust_background_animation(default=0.2,min=0,max=1); effects_adjust_texture(default=0.2,min=0,max=1); effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_filter(default=0.699,min=0,max=1); effects_adjust_range(default=0.25,min=0,max=1)
弹动摇镜 | 44400476 | 7332839146907505215 | true | effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1)
弹动旋入 | 69256604 | 7377307494097359371 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
弹性闪动 | 5718993 | 7161280260435087885 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_range(default=0.45,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1)
弹震运镜 | 75492745 | 7392137368624435752 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.667,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
彩光幻影 | 87673618 | 7429623957759726107 | true | effects_adjust_speed(default=0.474,min=0,max=1); effects_adjust_luminance(default=0.714,min=0,max=1); effects_adjust_distortion(default=0.667,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
彩光摇晃 | 58342723 | 7359557508014281268 | true | effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1)
彩光频闪 | 12061167 | 7221126479793361465 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1); effects_adjust_blur(default=0.85,min=0,max=1); effects_adjust_color(default=0.26,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
彩带飘落 | 101569557 | 7460732448666554889 | true | effects_adjust_speed(default=0.333,min=0,max=1)
彩色像素 | 17710540 | 7254126716489044538 | true | effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_blur(default=0.15,min=0,max=1); effects_adjust_background_animation(default=0.3,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0.7,min=0,max=1); effects_adjust_number(default=0.7,min=0,max=1); effects_adjust_size(default=0.27,min=0,max=1)
彩色流光 I | 15698169 | 7246400747665887802 | true | effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_color(default=0.59,min=0,max=1); effects_adjust_rotate(default=0.7,min=0,max=1); effects_adjust_distortion(default=0,min=0,max=1)
彩色流光 II | 16940779 | 7251502652549239354 | true | effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_color(default=0.03,min=0,max=1); effects_adjust_blur(default=0.65,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
彩色流光 III | 15699849 | 7246410407399658043 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_color(default=0.6,min=0,max=1); effects_adjust_range(default=0.2,min=0,max=1); effects_adjust_horizontal_shift(default=0.6,min=0,max=1)
彩色火焰 | 1142428 | 6966855040380178981 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
彩色珠滴 | 12323189 | 7223201236621726264 | true | effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_background_animation(default=0.9,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_size(default=0.26,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
彩色电光 | 22296923 | 7275262942348579389 | true | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_speed(default=0.68,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
彩色碎彩 | 7743725 | 7181402247824151099 | true | effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1)
彩色碎片 | 2148348 | 7101592529811804679 | true | sticker(default=1,min=0,max=1); effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_size(default=0,min=0,max=1)
彩色碎片 II | 2483800 | 7104546559747953166 | true | effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_noise(default=0.2,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1)
彩色碎闪 | 95964975 | 7446672733347254796 | true | effects_adjust_number(default=0.45,min=0,max=1); effects_adjust_intensity(default=0.66,min=0,max=1); effects_adjust_size(default=0.65,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_speed(default=0.25,min=0,max=1)
彩色闪烁 | 12297327 | 7222939637260489274 | true | effects_adjust_color(default=0.55,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_sharpen(default=0.15,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
彩色雪花 | 1235380 | 7001001281166774792 | true | effects_adjust_color(default=0.75,min=0,max=1); effects_adjust_number(default=0.66,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1)
彩虹光影 | 69089511 | 7377004728208593447 | true | effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.4,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_size(default=0.66,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
彩虹棱镜 | 9053951 | 7195867446429880889 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_luminance(default=0.3,min=0,max=1)
彩虹泛光 | 10021925 | 7195112049876144698 | true | effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_number(default=0.7,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1)
彩虹闪屏 | 49499805 | 7343557569589285413 | true | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
彩边频闪 | 54679766 | 7352815372510171688 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
微信祝福 | 102188349 | 7462226660188754458 | true | effects_adjust_speed(default=0.333,min=0,max=1)
微震闪黑 | 69480931 | 7377721589900513818 | true | effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.2,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1)
心花怒放 | 3803337 | 7125743711144645127 | true | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_blur(default=0.8,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0.15,min=0,max=1)
心花怒放III | 96154625 | 7447067834632376869 | true | effects_adjust_speed(default=0.333,min=0,max=1)
心跳 II | 4478025 | 7140620970934407693 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.33,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.36,min=0,max=1)
快速变焦 | 23539651 | 7281494629483024952 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_filter(default=0.3,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.285,min=0,max=1)
快闪运镜 | 62251172 | 7366140711969755674 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1)
怀旧画质 | 79669475 | 7404740894194143763 | true | effects_adjust_texture(default=0.333,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_filter(default=0.3,min=0,max=1); effects_adjust_color(default=0.3,min=0,max=1)
恐怖涂鸦 | 5418578 | 7117142803863310855 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.22,min=0,max=1); effects_adjust_filter(default=0.9,min=0,max=1)
恭喜发财 II | 102289828 | 7462352353199395366 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_vertical_shift(default=0.333,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
慢门拖影 | 37514660 | 7317916065353175579 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_intensity(default=0.14,min=0,max=1)
手写边框 | 3099452 | 7111253709614486029 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_speed(default=0.26,min=0,max=1); sticker(default=1,min=0,max=1)
手持运镜 | 89308029 | 7434412782293881382 | true | effects_adjust_speed(default=0.333,min=0,max=1)
扭动变焦 | 47079994 | 7338354272280515106 | true | effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_distortion(default=0.8,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_luminance(default=0.3,min=0,max=1)
扭曲变焦 | 28941014 | 7299392770534281765 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.2,min=0,max=1); effects_adjust_vertical_shift(default=0,min=0,max=1)
扭曲模糊 | 10694297 | 7210652297754317367 | true | effects_adjust_blur(default=1,min=0,max=1); effects_adjust_vertical_chromatic(default=1,min=0,max=1); effects_adjust_speed(default=0.455,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1)
抖动模糊 | 9780487 | 7202812661405323813 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_range(default=0.2,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
折叠拜年 | 101494014 | 7460466187265118747 | true | effects_adjust_horizontal_shift(default=0.33,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_distortion(default=0.75,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_luminance(default=0.75,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
抽帧拖影 | 54890386 | 7353197719587918362 | true | effects_adjust_blur(default=0.75,min=0,max=1); effects_adjust_range(default=0.8,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1)
拉伸旋镜 | 58077796 | 7359100199437865506 | true | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_distortion(default=0.6,min=0,max=1); effects_adjust_speed(default=0.67,min=0,max=1)
拉扯震动 | 14603013 | 7240010949938123320 | true | effects_adjust_distortion(default=0.4,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1)
拉镜开幕 | 48340294 | 7340923698955686451 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1)
拍照定格 | 57913226 | 7358795504966177292 | true | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1)
拍立得成像 | 97589170 | 7450356960953635354 | true | effects_adjust_speed(default=0.35,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
拖影灯光 | 42028150 | 7328017754584257075 | true | effects_adjust_number(default=0.698,min=0,max=1); effects_adjust_intensity(default=0.9,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_speed(default=0.336,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
拟截图放大镜 | 1478160 | 7028458557058060831 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1)
推拉跟随 | 70944695 | 7380236931893826089 | true | effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
推拉运镜 | 71865342 | 7382100760630137381 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=0.656,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_blur(default=0.849,min=0,max=1)
推近推远 | 89190636 | 7434055685572137523 | true | effects_adjust_speed(default=0.333,min=0,max=1)
摇摇乐 | 101601833 | 7460778162570400265 | true | effects_adjust_speed(default=0.5,min=0,max=1)
摇晃叠影 | 31866711 | 7307264899422360073 | true | effects_adjust_speed(default=0.35,min=0.1,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
摇晃推镜 | 33958767 | 7311585733976789554 | true | effects_adjust_range(default=1,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
摇晃运镜 | 14730265 | 7241063267357954619 | true | effects_adjust_speed(default=0.35,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_size(default=0.8,min=0,max=1)
撕纸定格 | 81222744 | 7409923919739621898 | true | effects_adjust_speed(default=0.333,min=0,max=1)
撕纸特写 | 14014573 | 7235886675845452349 | true | effects_adjust_speed(default=0.35,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
播放界面 | 1647944 | 7078880636584333838 | true | effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_noise(default=0.2,min=0,max=1)
放大镜视角 | 96299420 | 7447417965676335667 | true | effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
故障定格 | 12383111 | 7223652101287580216 | true | effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
故障开幕 | 47063402 | 7338335435959046656 | true | effects_adjust_sharpen(default=0.2,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
故障震闪 | 35954280 | 7315262223213924873 | true | effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.714,min=0,max=1)
散光弹动 | 52013378 | 7347985147662176807 | true | effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1)
散光闪烁 | 47894032 | 7338348256226710016 | true | effects_adjust_intensity(default=0.33,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
数字矩阵 | 17852330 | 7254547645903934010 | true | effects_adjust_blur(default=0.2,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=0.35,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_range(default=0.333,min=0,max=1)
数学公式 | 81347687 | 7410350357768835594 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
斜线震动 | 15332069 | 7244511673409606201 | true | effects_adjust_size(default=0.409,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1); effects_adjust_luminance(default=0.704,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=0.339,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
新年仙女棒 | 39297699 | 7321990419351343653 | true | effects_adjust_size(default=0.45,min=0,max=1); effects_adjust_horizontal_shift(default=0.48,min=0,max=1); effects_adjust_vertical_shift(default=0.78,min=0,max=1); effects_adjust_range(default=0.55,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_intensity(default=0,min=0,max=1)
新年兔气球 | 8629763 | 7189956032095851063 | true | effects_adjust_size(default=0.07,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
新年投影 | 97032431 | 7448898555617481267 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
新年烟花 II | 97041325 | 7448907790933824010 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=0.75,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
新年的一封信 | 101601588 | 7460777723925893683 | true | effects_adjust_speed(default=0.333,min=0,max=1)
新年礼花 | 101222490 | 7459729290070856229 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1)
新年边框 | 101601911 | 7460778303587095077 | true | effects_adjust_speed(default=0.333,min=0,max=1)
新春唱片 | 100675597 | 7458223206294360626 | true | effects_adjust_speed(default=0.333,min=0,max=1)
新春海报 | 102355526 | 7462629172121178633 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=0.1,min=0,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1)
新春边框 | 102355090 | 7462628644221882906 | true | effects_adjust_speed(default=0.333,min=0,max=1)
方形模糊 | 72505526 | 7384032238951731739 | true | effects_adjust_blur(default=0.877,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_color(default=0.25,min=0,max=1); effects_adjust_luminance(default=0.45,min=0,max=1)
旋焦 | 12505491 | 7224445669698703909 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
旋焦推镜 | 53786746 | 7351324357425107519 | true | effects_adjust_intensity(default=0,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
旋转变焦 | 33928843 | 7311544501057622555 | true | effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.15,min=0,max=1); effects_adjust_filter(default=0.15,min=0,max=1)
旋转回弹 | 49499445 | 7343557174058029568 | true | effects_adjust_speed(default=0.66,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_range(default=0.7,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1)
旋转圆球 | 71888863 | 7382147305350107700 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
旋转抖动 | 40324156 | 7324315025558999602 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1)
旋转抖动 II | 51995951 | 7347956961318539826 | true | effects_adjust_speed(default=0.45,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_rotate(default=0.8,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.8,min=0,max=1)
日进斗金 | 96135794 | 7447044440868262426 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
时尚涂鸦 | 76494544 | 7395106209155518987 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
星光变焦 | 78259894 | 7400757039498007079 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
星星变焦 | 6661731 | 7169474672671592991 | true | effects_adjust_size(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_horizontal_shift(default=0.33,min=0,max=1); effects_adjust_background_animation(default=0.7,min=0,max=1)
曝光变焦 | 19104048 | 7259639809491079737 | true | effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_soft(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
曝光扩散 | 47990686 | 7340136879615906344 | true | effects_adjust_luminance(default=0.33,min=0,max=1); effects_adjust_soft(default=0.33,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_intensity(default=0,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
曲线模糊 | 48215352 | 7340622176065688098 | true | effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.35,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=0.366,min=0,max=1); effects_adjust_vertical_shift(default=0.425,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1)
极速旋转 | 49487569 | 7343542497651462708 | true | effects_adjust_speed(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1)
柔和辉光 | 16279737 | 7249209626829263421 | true | effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_range(default=0.55,min=0,max=1); effects_adjust_size(default=0.25,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
梦幻辉光 | 56065875 | 7355386179308491300 | true | effects_adjust_luminance(default=0.55,min=0,max=1); effects_adjust_range(default=0.65,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_soft(default=0.6,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_sharpen(default=0.3,min=0,max=2); effects_adjust_blur(default=0.2,min=0,max=1.5)
模拟拍照 | 53350183 | 7349154734537708084 | true | effects_adjust_blur(default=0.1,min=0,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0,min=0,max=1)
横向闪光 | 14965785 | 7242555690965799483 | true | effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_range(default=0.2,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
横条开幕 | 71626094 | 7381442168759521792 | true | effects_adjust_speed(default=0.667,min=0,max=1); effects_adjust_luminance(default=0.55,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
樱花飘落 | 10348463 | 7207718227382637113 | true | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.1,min=0,max=1); effects_adjust_size(default=0,min=0,max=1)
欧根纱II | 62749085 | 7366882927801537024 | true | effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_rotate(default=0.35,min=0,max=1); effects_adjust_number(default=0.4,min=0,max=1)
气球满屏 | 97260689 | 7449596462649840155 | true | effects_adjust_speed(default=0.333,min=0,max=1)
气球花花 | 13400477 | 7231385092193522235 | true | effects_adjust_speed(default=0.7,min=0,max=1); sticker(default=1,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
氛围边框 | 32599175 | 7308944810646180379 | true | effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_background_animation(default=0,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1.8); effects_adjust_luminance(default=0.1,min=0,max=1)
水光影 | 3687389 | 7122736441053942285 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_distortion(default=0.15,min=0,max=1)
水波倒影 | 35129784 | 7313842878847914547 | true | effects_adjust_vertical_shift(default=0.35,min=0,max=1); effects_adjust_size(default=0.8,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1)
水波模糊 | 1499278 | 7047088638932292127 | true | effects_adjust_horizontal_chromatic(default=0.7,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1)
水波泛起 | 16641371 | 7250433374882370103 | true | effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.1,min=0,max=1); effects_adjust_number(default=0.44,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.3,min=0,max=1); effects_adjust_speed(default=0.46,min=0,max=1)
水波流动 | 4458607 | 7140273505630687780 | true | effects_adjust_distortion(default=0.35,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_number(default=0.6,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.65,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1)
水波负片 | 90036895 | 7436273714733257267 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
水滴扩散 | 12112703 | 7221508316852130362 | true | effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_horizontal_shift(default=0,min=0,max=1); effects_adjust_horizontal_chromatic(default=1,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1)
水雾消散 | 96257972 | 7447371185806905865 | true | -
油画模糊 | 13537551 | 7232232188278739493 | true | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_soft(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_texture(default=0.403,min=0,max=1)
油纸伞 | 101601695 | 7460777943397044745 | true | effects_adjust_speed(default=0.333,min=0,max=1)
法式暖调 | 1747384 | 7090546987170271780 | true | effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_number(default=0.3,min=0,max=1); effects_adjust_range(default=0.2,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
法式涂鸦 | 17395354 | 7253039682877919803 | true | effects_adjust_color(default=0.61,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_number(default=0.7,min=0,max=1); effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_texture(default=0.661,min=0,max=1); effects_adjust_speed(default=0.72,min=0,max=1)
泛光扫描 | 4217252 | 7134989289498087967 | true | effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_luminance(default=0.75,min=0,max=1); effects_adjust_blur(default=0.8,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_background_animation(default=0.33,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_shift(default=0,min=0,max=1)
泛光爆闪 | 17821188 | 7254484266996732476 | true | effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1)
泛光闪动 | 14080033 | 7236298986993226301 | true | effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.35,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
泡泡光斑 | 38547267 | 7320155012036825610 | true | effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_number(default=0.25,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_color(default=0.1,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_blur(default=0.3,min=0,max=1); effects_adjust_soft(default=0.3,min=0,max=1)
泡泡冲屏 | 67466796 | 7373963046693114387 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=0.8)
波动清晰 | 48213992 | 7340620060362281512 | true | effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_distortion(default=0.25,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=0.6,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1)
波浪 | 5574521 | 7159183282632921631 | true | effects_adjust_speed(default=0.9,min=0,max=1); effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_intensity(default=0.78,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1); effects_adjust_horizontal_shift(default=0.8,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
波浪丝印 | 4880117 | 7146406661249307150 | true | effects_adjust_texture(default=0.8,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_size(default=0.1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
波纹闪动 | 44222768 | 7332415663106953769 | true | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
流体冲屏 | 12130415 | 7221730308251456037 | true | effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.4,min=0,max=1); effects_adjust_background_animation(default=0.33,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
流体荡开 | 39315461 | 7322018576125137417 | true | effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
流光碎闪 | 95069546 | 7444520354703217178 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1)
浪漫烟火 | 95912238 | 7446622476928324146 | true | effects_adjust_speed(default=0.333,min=0,max=1)
海报描边 | 4118241 | 7133104392231719431 | true | effects_adjust_noise(default=1,min=0,max=1); effects_adjust_size(default=0.25,min=0,max=1); effects_adjust_number(default=0.9,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1)
海鸥DC | 1520896 | 7051853636548170271 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=1,min=0,max=1); effects_adjust_texture(default=0.7,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1)
涂鸦vlog | 84197797 | 7418860485258252826 | true | effects_adjust_range(default=0,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
涂鸦切开 | 96240757 | 7447351620649619994 | true | effects_adjust_speed(default=0.333,min=0,max=1)
涂鸦抽帧 | 88922989 | 7433322731896050212 | true | effects_adjust_speed(default=0.31,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
涂鸦拍立得 | 80566411 | 7407715616225759807 | true | effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_background_animation(default=0.3,min=0,max=1)
液态分离 | 14742833 | 7241096748184113701 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
滑动打开 | 102385218 | 7462679471246545459 | true | effects_adjust_speed(default=0.333,min=0,max=1)
滑动载入 | 93990334 | 7442210447844971017 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0.75,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_blur(default=0.25,min=0,max=1)
漂浮爱心 | 31585739 | 7306769922535723558 | true | effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_color(default=0.2,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
漏光闪烁 | 82396172 | 7413730211969110537 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_intensity(default=0,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_size(default=0.333,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
漫画负片 | 89895358 | 7435897594070438451 | true | effects_adjust_speed(default=0.333,min=0,max=1)
潮流涂鸦 | 53198933 | 7350240257914180135 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
瀑布开幕 | 54008092 | 7351689682138174006 | true | effects_adjust_speed(default=0.57,min=0,max=1); effects_adjust_intensity(default=0.65,min=0,max=1); effects_adjust_texture(default=0,min=0,max=1); effects_adjust_distortion(default=0.26,min=0,max=1); effects_adjust_range(default=0.25,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1)
瀑布烟花 | 102169716 | 7462213415688213001 | true | effects_adjust_size(default=0.201,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_filter(default=0.1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
灵异幻觉 | 93705701 | 7441568585081688585 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_distortion(default=0.333,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1)
灵魂出窍 II | 28934274 | 7299377358283215398 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.6,min=0,max=1); effects_adjust_background_animation(default=0.85,min=0,max=1)
灿灿金币 | 30737307 | 7304546673215148595 | true | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_soft(default=0.8,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_distortion(default=0.8,min=0,max=1)
灿金彩带 | 33271125 | 7308706488686481947 | true | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.33,min=0,max=1); effects_adjust_filter(default=0.25,min=0,max=1)
炫光变焦 | 1237470 | 7002109122350944781 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_range(default=0.753,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_blur(default=0.8,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
炫光扫描 | 63023070 | 7367314177741820435 | true | effects_adjust_speed(default=0.35,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.66,min=0,max=1)
炸蛇烟花 | 100663283 | 7458204947906040370 | true | effects_adjust_speed(default=0.333,min=0,max=1)
烟火星河 | 97260687 | 7449596462645645874 | true | effects_adjust_speed(default=0.333,min=0,max=1)
烟花2024 | 36744068 | 7308706250731033097 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.77,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_range(default=0.625,min=0,max=1)
烟花2025 | 96021458 | 7446764449010029066 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.77,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_range(default=0.625,min=0,max=1)
烟花光晕 | 95320465 | 7445177785410130469 | true | effects_adjust_speed(default=0.333,min=0,max=1)
烟花孔明灯 | 101569174 | 7460733084413989426 | true | effects_adjust_speed(default=0.333,min=0,max=1)
烟花字 | 101960315 | 7461841371700138505 | true | effects_adjust_speed(default=0.5,min=0,max=1)
热恋 | 9062069 | 7195020880018149944 | true | effects_adjust_size(default=0.45,min=0,max=1); effects_adjust_number(default=0.45,min=0,max=1); effects_adjust_rotate(default=0.06,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1); effects_adjust_range(default=0.55,min=0,max=1); effects_adjust_sharpen(default=0.75,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
爆元宝 | 101569519 | 7460732612668035634 | true | effects_adjust_speed(default=0.333,min=0,max=1)
爆闪锐化 | 12284805 | 7222907722486780472 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_sharpen(default=0.7,min=0,max=1)
爱心下雪 | 89190638 | 7434055685559554569 | true | effects_adjust_speed(default=0.333,min=0,max=1)
爱心扫光 | 39420273 | 7322345920962499123 | true | effects_adjust_luminance(default=0.55,min=0,max=1); effects_adjust_soft(default=0.3,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_size(default=0.8,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
爱心气球 | 20875808 | 7268210584707928634 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
爱心烟花Ⅱ | 98156320 | 7451813291430515210 | true | effects_adjust_speed(default=0.333,min=0,max=1)
爱心软糖 | 43774786 | 7331625316885991970 | true | effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_background_animation(default=0.9,min=0,max=1)
爱心边框 | 1572505 | 7065927898833621511 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1)
猫眼迎财 | 102389141 | 7462694218327134758 | true | effects_adjust_speed(default=0.333,min=0,max=1)
玫瑰冲屏 | 102609449 | 7463437625777459721 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
珠光Kira | 20820466 | 7267917946733728314 | true | effects_adjust_number(default=0.6,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_vertical_shift(default=0.3,min=0,max=1); effects_adjust_range(default=0.7,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1)
珠光碎闪 | 20405527 | 7265695554640810533 | true | effects_adjust_filter(default=0.55,min=0,max=1); effects_adjust_range(default=0.75,min=0,max=1); effects_adjust_size(default=0.65,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_blur(default=0.15,min=0,max=1)
琉璃拖影 | 31428923 | 7306400287323853349 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_range(default=0.45,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1)
电光描边 | 2721906 | 7106762731960668703 | true | effects_adjust_color(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1)
电光波动 | 29755128 | 7301674026173207066 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=2); effects_adjust_color(default=0.03,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
电光爆闪 | 31478585 | 7306471467397419547 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_distortion(default=0,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
电光爆闪 II | 52650215 | 7349150013441708559 | true | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1)
电光爱心 | 2724410 | 7106779118867321357 | true | effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_speed(default=0.419,min=0,max=1); effects_adjust_intensity(default=0.473,min=0,max=1); effects_adjust_color(default=0.59,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=1,min=0,max=1)
电子复古粉 | 89153641 | 7434001622113456678 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
电音故障 | 15772327 | 7246745900473651773 | true | effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.58,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
画质清晰 | 52400085 | 7348707427165934107 | true | effects_adjust_luminance(default=0.25,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_sharpen(default=0.8,min=0,max=2); effects_adjust_blur(default=0.3,min=0,max=1.5); effects_adjust_range(default=0.7,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_soft(default=0.333,min=0,max=1)
白鸽 | 71992424 | 7382490757770252827 | true | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
相机抓拍 | 92805703 | 7439935845156524583 | true | effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=0.42,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1)
相机框抖动 | 96240754 | 7447351621207462426 | true | effects_adjust_speed(default=0.333,min=0,max=1)
相片定格 | 20350863 | 7265526511220822586 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0.85,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
真爱至上 | 94166372 | 7442582812139459110 | true | effects_adjust_speed(default=0.333,min=0,max=1)
矩形闪白 | 89308030 | 7434412782289703450 | true | effects_adjust_speed(default=0.333,min=0,max=1)
矩阵频闪 | 31403673 | 7306346511367934491 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.33,min=0,max=1); effects_adjust_color(default=0.88,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1)
碎闪描边 | 4007289 | 7130585329609740814 | true | effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_color(default=0.55,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1)
磁带DV | 2211756 | 7101987162526061070 | true | effects_adjust_sharpen(default=0.3,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_size(default=0.1,min=0,max=1); effects_adjust_color(default=0.6,min=0,max=1); effects_adjust_texture(default=0.3,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
磨砂水晶 | 1729610 | 7090380952605561381 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.4,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1)
神龙纳福 | 41485429 | 7326853354615738889 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.65,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
秋日暖阳 | 5408805 | 7156868464894808583 | true | effects_adjust_blur(default=0.45,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0,min=0,max=1)
移轴模糊 | 15780929 | 7246784641384845861 | true | effects_adjust_range(default=0.1,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_filter(default=0,min=0,max=1)
竖向开幕 | 72501890 | 7384009190836015654 | true | effects_adjust_blur(default=0.877,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.6,min=0,max=1)
竖向闪光 | 10976911 | 7212938795702817338 | true | effects_adjust_number(default=0.8,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_range(default=0.69,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
竖线屏闪 | 30666842 | 7304258446658900489 | true | effects_adjust_luminance(default=1.7,min=0,max=2.3); effects_adjust_blur(default=1,min=0,max=2.5); effects_adjust_range(default=0.15,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=2); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
竖闪模糊 | 26216108 | 7291135061494075960 | true | effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1)
童趣闪电 | 88507650 | 7432192373163037222 | true | effects_adjust_speed(default=0.333,min=0,max=1)
粉雪 | 28549704 | 7298283919944716827 | true | effects_adjust_background_animation(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.95,min=0,max=1)
粒子放射 | 11587497 | 7217716815407878693 | true | effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
精致辉光 | 63611181 | 7368344527494451712 | true | effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_range(default=0.85,min=0,max=1); effects_adjust_size(default=0.4,min=0,max=1); effects_adjust_soft(default=0.6,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.4,min=0,max=1)
紫光夜 | 34184103 | 7311995150962528778 | true | effects_adjust_number(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
繁花棱镜II | 21150170 | 7269749564658160184 | true | effects_adjust_background_animation(default=0.8,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.3,min=0,max=1)
红包来了 | 39289351 | 7320154851793441307 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
红包转转 | 102355143 | 7462628759770763826 | true | effects_adjust_speed(default=0.333,min=0,max=1)
红蓝魔 | 3675609 | 7122384870294163975 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
红边模糊 | 4007601 | 7130591331700707876 | true | effects_adjust_blur(default=0.9,min=0,max=1); effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_filter(default=0.9,min=0,max=1)
纵向跳动 | 8626971 | 7190200556692967995 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_vertical_chromatic(default=1,min=0,max=1)
纸质抽帧 | 83272772 | 7416333380603613737 | true | effects_adjust_speed(default=0.1,min=0,max=1); effects_adjust_size(default=0.333,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
线光变速 | 63209940 | 7367628113062138377 | true | effects_adjust_intensity(default=0.3,min=0,max=1); effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_horizontal_shift(default=0.6,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1)
绚丽光斑 | 95331639 | 7445196904868090419 | true | effects_adjust_speed(default=0.67,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_noise(default=0.75,min=0,max=1)
缤纷 | 1607634 | 7072268839303516709 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_number(default=0.3,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
缤纷彩带 | 95320463 | 7445177785405936138 | true | effects_adjust_speed(default=0.333,min=0,max=1)
缤纷烟花 | 35751784 | 7314928469819789850 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.77,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
缩放运镜 | 90036898 | 7436273714733257253 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
网点丝印 | 4879935 | 7146404902971904548 | true | effects_adjust_texture(default=0.6,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
群蝶飞舞 | 51832286 | 7347658324956942883 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
羽毛飘落 | 70529088 | 7379513630837969445 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_speed(default=0.35,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=0.26,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.108,min=0,max=1)
翻转变焦 | 28934164 | 7299377095107416585 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_intensity(default=0.45,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_sharpen(default=0.4,min=0,max=1); effects_adjust_luminance(default=0.4,min=0,max=1)
翻转开幕 | 14020695 | 7235902836188385852 | true | effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_color(default=0.1,min=0,max=1)
老式DV | 1426168 | 7026261220961292807 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_sharpen(default=0.63,min=0,max=1); effects_adjust_noise(default=0.3,min=0,max=1)
聚光灯金粉 | 101569261 | 7460732843547693577 | true | effects_adjust_speed(default=0.333,min=0,max=1)
聚焦色散 | 88045350 | 7430786234508644875 | true | effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.125,min=0,max=1); effects_adjust_sharpen(default=0.2,min=0,max=1)
胶卷 | 101569809 | 7460730844018119205 | true | effects_adjust_speed(default=0.333,min=0,max=1)
胶片V | 5050659 | 7151967279817691662 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
胶片冷绿 | 4837281 | 7146524414312452645 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
胶片暖棕 | 4837280 | 7145385234320593439 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1)
胶片滚动 | 1655466 | 7080354236956938782 | true | effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
胶片漏光III | 90546418 | 7437386424036364827 | true | effects_adjust_speed(default=0.333,min=0,max=1)
胶片翻转 | 87654332 | 7429592751961805348 | true | effects_adjust_speed(default=0.48,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
胶片边框 | 97032432 | 7448898555617481243 | true | -
胶片闪切 | 72761923 | 7384745950608101924 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1)
脉搏跳动 | 1522814 | 7052226294972420621 | true | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.9,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_range(default=0.7,min=0,max=1)
腾云驾雾 | 79942991 | 7405560326650860042 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=0,min=0,max=1)
色差震闪 | 55932216 | 7355109046694711871 | true | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_vertical_chromatic(default=0.5,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_color(default=0.3,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
色散冲击 | 67503542 | 7374053937369846307 | true | effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.6,min=0,max=1); effects_adjust_vertical_chromatic(default=0.6,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1)
色散故障 | 14972687 | 7242574690638631479 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
节奏热成像 | 83369566 | 7416626838232896012 | true | effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_luminance(default=0.4,min=0,max=1)
花屏故障 | 86397374 | 7425528614847779379 | true | effects_adjust_speed(default=0.091,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
花屏故障 II | 75855950 | 7392894917720150565 | true | effects_adjust_intensity(default=0.75,min=0,max=1); effects_adjust_luminance(default=0,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1)
花瓣环绕 | 50608291 | 7345688874577826342 | true | effects_adjust_size(default=0,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.333,min=0,max=1)
荧光星河 | 97032428 | 7448898556410204681 | true | effects_adjust_speed(default=0.333,min=0,max=1)
菱形光斑 | 40449614 | 7316813562783994395 | true | effects_adjust_filter(default=0.55,min=0,max=1); effects_adjust_range(default=0.25,min=0,max=1); effects_adjust_color(default=0.23,min=0,max=1); effects_adjust_blur(default=0.65,min=0,max=1); effects_adjust_speed(default=0.45,min=0,max=1); effects_adjust_vertical_shift(default=0.75,min=0,max=1)
菱形变焦 | 4841353 | 7147943538120987166 | true | effects_adjust_size(default=0.521,min=0,max=1); effects_adjust_intensity(default=0.72,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_horizontal_shift(default=0.33,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1)
落叶 II | 5418631 | 7153556255263429151 | true | effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
蓝光爆闪 | 25450329 | 7288655540341707324 | true | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_speed(default=0.65,min=0.01,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_color(default=0.8,min=0,max=1)
蓝色丝印 | 4097661 | 7131985730791805448 | true | effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_size(default=0.7,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
虹光旋入 | 69273433 | 7377352335028130367 | true | effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.66,min=0,max=1)
蛇形走位 | 101569875 | 7460729982474523163 | true | effects_adjust_speed(default=0.333,min=0,max=1)
蛇蛇涂鸦 | 101570158 | 7460729365366575667 | true | effects_adjust_speed(default=0.333,min=0,max=1)
西海岸涂鸦 | 97254884 | 7449588013115380251 | true | -
视频播放 | 4668537 | 7144915597308989988 | true | effects_adjust_filter(default=0.8,min=0,max=1)
记忆存档 | 101569592 | 7460732200074351142 | true | effects_adjust_speed(default=0.333,min=0,max=1)
诡异故障 | 86397483 | 7425528781156127258 | true | effects_adjust_speed(default=0.091,min=0,max=1)
负片分屏 | 22907949 | 7278974994623763003 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.33,min=0,max=1)
负片描边 | 89308031 | 7434412782285492746 | true | effects_adjust_speed(default=0.333,min=0,max=1)
负片涂鸦 | 5477607 | 7157966185571553822 | true | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
负片涂鸦 II | 13379581 | 7231111030028374584 | true | effects_adjust_texture(default=0.6,min=0,max=1); effects_adjust_size(default=0.4,min=0,max=1); effects_adjust_speed(default=0.75,min=0,max=1); effects_adjust_noise(default=0.32,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
负片涂鸦 III | 20745376 | 7267517097775731261 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0,min=0,max=1)
负片游移 | 1787254 | 7091488033555354120 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1)
负片频闪 | 5155369 | 7153575555554611720 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_speed(default=0.45,min=0,max=1); effects_adjust_filter(default=0.85,min=0,max=1)
负片频闪 II | 83794424 | 7417726471868781110 | true | effects_adjust_speed(default=0.091,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1)
贴身粒子 | 94976472 | 7444407996911718949 | true | effects_adjust_number(default=0.18,min=0,max=1); effects_adjust_speed(default=0.34,min=0,max=1); effects_adjust_size(default=0.18,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_distortion(default=0.24,min=0,max=1)
超大光斑 | 6691829 | 7171321435200164383 | true | effects_adjust_size(default=1,min=0,max=1); effects_adjust_number(default=0.1,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_filter(default=0.2,min=0,max=1)
超强锐化 | 3950243 | 7129336892121682468 | true | effects_adjust_sharpen(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.35,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
跟随运镜 | 28956878 | 7299426452896748042 | true | effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.15,min=0,max=1); effects_adjust_vertical_shift(default=0.3,min=0,max=1); effects_adjust_speed(default=0.15,min=0,max=1)
跟随运镜 II | 48362872 | 7340954638184616467 | true | effects_adjust_range(default=0,min=0,max=1); effects_adjust_horizontal_shift(default=0.4,min=0.1,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.8,min=0,max=1)
跳色四宫格 | 96240759 | 7447351620641247754 | true | effects_adjust_speed(default=0.333,min=0,max=1)
车窗 II | 4795296 | 7109280482025542157 | true | effects_adjust_range(default=0.55,min=0,max=1); effects_adjust_intensity(default=0.45,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); sticker(default=0.35,min=0,max=1)
转运祝福 | 101959980 | 7461840876596105766 | true | effects_adjust_speed(default=0.5,min=0,max=1)
轻微故障 | 86397588 | 7425528929454133786 | true | effects_adjust_speed(default=0.091,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_sharpen(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
辉光开幕 | 47051728 | 7338322046822126114 | true | effects_adjust_texture(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_luminance(default=0.75,min=0,max=1); effects_adjust_color(default=0.27,min=0,max=1); effects_adjust_blur(default=0.4,min=0,max=1)
边缘扫光 | 39434745 | 7322363012092793353 | true | effects_adjust_soft(default=0.75,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_blur(default=0.6,min=0,max=1); effects_adjust_range(default=0.6,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
迎接2025 | 97032430 | 7448898555621675571 | true | effects_adjust_speed(default=0.333,min=0,max=1)
迷幻故障 | 20440246 | 7265960462330630714 | true | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
迷幻荡漾 | 12324741 | 7223208176206746173 | true | effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=0.55,min=0,max=1); effects_adjust_speed(default=0.7,min=0,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
迷幻震动 | 14438877 | 7238863029775897148 | true | effects_adjust_distortion(default=0.65,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_color(default=0.6,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1)
重复变焦 | 5719311 | 7161285099667853831 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_texture(default=0.65,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
重复震闪 | 16610415 | 7250369682207674938 | true | effects_adjust_luminance(default=0.8,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_blur(default=0.7,min=0,max=1); effects_adjust_range(default=0.25,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1)
金元宝 | 102547299 | 7463321874349429258 | true | effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_size(default=0.9,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.3,min=0,max=1)
金币掉落 | 96107626 | 7447018501778182666 | true | effects_adjust_speed(default=0.333,min=0,max=1)
金粉飘落 | 100068434 | 7456695082293400115 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_filter(default=0.15,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_size(default=0.15,min=0,max=1)
金色碎片 | 2622164 | 7106040163402256927 | true | effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_noise(default=0.3,min=0,max=1)
金色辉光 | 95041384 | 7444470107004211763 | true | effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1)
金色雪花 | 95041381 | 7444470107000017435 | true | effects_adjust_speed(default=0.333,min=0,max=1)
金蛇贺岁 | 101569782 | 7460731076856517129 | true | effects_adjust_speed(default=0.333,min=0,max=1)
金边闪烁 | 30855689 | 7304832158466576947 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
金银珠宝 | 97573972 | 7450336559141753395 | true | effects_adjust_speed(default=0.333,min=0,max=1)
金鱼漂浮 | 98209671 | 7451879925545439795 | true | effects_adjust_speed(default=0.333,min=0,max=1)
铅笔涂鸦 | 81202828 | 7409883232667177499 | true | effects_adjust_speed(default=0.333,min=0,max=1)
银杏飘落 | 28024643 | 7296789290724364850 | true | effects_adjust_luminance(default=0.4,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_speed(default=0,min=0.1,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_blur(default=0.1,min=0,max=1)
银蛇缠绕 | 101977565 | 7461865163826663945 | true | effects_adjust_speed(default=0.333,min=0,max=1)
闪光弹跳 | 10660327 | 7210315941396091447 | true | effects_adjust_speed(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.2,min=0,max=1)
闪光灯 II | 4795220 | 7143919857539486238 | true | effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_intensity(default=0.65,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
闪光灯IV | 22328905 | 7276317197658493498 | true | effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1)
闪电扭曲 | 42913127 | 7329871968298078759 | true | effects_adjust_luminance(default=0.666,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
闪白 II | 23489443 | 7281219213828559397 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=2)
闪粉胶片 | 97260690 | 7449596462658228762 | true | effects_adjust_speed(default=0.333,min=0,max=1)
随机闪切 | 20816436 | 7267909305519575608 | true | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.2,min=0,max=1)
随机马赛克 | 29099986 | 7299769859900969510 | true | effects_adjust_size(default=0.28,min=0,max=1); effects_adjust_number(default=0.22,min=0,max=1); effects_adjust_filter(default=0.3,min=0,max=1); effects_adjust_color(default=0.9,min=0,max=1); effects_adjust_background_animation(default=0.9,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1)
隔行DV | 11331317 | 7215598241558041125 | true | effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_sharpen(default=0.2,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.2,min=0,max=1)
雨季 I | 6731496 | 7149065282768605732 | true | effects_adjust_blur(default=0.16,min=0,max=0.8); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.336,min=0,max=1)
雨滴 | 79016931 | 7402879770079269403 | true | effects_adjust_size(default=1,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_range(default=0,min=0,max=1)
雨滴2 | 81600389 | 7411360993369920015 | true | effects_adjust_size(default=1,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_blur(default=0,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_noise(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_range(default=0,min=0,max=1)
雪花光斑 | 27986887 | 7296707597707514406 | true | effects_adjust_background_animation(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_filter(default=0.3,min=0,max=1); effects_adjust_color(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.1,min=0,max=1); sticker(default=0.6,min=0,max=1)
雪花变色 | 95041385 | 7444470107000017417 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
雪花散落 | 97032426 | 7448898556401816115 | true | effects_adjust_speed(default=0.333,min=0,max=1)
雪雾 | 30305488 | 7303380658934518323 | true | sticker(default=0.28,min=0,max=1); effects_adjust_filter(default=0.9,min=0,max=1); effects_adjust_texture(default=0.9,min=0,max=1); effects_adjust_background_animation(default=0.3,min=0,max=1)
零帧起手 | 89895357 | 7435897594070438426 | true | effects_adjust_speed(default=0.333,min=0,max=1)
雾镜 II | 6731657 | 7147920433604465159 | true | effects_adjust_blur(default=0.6,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
震动光束 | 15775885 | 7246758527992074811 | true | effects_adjust_intensity(default=0.42,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.16,min=0,max=1); effects_adjust_luminance(default=0.49,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_range(default=0.75,min=0,max=1)
震动发光 | 16303237 | 7249264623226982968 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_soft(default=0.6,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.8,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.5,min=0,max=1)
震动屏闪 | 6733311 | 7171697545154925069 | true | effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_range(default=0.7,min=0,max=1)
震动扫光 | 67503342 | 7374053409546048052 | true | effects_adjust_intensity(default=0.4,min=0,max=1); effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_color(default=0.2,min=0,max=1); effects_adjust_horizontal_shift(default=0.4,min=0,max=1); effects_adjust_vertical_shift(default=0.4,min=0,max=1)
震动推镜 | 50238678 | 7345004981029704233 | true | effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0.22,min=0,max=1)
震闪渐黑 | 30662744 | 7304249285577544201 | true | effects_adjust_intensity(default=0.2,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_range(default=0.3,min=0,max=1); effects_adjust_speed(default=0.5,min=0.1,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
霓虹光线 | 17710570 | 7254125922222084663 | true | effects_adjust_luminance(default=0.45,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_color(default=0.8,min=0,max=1); effects_adjust_range(default=0.8,min=0,max=1); effects_adjust_horizontal_shift(default=0,min=0,max=1)
霓虹闪切 | 50455778 | 7345353688774349348 | true | effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_luminance(default=0.825,min=0,max=1); effects_adjust_horizontal_chromatic(default=1,min=0,max=1)
飞机窗 | 83837896 | 7417827699902648868 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_size(default=0,min=0,max=0.7); effects_adjust_luminance(default=0.35,min=0,max=0.7)
马赛克闪切 | 32503798 | 7308712918902641203 | true | effects_adjust_size(default=0.4,min=0,max=1); effects_adjust_speed(default=0.8,min=0,max=1); effects_adjust_range(default=0.13,min=0,max=1)
高速彩光 | 49475327 | 7343527966145516042 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=0.65,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1)
鱼眼 II | 1418072 | 7023664868083372580 | true | effects_adjust_speed(default=0,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_distortion(default=0.8,min=0,max=1)
鱼眼 III | 1521356 | 7051881765975101983 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1); effects_adjust_intensity(default=0,min=0,max=1); effects_adjust_distortion(default=1,min=0,max=1); effects_adjust_range(default=0.3,min=0,max=1)
鱼眼 IV | 1790048 | 7091597643553444359 | true | effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_texture(default=0.55,min=0,max=1)
鱼眼星星 | 88503775 | 7432187089862529546 | true | effects_adjust_speed(default=0.333,min=0,max=1)
鱼眼涂鸦 | 98675391 | 7453001309596160522 | true | effects_adjust_speed(default=0.333,min=0,max=1)
鱼眼闪电 | 88503776 | 7432187089858351667 | true | effects_adjust_speed(default=0.333,min=0,max=1)
黑白胶片 | 1691558 | 7085992144627831326 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
```


---

## 附录 H 视频人物特效（240 条）

- 挂载位置：materials.video_effects[type=face_effect]
- 草稿实际使用编号：effect_id + resource_id
- 免费 159 条，VIP 81 条
```text
name | effect_id | resource_id | is_vip | params
BOOM！ | 1378605 | 6999560597230588429 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
X | 1464226 | 7037006820749087246 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
crash！ | 1378609 | 6999887184018805285 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
中刀 | 1436386 | 7029514054179754510 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
主体冲破屏幕 | 74731169 | 7390265515056304681 | false | -
九尾狐 | 1404740 | 7011416501160776228 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
人影爆闪 | 19799492 | 7260741462269104697 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_luminance(default=0.45,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1)
光环 I | 1378551 | 6999584193848021535 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
光环 II | 1378552 | 6999882629893853726 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
几何拖尾 I | 1404702 | 6985081270208303653 | false | -
几何拖尾 II | 1404705 | 7008079206181507615 | false | -
击中 | 1404729 | 7008009586581967397 | false | effects_adjust_color(default=1,min=0,max=1)
分头行动 | 1570064 | 7065570293552517646 | false | effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.4,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
分身 | 9010351 | 7194734735434715704 | false | effects_adjust_distortion(default=0.2,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_number(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1)
动感爱心 | 1238121 | 6998039666024780318 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
卡通脸 | 10092161 | 7205481536240489019 | false | -
变身 | 1238120 | 6998018272557797924 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
可爱女生 | 1182270 | 6971317732948054542 | false | effects_adjust_size(default=0,min=0,max=1)
可爱猪 | 1182274 | 6971317650219602446 | false | effects_adjust_size(default=0,min=0,max=1)
吻痕坏笑 | 9392743 | 7197741530751177274 | false | effects_adjust_texture(default=1,min=0,max=1)
哈哈哈 | 1217040 | 6993187958685700638 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
图腾 | 1378608 | 6999820560528052743 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
圣诞小熊 | 7126277 | 7175084803874624061 | false | effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
圣诞帽 | 1457102 | 7034784053609894430 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.3,min=0,max=1)
圣诞树 | 6993587 | 7173942106061279781 | false | -
圣诞胡子 | 1457484 | 7034831862597947918 | false | effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_vertical_shift(default=0.77,min=0,max=1)
圣诞辣妹 | 7406471 | 7165705324777705992 | false | effects_adjust_texture(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
圣诞铃铛 | 7126337 | 7175084694940160568 | false | effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
声波 | 1404731 | 7008055446397260319 | false | effects_adjust_color(default=1,min=0,max=1)
多屏圣诞树 | 7126387 | 7175084576950194725 | false | effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
大头 | 1201644 | 6986556887818834462 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
大眼睛 | 1489516 | 7044080818544710152 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
天使环 | 1400400 | 7019228748775952933 | false | -
太阳神 | 1404735 | 7009186849444860453 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
好吃 | 1626122 | 7075218981442818596 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1.2); effects_adjust_horizontal_shift(default=0.6,min=0.3,max=2.6); effects_adjust_size(default=0.5,min=0.3,max=2); sticker(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
妖气 | 1558942 | 6729410038047183364 | false | effects_adjust_intensity(default=0.5,min=0,max=1)
委屈丑丑脸 | 4192363 | 7130874026733343268 | false | -
害羞 | 1187976 | 6979931248890221069 | false | effects_adjust_background_animation(default=1,min=0,max=1); sticker(default=1,min=0,max=1)
小恶魔 | 1225626 | 6995534946311868958 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1)
小鹿角 | 1459882 | 7035938555683672612 | false | -
尴尬住了 | 5481035 | 7156141357008949790 | false | -
局部扭曲 | 1470210 | 7038521452668129822 | false | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
局部马赛克 | 1454112 | 7034092576726585869 | false | effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
巴哥犬 | 1182273 | 6971317662567633421 | false | effects_adjust_size(default=0,min=0,max=1)
帅气男生 | 1182269 | 6971317748542476814 | false | effects_adjust_size(default=0,min=0,max=1)
幻影 I | 11357751 | 7212904257043829307 | false | effects_adjust_speed(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
幽灵 | 1378554 | 7000630410275197470 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
弥散流光 | 1455764 | 7034508334157795876 | false | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0,min=0,max=1)
彩色负片 | 1459050 | 7035876641083494926 | false | effects_adjust_size(default=0.4,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
彩色重影 | 1235614 | 6995746173772370469 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
微笑摇摆头 | 6253239 | 7166825483902915109 | false | effects_adjust_size(default=0.45,min=0,max=1); effects_adjust_speed(default=0.75,min=0,max=1); effects_adjust_range(default=0.35,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
心动 | 1204190 | 6986186073814602277 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.75,min=0,max=1)
心动信号 | 1478394 | 7040012457842053662 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
心心眼 | 9126233 | 7196943722523660858 | false | effects_adjust_distortion(default=1,min=0,max=1)
恶灵骑士 | 1378618 | 7000301210993431053 | false | effects_adjust_size(default=1,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
恶魔印记 | 1378619 | 7000647554337608222 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
恶魔尾巴 | 1404725 | 7001021232371995149 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_vertical_shift(default=1,min=0,max=1)
恶魔角 | 1400399 | 7019228817549955597 | false | -
惨 | 1225625 | 6992836065245532680 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1)
意识流 | 1378555 | 7000629338529862151 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.6,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
憔悴 | 1197947 | 6986160256103485989 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0.75,min=0,max=1)
懵 | 1187977 | 6980272649066779143 | false | effects_adjust_background_animation(default=1,min=0,max=1); sticker(default=1,min=0,max=1)
我不听 | 1353102 | 7001058741571293709 | false | effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
我服了 | 1436336 | 7029509874862002724 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1)
手印涂抹 | 5190085 | 7153950763348136478 | false | effects_adjust_intensity(default=1,min=0,max=1)
手绘描边 | 80106342 | 7406177019404227109 | false | -
打击 | 1169502 | 6971302911317905956 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.55,min=0,max=1)
打脸 | 1217039 | 6992915114051506725 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
扫描 II | 1378580 | 7000630959565443614 | false | effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
拼贴抽帧 | 4574525 | 7142777693707178533 | false | effects_adjust_vertical_chromatic(default=0,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.1,min=0,max=1); effects_adjust_size(default=0.3,min=0,max=1); effects_adjust_texture(default=0.661,min=0,max=1); effects_adjust_filter(default=0.65,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
拼贴风暴 | 1464400 | 7037019101402763806 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.75,min=0,max=1)
拽酷红眼 | 1185226 | 6979861988935471623 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1)
掉小珍珠啦 | 4080159 | 7132336135748981255 | false | -
故障描边 I | 1238132 | 6998080413587477005 | false | effects_adjust_speed(default=0.33,min=0,max=1)
敲打 | 1197949 | 6986918523704447501 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
新年星黛露 | 7823781 | 7182406780733887033 | false | effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
无信号 | 1478054 | 7039965830192304671 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
日系大头贴 | 32668223 | 7309039877796925978 | false | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_texture(default=0.8,min=0,max=1); effects_adjust_blur(default=0.1,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1); sticker(default=1,min=0,max=1)
星光放射 | 1378610 | 6999904379822150158 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
星星拖尾 | 1404703 | 7007679689388986888 | false | -
未来眼镜 | 1238126 | 6989160247034122789 | false | effects_adjust_color(default=1,min=0,max=1)
机械几何 | 1238116 | 6997682380454498824 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
机械姬 I | 1238098 | 6978809529215488548 | false | -
机械姬 II | 1238099 | 6997969810822795813 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
机灵怪 | 5510681 | 7158373218724614664 | false | -
欧美女性 | 1182266 | 6971317800098861576 | false | effects_adjust_size(default=0,min=0,max=1)
欧美男性 | 1182267 | 6971317784085008909 | false | effects_adjust_size(default=0,min=0,max=1)
气泡 I | 1378604 | 6999560743653741087 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
气泡 II | 1378603 | 6999560859986956813 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
气波 | 1404693 | 7008459080452805133 | false | effects_adjust_color(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
氛围大头贴 | 32919263 | 7309480138486321715 | false | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_texture(default=0.8,min=0,max=1); effects_adjust_blur(default=0.1,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1); sticker(default=1,min=0,max=1)
沉沦 | 1378579 | 7000286535568331294 | false | effects_adjust_range(default=1,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
流光描边 | 6699941 | 7156203771352060424 | false | effects_adjust_intensity(default=0.85,min=0,max=1); effects_adjust_size(default=0.15,min=0,max=1); effects_adjust_range(default=0.33,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=0.25,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
流口水 | 1610044 | 7072912940101276196 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.5,min=0.4,max=0.7); effects_adjust_size(default=0.8,min=0.5,max=1.2)
漩涡 | 1404726 | 7007639691797205511 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
潮流入侵 | 1475552 | 7039588403897176583 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
潮酷女孩 | 1182282 | 6973998028587799076 | false | effects_adjust_size(default=0,min=0,max=1)
潮酷男孩 | 1182268 | 6971317770835202574 | false | effects_adjust_size(default=0,min=0,max=1)
激光几何 | 1238146 | 6998130105188880909 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
火焰拖尾 | 1404704 | 7008060347789611551 | false | -
火焰环绕 | 1404737 | 7009186695157387784 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
火焰翅膀 I | 1404738 | 7009186539762618910 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
火焰翅膀 II | 1404728 | 7007998245511107108 | false | effects_adjust_color(default=1,min=0,max=1)
灵机一动 | 1187978 | 6982806720867209765 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_background_animation(default=0.6,min=0,max=1); sticker(default=1,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
灵魂出走 | 1220234 | 6994263736991093278 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.6,min=0,max=1); sticker(default=1,min=0,max=1)
爱心光波 | 1552114 | 7058944699737838116 | false | effects_adjust_texture(default=0.204,min=0,max=1); effects_adjust_size(default=0.753,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
爱心焰火 | 1378601 | 6999550440639566350 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
狼人 | 5413619 | 7156899280374993416 | false | effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1)
猩猩脸 | 3186064 | 7112786295771894285 | false | -
猫耳女孩 | 1182272 | 6971317673699316261 | false | effects_adjust_size(default=0,min=0,max=1)
电光描边 | 6738041 | 7171723380003967496 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_range(default=0.9,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
电光放射 | 1404739 | 7011414375130993188 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
电击 | 1378602 | 6999560974638256671 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
电子屏故障 | 1238119 | 6997976386413531661 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
真的会谢 | 7600931 | 7179493200904589881 | false | -
真香 | 1225627 | 6995535089975169549 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1)
破碎的心 | 1404734 | 7008077860397126158 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
神明少女 | 1169466 | 6906817277316829703 | false | effects_adjust_soft(default=0.25,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
科技氛围 I | 1238115 | 6989160173826740767 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
科技氛围 III | 1238118 | 6983927792010269214 | false | effects_adjust_speed(default=0.33,min=0,max=1)
秘密 | 1418782 | 7023684632591733284 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
箭头环绕 | 1378553 | 6999943971162034702 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
粉色便便 | 1182271 | 6971317685216875044 | false | effects_adjust_size(default=0,min=0,max=1)
背景拖影 | 1379270 | 7012512877038801415 | false | effects_adjust_horizontal_shift(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.85,min=0,max=1)
背景氛围II | 1404727 | 7007713075486790152 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
脸红 | 1424210 | 7025808257306333732 | false | sticker(default=1,min=0,max=1); effects_adjust_background_animation(default=0.802,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
脸绿了 | 1418056 | 7023661644853023263 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.802,min=0,max=1)
脸部故障 | 19351944 | 7260774105073324602 | false | effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_color(default=0.6,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
舞者 | 1238134 | 6978809631678140935 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
舞者 II | 1378611 | 7000629698401145352 | false | effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.6,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
萤火 | 1378556 | 6979415063106949639 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
虚拟人生 I | 1238100 | 6998017546452472351 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
虚拟人生 II | 1238101 | 6998017726589440519 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
衰 | 1225628 | 6995855600764588557 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1)
视线遮挡 | 1455754 | 7034507846305714696 | false | effects_adjust_speed(default=0,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
赛博朋克 I | 1238114 | 6975112087659876895 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
赛博朋克 II | 1238113 | 6997261680803582494 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
赛博眼镜 | 1536126 | 7055586958050857503 | false | -
轻金属 | 1463702 | 7036946127320519182 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.75,min=0,max=1)
运动轨迹 | 74470467 | 7389547512987652658 | false | effects_adjust_number(default=0.4,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
迷茫 | 1185225 | 6979931594408595975 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
闪影 | 1825212 | 7090458377901314568 | false | effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
闪烁 | 1404733 | 7008060861528936991 | false | effects_adjust_color(default=1,min=0,max=1)
闪电炸裂 | 1378606 | 6999539022812942884 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
阳光 | 1197948 | 6986176759725036039 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.75,min=0,max=1)
阴云密布 | 1427592 | 7025527915320185375 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
阴暗面 | 1378620 | 7000679723906896397 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
难吃 | 1627088 | 7075326356585714207 | false | effects_adjust_vertical_shift(default=0.5,min=0,max=1.2); effects_adjust_horizontal_shift(default=0.55,min=0.3,max=2.6); effects_adjust_size(default=0.5,min=0.3,max=2); sticker(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
难过 | 1187975 | 6979931396827517477 | false | effects_adjust_background_animation(default=1,min=0,max=1); sticker(default=1,min=0,max=1)
雪花眼泪 | 7078531 | 7174694873897898553 | false | effects_adjust_intensity(default=0.85,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_speed(default=0.2,min=0,max=1); effects_adjust_sharpen(default=0.25,min=0,max=1)
霓虹特技 | 74469969 | 7389546043534217778 | false | effects_adjust_size(default=0.51,min=0,max=1); effects_adjust_horizontal_chromatic(default=0,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1)
音符拖尾 | 1404706 | 7008458769675850248 | false | -
音符拖尾 II | 1238188 | 7002176395312894494 | false | -
飓风 | 1404694 | 7008458952451035678 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
飞翔的帽子 | 1404708 | 6999892125697446414 | false | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
鬼火 | 1404696 | 7008470453366821389 | false | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
黑人女孩 | 1182265 | 6971317836648026661 | false | effects_adjust_size(default=0,min=0,max=1)
黑人男生 | 1182264 | 6971317847318336031 | false | effects_adjust_size(default=0,min=0,max=1)
鼻血 | 5182539 | 7153900212623249950 | false | effects_adjust_intensity(default=1,min=0,max=1)
3D兔兔 | 1924176 | 7098954198204551716 | true | sticker(default=1,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
Love u | 1551894 | 7058892012358996510 | true | effects_adjust_filter(default=0.8,min=0,max=1); effects_adjust_size(default=0.8,min=0,max=1); effects_adjust_color(default=0.3,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1)
X瞬移 | 20387617 | 7265629618424517157 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1)
分身 III | 23497249 | 7281245666309837349 | true | effects_adjust_speed(default=0.3,min=0,max=0.6); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
分身ll | 10287363 | 7207269616299545149 | true | effects_adjust_vertical_shift(default=0.3,min=0,max=1); effects_adjust_size(default=0.62,min=0,max=1); effects_adjust_range(default=0.4,min=0,max=1); effects_adjust_speed(default=0.55,min=0,max=1); effects_adjust_horizontal_shift(default=0.3,min=0,max=1)
发光分身 | 13661053 | 7233250530292666939 | true | effects_adjust_color(default=0.84,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_horizontal_shift(default=0.35,min=0,max=1); effects_adjust_size(default=0.102,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1)
变老-美颜 | 12825757 | 7226689898118386237 | true | -
可爱龙龙 | 41751981 | 7327508217590714931 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
吸血鬼 | 5226581 | 7154356694376518158 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_texture(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
哥特 | 5199947 | 7154061273838129672 | true | effects_adjust_filter(default=0.6,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1)
嘻哈眼镜 | 1238128 | 6998017895024300557 | true | effects_adjust_color(default=1,min=0,max=1); effects_adjust_vertical_shift(default=0.6,min=0,max=1)
天使 | 5374123 | 7156481333189939720 | true | effects_adjust_texture(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.9,min=0,max=1)
天使翅膀 | 1378600 | 6999514637767021070 | true | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
奇行种 | 6432361 | 7168749461206733342 | true | -
局部模糊 | 1461580 | 7036282000780562981 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_noise(default=1,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.75,min=0,max=1); effects_adjust_vertical_chromatic(default=0.75,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1)
幻彩流光 | 30319544 | 7303422113812058633 | true | effects_adjust_texture(default=0.8,min=0,max=1); effects_adjust_luminance(default=0.2,min=0,max=1); effects_adjust_intensity(default=0.95,min=0,max=1); effects_adjust_color(default=0.2,min=0,max=1)
幻影平移 | 19114588 | 7259667629357404730 | true | effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1)
彩虹流体 | 21883974 | 7273753115604554295 | true | effects_adjust_distortion(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_luminance(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=0.9,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
彩虹边缘 | 31771661 | 7306769922535723558 | true | effects_adjust_intensity(default=0.55,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_size(default=0.6,min=0,max=1); effects_adjust_rotate(default=1,min=0,max=1); effects_adjust_luminance(default=0.15,min=0,max=1)
影分身 | 31622417 | 7306822259186864691 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_luminance(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
恶魔之翼 | 1404730 | 7008049313305596446 | true | effects_adjust_color(default=1,min=0,max=1)
情绪定格 | 28662656 | 7298250619167445531 | true | effects_adjust_intensity(default=0.6,min=0,max=1); effects_adjust_range(default=0.6,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=0.1,min=0,max=1)
我太可爱了 | 4104909 | 7132773677086544398 | true | -
我爱了 | 9267743 | 7182098630935843385 | true | -
我麻了 | 1441766 | 7030722591358718494 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
手写描边 | 2869818 | 7108559446065811998 | true | effects_adjust_color(default=0.2,min=0,max=1); effects_adjust_size(default=0.21,min=0,max=1); effects_adjust_vertical_shift(default=0.2,min=0,max=1); effects_adjust_horizontal_shift(default=0.8,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
捕梦 | 1471454 | 7038866261677183524 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
撕纸拼贴 | 80787899 | 7406207253583237682 | true | -
旋转分身 | 19114658 | 7259667753731101244 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_range(default=0.3,min=0,max=0.75); effects_adjust_blur(default=0.4,min=0,max=1); effects_adjust_background_animation(default=0.5,min=0,max=1); effects_adjust_size(default=1,min=0,max=1); effects_adjust_number(default=1,min=0,max=1)
无限穿越 | 27074734 | 7293870099738399269 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_number(default=0,min=0,max=1)
有事吗？ | 39451195 | 7322382230930592266 | true | effects_adjust_texture(default=0.8,min=0,max=1); effects_adjust_background_animation(default=0.6,min=0,max=1)
机械环绕 I | 1238184 | 6986465789259813406 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
机械环绕 II | 1238185 | 6997731822104744478 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
梦境 | 1478040 | 7039963252612141598 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
气炸了 | 1426832 | 7026548629498237454 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
波点分身 | 1826180 | 7086779590768595469 | true | effects_adjust_color(default=0.6,min=0,max=1); effects_adjust_intensity(default=0.25,min=0,max=1); effects_adjust_range(default=0,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
流体故障 | 24949284 | 7287114240089920061 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.8,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1)
涂鸦鬼影 | 5185037 | 7153917024723276325 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
漩涡溶解 | 9583557 | 7201020527501120057 | true | effects_adjust_distortion(default=0.45,min=0,max=1); effects_adjust_speed(default=0.45,min=0,max=1); effects_adjust_horizontal_shift(default=0.45,min=0,max=1); effects_adjust_vertical_shift(default=0.25,min=0,max=1); effects_adjust_size(default=0.45,min=0,max=1); effects_adjust_range(default=0.45,min=0,max=1)
火焰图腾 | 1404736 | 7009186785662079524 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
点赞 | 1609620 | 7072663671096218143 | true | effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=0.25,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1)
热力光谱 I | 1451182 | 7033284501253919268 | true | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1)
热力光谱 II | 1451606 | 7033338062113346056 | true | effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=0.801,min=0,max=1)
焰火 | 1404695 | 7008459945590919716 | true | effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
熬夜冠军 | 43238686 | 7330555999801053746 | true | effects_adjust_texture(default=0.8,min=0,max=1)
爱心 | 1587990 | 7068191600148484638 | true | effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
爱心发射 | 1551876 | 7057403623004705294 | true | effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_color(default=0,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.35,min=0,max=1)
爱心泡泡 | 1551930 | 7055592805174874632 | true | effects_adjust_size(default=0.35,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
爱心眼 | 2491250 | 7104647986176594463 | true | effects_adjust_color(default=0.15,min=0,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_range(default=0.05,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1)
爱心美瞳 | 8950197 | 7194734371872444965 | true | effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
狱火 | 1404692 | 7007676026406834725 | true | effects_adjust_color(default=1,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1)
生气 | 1588764 | 7068227476035473928 | true | effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
电光描边 II | 20444547 | 7265989852099777061 | true | effects_adjust_luminance(default=0.75,min=0,max=1); effects_adjust_distortion(default=0.65,min=0,max=1); effects_adjust_size(default=0.75,min=0,max=1); effects_adjust_color(default=0.11,min=0,max=1); effects_adjust_range(default=0.2,min=0,max=1); effects_adjust_speed(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1)
电光灼烧 | 19106834 | 7259649795571061305 | true | effects_adjust_rotate(default=0.73,min=0,max=1); effects_adjust_color(default=0.8,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_distortion(default=0.3,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1)
电光眼 | 2724384 | 7106778883143242271 | true | effects_adjust_color(default=0.25,min=0,max=1); effects_adjust_range(default=1,min=0,max=1); effects_adjust_intensity(default=0.25,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1)
电光耳机 | 1238127 | 6998018067154342408 | true | effects_adjust_color(default=1,min=0,max=1)
眼神光 | 1793042 | 7091874262364983815 | true | effects_adjust_intensity(default=0.75,min=0,max=1); effects_adjust_range(default=0.85,min=0,max=1); effects_adjust_color(default=0,min=0,max=1)
瞬移 | 39618119 | 7322735107280736805 | true | effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_speed(default=0.6,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.7,min=0,max=1)
碎片分身 | 10339835 | 7207691092655870523 | true | effects_adjust_range(default=0.1,min=0,max=1); effects_adjust_intensity(default=0.95,min=0,max=1); effects_adjust_speed(default=0,min=0,max=1)
碎闪边缘 | 31771693 | 7306471467397419547 | true | effects_adjust_range(default=0.5,min=0,max=1); effects_adjust_background_animation(default=0.8,min=0,max=1); effects_adjust_size(default=0.2,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_luminance(default=0.15,min=0,max=1)
科技氛围 II | 1238117 | 6982572496356643359 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
移形回位 | 21811668 | 7270801008094089784 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_luminance(default=0.3,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
移形幻影 I | 9583559 | 7201010922742092325 | true | effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_blur(default=1,min=0,max=1); effects_adjust_speed(default=1,min=0,max=1)
移形幻影 II | 9010339 | 7194734891353772603 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.5,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1)
空气流体 | 24123133 | 7283548311217246781 | true | effects_adjust_intensity(default=0.7,min=0,max=1); effects_adjust_speed(default=0.4,min=0,max=1); effects_adjust_horizontal_chromatic(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.72,min=0,max=1); effects_adjust_size(default=0.66,min=0,max=1)
笑哭 | 1606772 | 7072173200418804231 | true | effects_adjust_horizontal_shift(default=0.5,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0,min=0,max=1); effects_adjust_filter(default=0.25,min=0,max=1); effects_adjust_speed(default=0.3,min=0,max=1)
粒子弥散 | 23970537 | 7283038170826936892 | true | effects_adjust_horizontal_shift(default=0.66,min=0,max=1); effects_adjust_speed(default=0.33,min=0,max=1)
美味召唤 | 1612792 | 7073398095186235935 | true | effects_adjust_vertical_shift(default=0.6,min=0,max=1.2); effects_adjust_size(default=0.5,min=0,max=1); sticker(default=1,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
蝴蝶翅膀 | 1378607 | 6999567409677865486 | true | effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
轮廓扫描 | 19351962 | 7260773990178755129 | true | effects_adjust_color(default=0.6,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_rotate(default=0,min=0,max=1); effects_adjust_soft(default=0.5,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1)
迷幻分身 | 23303207 | 7280421849974968889 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_number(default=0.5,min=0,max=1); effects_adjust_blur(default=0.5,min=0,max=1); effects_adjust_rotate(default=0.7,min=0,max=1); effects_adjust_luminance(default=0.7,min=0,max=1); effects_adjust_intensity(default=0.9,min=0,max=1); effects_adjust_size(default=0.85,min=0,max=1)
金币掉落 | 1543838 | 7021362776404660743 | true | effects_adjust_speed(default=0.333,min=0,max=1); effects_adjust_background_animation(default=1,min=0,max=1)
镭射眼 I | 2724386 | 7106778448344912421 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=0.9,min=0,max=1); effects_adjust_speed(default=0.5,min=0,max=1)
镭射眼 II | 2724385 | 7106778621326397983 | true | effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_color(default=0.62,min=0,max=1)
闪光放大 | 33838202 | 7304912977180758537 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_intensity(default=0.5,min=0,max=1); effects_adjust_luminance(default=0.6,min=0,max=1); effects_adjust_distortion(default=0.7,min=0,max=1)
闪电 | 1711412 | 7088198349324554766 | true | effects_adjust_color(default=0,min=0,max=1); effects_adjust_speed(default=0.1,min=0,max=1); effects_adjust_intensity(default=1,min=0,max=1); effects_adjust_filter(default=0.7,min=0,max=1)
闪电环绕 | 1238186 | 6998102186068546078 | true | effects_adjust_speed(default=0.33,min=0,max=1); effects_adjust_vertical_shift(default=0.5,min=0,max=1); effects_adjust_size(default=0.5,min=0,max=1); effects_adjust_color(default=1,min=0,max=1)
闪电眼 | 2722184 | 7106763566262260231 | true | effects_adjust_color(default=0.25,min=0,max=1); effects_adjust_luminance(default=0.25,min=0,max=1); effects_adjust_filter(default=1,min=0,max=1); effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_range(default=0.85,min=0,max=1)
霓虹爱心 | 9221893 | 7194734553288675895 | true | effects_adjust_speed(default=0.5,min=0,max=1); effects_adjust_filter(default=0.5,min=0,max=1)
高光人物 | 80107647 | 7406179353362436645 | true | -
黑色眼泪 | 5208347 | 7154231632604434981 | true | effects_adjust_intensity(default=0.8,min=0,max=1); effects_adjust_filter(default=0.8,min=0,max=1)
```


---

## 附录 I 音频场景音（85 条）

- 挂载位置：materials.audio_effects[type=audio_effect]
- 草稿实际主要使用编号：resource_id
- 仓库元数据里也有 effect_id，但导出草稿时主要落 resource_id + audio_adjust_params
- 免费 12 条，VIP 73 条
```text
name | effect_id | resource_id | is_vip | params
8bit | 5723961 | 7161319747584266766 | false | change_voice_param_pitch_shift(default=0.5,min=0,max=1); change_voice_param_timbre(default=1,min=0,max=1); change_voice_param_strength(default=1,min=0,max=1)
低保真 | 2672762 | 7024390914537689614 | false | 强弱(default=1,min=0,max=1)
合成器 | 2672753 | 7018011500577034759 | false | 强弱(default=1,min=0,max=1)
回音 | 5723901 | 7018011608408396325 | false | change_voice_param_quantity(default=0.8,min=0,max=1); change_voice_param_strength(default=0.762,min=0,max=1)
扩音器 | 2672749 | 7018011975514853924 | false | 强弱(default=1,min=0,max=1)
水下 | 2673077 | 7106404450444513806 | false | 深度(default=0.5,min=0,max=1)
没电了 | 2672747 | 7018012193769656845 | false | 强弱(default=1,min=0,max=1)
环绕音 | 5723960 | 7161319847819743780 | false | change_voice_param_center_position(default=0.5,min=0,max=1); change_voice_param_surrounding_frequency(default=0.5,min=0,max=1)
电音 | 2672754 | 7018011438379700773 | false | 强弱(default=1,min=0,max=1)
颤音 | 2672755 | 7018011370289369637 | false | 频率(default=0.714,min=0,max=1); 幅度(default=0.905,min=0,max=1)
麦霸 | 2672748 | 7018012141332468260 | false | 空间大小(default=0.052,min=0,max=1); 强弱(default=0.45,min=0,max=1)
黑胶 | 2672761 | 7024391411764040205 | false | 强弱(default=1,min=0,max=1); 噪点(default=0.743,min=0,max=1)
360度环绕音 | 81298963 | 7410254975328064040 | true | strength(default=1,min=0,max=1)
3d环绕音 | 53187169 | 7350214888242811455 | true | 强度(default=0,min=0,max=1)
Autotune | 58979352 | 7360900806851170828 | true | 强度(default=1,min=0,max=1)
Livehouse | 82364386 | 7413661671941476904 | true | 强度(default=1,min=0,max=1)
下雨 | 68076030 | 7375069649446113804 | true | strength(default=1,min=0,max=1); noise(default=0.743,min=0,max=1)
乡村大喇叭 | 23897651 | 7282691036197950009 | true | 强度(default=1,min=0,max=1)
人声增强 | 2673078 | 7106404399756349983 | true | 强弱(default=1,min=0,max=1)
人声增强3 | 86419033 | 7425556785693463090 | true | 强度(default=1,min=0,max=1)
低保真扩音器 | 103845136 | 7467815819540435506 | true | 强度(default=1,min=0,max=1)
低音增强 | 2673080 | 7106404304247853604 | true | change_voice_param_strength(default=1,min=0,max=1)
低音增强2 | 81298965 | 7410254814539420195 | true | strength(default=1,min=0,max=1)
停车场 | 66413024 | 7372150242524795446 | true | strength(default=1,min=0,max=1)
冥想 | 103845143 | 7467815749931766322 | true | 强度(default=1,min=0,max=1)
冰川之下 | 68076029 | 7375068986829967883 | true | strength(default=1,min=0,max=1); noise(default=0.743,min=0,max=1)
刮风 | 68076028 | 7375069247275274771 | true | strength(default=1,min=0,max=1); noise(default=0.743,min=0,max=1)
午夜电台 | 88155751 | 7431088998652580378 | true | 强度(default=1,min=0,max=1)
噪音混响 | 72110975 | 7382844688987853349 | true | strength(default=1,min=0,max=1)
回声 | 86419034 | 7425556970339308083 | true | 强度(default=1,min=0,max=1)
回忆人声 | 78208789 | 7400653027557773865 | true | strength(default=1,min=0,max=1)
地狱 | 68076027 | 7375069113988682281 | true | strength(default=1,min=0,max=1); noise(default=0.743,min=0,max=1)
复古收音机 | 53187166 | 7350215379714576907 | true | 强度(default=1,min=0,max=1)
复古收音机2 | 88155750 | 7431088943560397339 | true | 强度(default=1,min=0,max=1)
复古电视 | 88155749 | 7431089082647712282 | true | 强度(default=1,min=0,max=1)
失真电子 | 53187167 | 7350215296801575443 | true | 强度(default=1,min=0,max=1)
宽阔人声 | 78208785 | 7400653260320674343 | true | strength(default=1,min=0,max=1)
对讲机 | 53187168 | 7350214704284832275 | true | 强度(default=1,min=0,max=1)
山洞 | 75411128 | 7392070412865114659 | true | strength(default=1,min=0,max=1)
广播 | 84093261 | 7418519152467382794 | true | 强度(default=1,min=0,max=1)
延迟回声 | 86419029 | 7425556912709571110 | true | 强度(default=1,min=0,max=1)
恐怖音效 | 88155748 | 7431088801579012645 | true | 强度(default=1,min=0,max=1); 背景音(default=0.5,min=0,max=1)
房间 | 23880629 | 7282691385872880165 | true | 强度(default=1,min=0,max=1)
捂嘴 | 66552320 | 7372405649684042292 | true | strength(default=1,min=0,max=1)
教堂 | 23882063 | 7282691146759803429 | true | 强度(default=1,min=0,max=1)
教室 | 23897703 | 7282687783833965113 | true | 强度(default=1,min=0,max=1)
时光扭曲 | 81298964 | 7410254477246075407 | true | strength(default=1,min=0,max=1)
森林 | 82210570 | 7413270049080742415 | true | 强度(default=1,min=0,max=1); 背景音(default=0.5,min=0,max=1)
楼道 | 81298960 | 7410254596020376064 | true | strength(default=1,min=0,max=1)
楼道回声 | 86419032 | 7425556847509115401 | true | 强度(default=1,min=0,max=1)
氦气 | 78208787 | 7400653188803596836 | true | strength(default=1,min=0,max=1)
沙漠 | 68076025 | 7375069515530375691 | true | strength(default=1,min=0,max=1); noise(default=0.743,min=0,max=1)
洞穴回声 | 86419031 | 7425557093597319689 | true | 强度(default=1,min=0,max=1)
派对 | 71718513 | 7381685442795541042 | true | strength(default=1,min=0,max=1); noise(default=0.743,min=0,max=1)
浴室 | 75411129 | 7392070514686038543 | true | strength(default=1,min=0,max=1)
深海回声 | 53187172 | 7350215168413929995 | true | 强度(default=1,min=0,max=1)
深邃人声 | 78208786 | 7400653111255110183 | true | strength(default=1,min=0,max=1)
清澈人声 | 81298967 | 7410254648440787456 | true | strength(default=1,min=0,max=1)
演唱会 | 82364387 | 7413661596611777076 | true | 强度(default=1,min=0,max=1)
演讲舞台 | 88155747 | 7431088715092464155 | true | 强度(default=1,min=0,max=1)
环绕回声 | 86419030 | 7425557028694659635 | true | 强度(default=1,min=0,max=1)
电台播音 | 84093262 | 7418519267659747877 | true | 强度(default=1,min=0,max=1)
电话 | 20255003 | 7264894634285863483 | true | 强弱(default=0.7,min=0,max=1)
留声机 | 23897797 | 7282687663872676408 | true | 强度(default=1,min=0,max=1)
百老汇 | 66413025 | 7372150379150053907 | true | strength(default=1,min=0,max=1)
空灵感 | 53187171 | 7350215092975178252 | true | 强度(default=1,min=0,max=1)
空谷回声 | 53187170 | 7350214991628210727 | true | 强度(default=1,min=0,max=1)
立体声 | 84093260 | 7418519209996456498 | true | 强度(default=1,min=0,max=1)
管道 | 81298962 | 7410254536234766863 | true | strength(default=1,min=0,max=1)
老式电话 | 23880011 | 7282691476843139621 | true | 强度(default=1,min=0,max=1)
蚊子变声 | 103845137 | 7467815685876355622 | true | 强度(default=1,min=0,max=1)
言灵术 | 72110974 | 7382844601435951653 | true | strength(default=1,min=0,max=1)
豪宅回声 | 58979353 | 7360900963294515775 | true | 强度(default=1,min=0,max=1)
超市广播 | 88155744 | 7431088660709118514 | true | 强度(default=1,min=0,max=1); 背景音(default=0.5,min=0,max=1)
超级混响 | 78208790 | 7400652941318689299 | true | strength(default=1,min=0,max=1)
超重低音 | 81298961 | 7410254867232461364 | true | strength(default=1,min=0,max=1)
迷幻 | 81298966 | 7410254415921156643 | true | 强度(default=1,min=0,max=1)
迷幻电子 | 68076026 | 7375069381769826879 | true | strength(default=1,min=0,max=1); noise(default=0.743,min=0,max=1)
闷响 | 82210571 | 7413269872307606016 | true | 强度(default=1,min=0,max=1)
震撼全景音 | 78208788 | 7400653333456753163 | true | strength(default=1,min=0,max=1)
音乐厅 | 79701150 | 7404798608395997723 | true | strength(default=1,min=0,max=1)
颤抖电音 | 103845138 | 7467815889602089523 | true | 强度(default=1,min=0,max=1)
马路边 | 82210569 | 7413269976628335119 | true | 强度(default=1,min=0,max=1); 背景音(default=0.5,min=0,max=1)
高解析人声 | 81298968 | 7410254695169528355 | true | strength(default=1,min=0,max=1)
高音增强 | 81298959 | 7410254923037676047 | true | strength(default=1,min=0,max=1)
```


---

## 附录 J 音色（57 条）

- 挂载位置：materials.audio_effects[type=audio_effect]
- 草稿实际主要使用编号：resource_id
- 免费 14 条，VIP 43 条
```text
name | effect_id | resource_id | is_vip | params
台湾小哥 | 18149602 | 7255565276819755576 | false | -
圣诞精灵 | 33214695 | 7310059412062736946 | false | -
圣诞老人 | 33214489 | 7310059178133819930 | false | -
广告男声 | 42060748 | 7328088579811316263 | false | -
港普男声 | 42060743 | 7328087687548637732 | false | -
老婆婆 | 42060746 | 7328089253114548799 | false | -
解说小帅 | 44254166 | 7332473259369173540 | false | -
大叔 | 2672760 | 7020344898033291790 | false | 音调(default=0.834,min=0,max=1); 音色(default=1,min=0,max=1)
女生 | 2672757 | 7020345715901600270 | false | 音调(default=0.834,min=0,max=1); 音色(default=0.334,min=0,max=1)
怪物 | 2672759 | 7020344978794615327 | false | 音调(default=0.65,min=0,max=1); 音色(default=0.78,min=0,max=1)
机器人 | 2672750 | 7018011705414259213 | false | 强弱(default=1,min=0,max=1)
男生 | 2672758 | 7020345085233467917 | false | 音调(default=0.375,min=0,max=1); 音色(default=0.25,min=0,max=1)
花栗鼠 | 2672752 | 7018011553081332231 | false | 音调(default=0.5,min=0,max=1); 音色(default=0.5,min=0,max=1)
萝莉 | 2672756 | 7020345789599715848 | false | 音调(default=0.75,min=0,max=1); 音色(default=0.6,min=0,max=1)
TVB女声 | 19186454 | 7260024060417937978 | true | -
东厂公公 | 42060742 | 7328092524612948491 | true | -
云龙哥 | 68856989 | 7376558114830553612 | true | -
侠客 | 42060738 | 7328089134331859468 | true | -
做作夹子音 | 63231108 | 7367676929496846911 | true | -
八戒 | 20427371 | 7265891792766112314 | true | -
军事解说 | 42060734 | 7328092289480266252 | true | -
动漫小新 | 58979441 | 7360901047662940708 | true | -
动漫海绵 | 63231109 | 7367676859883983379 | true | -
咆哮哥 | 44254278 | 7332473122605503039 | true | -
商务殷语 | 42060747 | 7328085477267870249 | true | -
四郎 | 16627073 | 7250403044414722621 | true | -
太白 | 42060736 | 7328091247308968484 | true | -
如来佛祖 | 68856990 | 7376558174049931830 | true | -
姜饼人 | 33214539 | 7310059267384414747 | true | -
容嬷嬷 | 44254320 | 7332472945366798860 | true | -
小孩 | 19716244 | 7262648951948448315 | true | -
强势妹 | 42060740 | 7328091624427229759 | true | -
快板 | 42060741 | 7328088454183522827 | true | -
恐怖电影 | 40932465 | 7325710953247412787 | true | -
悬疑解说 | 40932811 | 7325711304390349362 | true | -
懒小羊 | 44254304 | 7332473035116515859 | true | -
搞笑解说 | 19716150 | 7262648842238038584 | true | -
文艺女声 | 70562787 | 7379565719991620132 | true | -
樱桃丸子 | 40931609 | 7325709643332719113 | true | -
樱花小哥 | 42060735 | 7328091741678998055 | true | -
武则天 | 42060744 | 7328088300474864167 | true | -
沉稳解说 | 63231110 | 7367676791164506636 | true | -
温柔姐姐 | 70562785 | 7379565769190806079 | true | -
熊二 | 16627311 | 7250403222798471740 | true | -
猴哥 | 14477015 | 7236944659547689531 | true | -
甜美悦悦 | 40932253 | 7325710673978069530 | true | -
生活小妙招 | 42060737 | 7328092409525441065 | true | -
电竞解说 | 40933559 | 7325711893551649330 | true | -
电视广告 | 58979440 | 7360901109667336743 | true | -
紫薇 | 23475307 | 7281175506391667257 | true | -
舌尖解说 | 42060739 | 7328091500753982015 | true | -
蜡笔小妮 | 70562786 | 7379565670398169619 | true | -
语音助手 | 40931973 | 7325710335455793714 | true | -
那姐 | 64206631 | 7369177370873303587 | true | -
锤子哥 | 42060745 | 7328091348098093580 | true | -
顾姐 | 16627197 | 7250403134923608631 | true | -
黛玉 | 18149634 | 7255565592093004343 | true | -
```


---

## 附录 K 声音成曲（6 条）

- 挂载位置：materials.audio_effects[type=audio_effect]
- 草稿实际主要使用编号：resource_id
- 免费 2 条，VIP 4 条
```text
name | effect_id | resource_id | is_vip | params
Lofi | 17345060 | 7252917861948068410 | false | -
民谣 | 17046923 | 7251868698170888759 | false | -
嘻哈 | 17344948 | 7252918249036190245 | true | -
爵士 | 20120940 | 7264413578860433978 | true | -
节奏蓝调 | 17345046 | 7252918101958726200 | true | -
雷鬼 | 20120864 | 7264413386962637368 | true | -
```


---

## 附录 L 视频入场动画（155 条）

- 挂载位置：materials.material_animations[*].animations[*]
- 识别字段：type=in, material_type=video, panel=video
- 草稿实际使用编号：effect_id + resource_id
- 免费 38 条，VIP 117 条
```text
name | effect_id | resource_id | is_vip | default_duration_sec
Kira游动 | 34176967 | 7311984593387655731 | false | 2.267
上下抖动 | 431652 | 6739418390030455300 | false | 0.5
动感放大 | 431662 | 6740867832570974733 | false | 0.5
动感缩小 | 431658 | 6740868384637850120 | false | 0.5
向上滑动 | 624739 | 6798333487523828238 | false | 0.5
向上转入 | 645307 | 6808401616564130312 | false | 0.5
向上转入 II | 701961 | 6818747060649464327 | false | 0.5
向下滑动 | 624735 | 6798333705401143816 | false | 0.5
向下甩入 | 431638 | 6739338374441603598 | false | 0.5
向右上甩入 | 431644 | 6740122731418751495 | false | 0.5
向右下甩入 | 431640 | 6739395718223499787 | false | 0.5
向右滑动 | 624743 | 6798333076469453320 | false | 0.5
向右甩入 | 431636 | 6739338727866241539 | false | 0.5
向右转入 | 638825 | 6805019065761927694 | false | 0.5
向左上甩入 | 431648 | 6740122563692728844 | false | 0.5
向左下甩入 | 431642 | 6739395445346275853 | false | 0.5
向左滑动 | 624747 | 6798332871267324423 | false | 0.5
向左转入 | 699157 | 6816560956647150093 | false | 0.5
左右抖动 | 431654 | 6739418540421419524 | false | 0.5
抖动下降 | 1206320 | 6991764455931515422 | false | 0.5
折叠开幕 | 14506065 | 7239273897491698232 | false | 1.5
放大 | 624751 | 6798332733694153230 | false | 0.5
斜切 | 10696371 | 7210657307938525751 | false | 0.7
旋转 | 624731 | 6798334070653719054 | false | 0.5
旋转开幕 | 8295043 | 7186944542409495099 | false | 1
渐显 | 624705 | 6798320778182922760 | false | 0.5
漩涡旋转 | 703281 | 6782010677520241165 | false | 0.5
缩小 | 624755 | 6798332584276267527 | false | 0.5
翻入 | 98430529 | 7452407076417966619 | false | 1.17
跳转开幕 | 23185431 | 7279999334001676857 | false | 0.733
轻微抖动 | 431664 | 6739418227031413256 | false | 0.5
轻微抖动 II | 431650 | 6739418677910704651 | false | 0.5
轻微抖动 III | 503136 | 6781683302672634382 | false | 0.5
轻微放大 | 629085 | 6800268825611735559 | false | 0.5
钟摆 | 636115 | 6803260897117606414 | false | 0.5
镜像翻转 | 646003 | 6797338697625768455 | false | 0.5
雨刷 | 634681 | 6802871256849846791 | false | 0.5
雨刷 II | 640101 | 6805748897768542727 | false | 0.5
2024 | 33056565 | 7309774750677471794 | true | 1.5
2025 | 95801149 | 7446306216038371891 | true | 1.5
PASSION | 88544178 | 7432237078705869362 | true | 2
三屏下滑 | 90036560 | 7436273289170784818 | true | 1.83
三屏切闪 | 89308508 | 7434412782289687066 | true | 1.04
九宫格 | 90178902 | 7434746460186350090 | true | 2
交叉震动 | 12309329 | 7222990639984546360 | true | 0.833
交错开幕 | 23387955 | 7280797339042714169 | true | 1.1
侧滑 | 14524393 | 7239559299196785209 | true | 0.6
便利贴 | 70486392 | 7379456870265655859 | true | 0.9
冬季雪花 | 96136129 | 7447044440868262451 | true | 2
冰块 | 82268315 | 7413325383308677683 | true | 1.3
冰雪融化 | 96136131 | 7447044440868278794 | true | 2.92
冲撞 | 11320895 | 7215530662986519096 | true | 2
分屏横移 | 18746326 | 7257878167023522365 | true | 1
分屏组合 | 89406819 | 7434746460186366515 | true | 2.96
分屏翻转 | 18711457 | 7257782721575916088 | true | 0.7
分身模糊 | 89406818 | 7434746460186350131 | true | 1.5
划水 | 12811781 | 7226632607939695161 | true | 0.8
区域色块滑动 | 90036562 | 7436273288608748042 | true | 2
十字震动 | 54686020 | 7352824361625063987 | true | 0.8
卡片扫光 | 90546137 | 7437386424032186931 | true | 1.83
发光矩形 | 51093680 | 7346511208171704841 | true | 1.033
变速扩大 | 97484920 | 7450031573954466314 | true | 0.96
变速时空 | 90546138 | 7437386424036364850 | true | 1.21
向上滚动 | 34388476 | 7312341574988337690 | true | 1
向上闪入 | 21816946 | 7273389803532456504 | true | 0.7
向下甩动 | 47050546 | 7338320641306661410 | true | 1.4
四屏转换 | 48492378 | 7341283787143123507 | true | 1
圆形开幕 | 11680735 | 7218210014949806647 | true | 0.9
多层环形 | 42686363 | 7329444938960081460 | true | 2
多屏分割I | 89192703 | 7434055685572137509 | true | 1.42
多屏分割II | 89192705 | 7434055685572137499 | true | 1.83
多维空间 | 97260799 | 7449596462645645850 | true | 1.38
展开 | 12088589 | 7221413342257091133 | true | 0.5
幸运圣诞树 | 96136128 | 7447044441371578906 | true | 2
开辟2025 | 101958682 | 7461839463879021083 | true | 2
弹力分割 | 35994464 | 7267827357627454013 | true | 1.06
弹近 | 35289246 | 7314144465944318502 | true | 1.5
录像带分屏 | 90036561 | 7436273288600359474 | true | 2
心形放大 | 1487080 | 7042968847070007844 | true | 1.5
快速翻页 | 27878991 | 7296381392340914715 | true | 0.167
手写云朵 | 104144357 | 7468589903001948681 | true | 1.53
手机倒数 | 97032631 | 7448898555617497610 | true | 6.92
扫描 | 34385508 | 7312335732721324554 | true | 0.6
抖动变焦 | 5414507 | 7156911481563386381 | true | 0.8
抖动横移 | 20437845 | 7265946978792510010 | true | 0.567
报纸拼贴 | 97255882 | 7449589619034690074 | true | 1.5
报纸拼贴Ⅱ | 97255883 | 7449589619038884390 | true | 1.5
拉丝滑入 | 3179668 | 7112725640901562887 | true | 0.5
拼图 | 64963350 | 7369889381357720102 | true | 1.067
探灯聚焦 | 89895075 | 7435897594074649114 | true | 2
斜向拉丝 | 58777551 | 7360531434487943743 | true | 0.667
旋转圆球 | 70989966 | 7380298290140549647 | true | 0.8
时间倒计时 | 97032629 | 7448898555617481242 | true | 2
晃动抽帧 | 89895076 | 7435897594070438438 | true | 2.96
曝光放射 | 5529363 | 7158737452939612703 | true | 0.8
果冻 I | 6725401 | 7171640017574433294 | true | 0.8
果冻 II | 6732061 | 7171690870788329992 | true | 0.8
枫叶遮罩 | 90036564 | 7436273288612942363 | true | 2.3
模糊聚焦 | 46838778 | 7337937899704291866 | true | 1.2
横向模糊 | 29805902 | 7301896031673782835 | true | 0.5
水墨 | 39180627 | 7321672946466951731 | true | 2.433
水滴遮罩 | 93637608 | 7441475431309513267 | true | 1.96
油画描边变色 | 92053880 | 7439276108022813193 | true | 2
波纹弹动 | 50640360 | 7345731405663441460 | true | 1.2
流金 | 39438403 | 7322367212142989850 | true | 1.5
游蛇开幕 | 101962292 | 7461845576447955506 | true | 2
滑片滑动 | 96240861 | 7447351620641247781 | true | 1.4
灼烧出现 | 96136130 | 7447044441388356106 | true | 2.88
点开 | 90252347 | 7436667461837001267 | true | 1.3
烟雾弹 | 12815013 | 7226641244938572346 | true | 1.2
照片回忆 | 90036563 | 7436273289170784806 | true | 2
爱心碰撞 | 41910725 | 7327872475453198848 | true | 2.667
玫瑰 | 77061084 | 7397370569856913947 | true | 1.533
玻璃聚集 | 48072242 | 7340265236101861915 | true | 1.7
画出爱心 | 16211481 | 7248901535894082105 | true | 1.6
画面擦除 | 97032630 | 7448898555617481226 | true | 2
砸出波纹 | 18159482 | 7255594501694034490 | true | 1.56
神奇弹窗 | 103860744 | 7467842885740663306 | true | 0.5
空间扭曲 | 28693486 | 7298688232294715931 | true | 1.16
立体交叉 | 89406816 | 7434746460190544435 | true | 0.67
立体翻转 | 51089258 | 7346505124820292150 | true | 1.1
立方分体 | 78751449 | 7402167652220670514 | true | 1.8
竖向拼接 | 89308509 | 7434412782302269962 | true | 2.46
粒子爱心 | 104144327 | 7468589731727544882 | true | 3
翻书 | 98557334 | 7452662871550333477 | true | 1.6
翻卡 | 88299576 | 7431502518753956403 | true | 1
老电视 | 26091602 | 7290754106417746491 | true | 1.4
聚合 | 30391788 | 7303524763589153306 | true | 2
能量立方 | 58285135 | 7359472053998588425 | true | 1.333
脉冲 | 70764198 | 7379909514847326732 | true | 0.9
色散波纹 | 28824874 | 7299029942870741542 | true | 0.83
荧光爆闪 | 51992419 | 7347948517471556096 | true | 1
负片闪屏 | 89192704 | 7434055685576331785 | true | 1.5
转圈圈 | 15726741 | 7246643852411408952 | true | 0.8
迷幻流光 | 76511457 | 7395178910083715638 | true | 1.8
金沙 | 93472473 | 7441139821747114523 | true | 2
钱币遮罩 | 102049088 | 7461942207482696242 | true | 2
镜面组成 | 53224111 | 7350282290984915491 | true | 1.5
闪屏 | 14904085 | 7242155802209817147 | true | 1.2
闪现 | 10668047 | 7210363235906622012 | true | 0.44
闪电分屏 | 90546139 | 7437386424032170505 | true | 2
雪花遮罩 | 94174749 | 7442590758760092198 | true | 1.75
震动波纹 | 31806105 | 7307196313148330547 | true | 1.5
震撼倒数 | 95912088 | 7446622476928291365 | true | 3
震波 | 3297068 | 7115301367786246692 | true | 0.8
震波 II | 10744265 | 7211042099737662009 | true | 0.833
震波 III | 25545977 | 7288985830578721336 | true | 1.7
鞭炮遮罩 | 102019912 | 7461915994215158299 | true | 2
音量大小 | 102188589 | 7462226433700532745 | true | 2
飞近 | 76385331 | 7394717122653327910 | true | 1.6
马赛克 | 23885083 | 7282703408383922745 | true | 1
魔方 III | 88465764 | 7432135739745243686 | true | 1.1
魔法粒子I | 95912089 | 7446622476928291379 | true | 3
魔法粒子II | 95966017 | 7446673584296038949 | true | 3
黑白画中画 | 90036559 | 7436273288608764442 | true | 2
```


---

## 附录 M 视频出场动画（124 条）

- 挂载位置：materials.material_animations[*].animations[*]
- 识别字段：type=out, material_type=video, panel=video
- 草稿实际使用编号：effect_id + resource_id
- 免费 21 条，VIP 103 条
```text
name | effect_id | resource_id | is_vip | default_duration_sec
Kira游动 | 34389264 | 7312343337199997450 | false | 2.267
冰雪融化 | 96136047 | 7447044440864068122 | false | 2.83
向上滑动 | 624737 | 6798333612958683656 | false | 0.5
向上转出 | 701963 | 6818747115934585357 | false | 0.5
向上转出 II | 701965 | 6818747169017696781 | false | 0.5
向下滑动 | 624733 | 6798333787986989576 | false | 0.5
向右滑动 | 624741 | 6798333350487527950 | false | 0.5
向左滑动 | 624745 | 6798332972098392584 | false | 0.5
折叠闭幕 | 14506017 | 7239273967310082621 | false | 1.5
放大 | 624749 | 6798332801864176142 | false | 0.5
斜切 | 10697199 | 7210659943051956797 | false | 0.7
旋转 | 624729 | 6798334141323547143 | false | 0.5
旋转闭幕 | 1221132 | 6942482728335970823 | false | 1
渐隐 | 624707 | 6798320902548230669 | false | 0.5
漩涡旋转 | 634701 | 6778418947361346061 | false | 0.5
灼烧出现 | 96136048 | 7447044440859873801 | false | 2.96
缩小 | 624753 | 6798332648814023181 | false | 0.5
翻出 | 98425486 | 7452359860659687986 | false | 1.17
跳转闭幕 | 23302677 | 7280420767378969143 | false | 0.733
轻微放大 | 629083 | 6800268611807089166 | false | 0.5
镜像翻转 | 645999 | 6738353628215513613 | false | 0.5
2024 | 34158075 | 7311958876406944266 | true | 1
2025 | 95801179 | 7446306392748593714 | true | 1
PASSION | 88544141 | 7432237078710063643 | true | 1.5
三屏下滑 | 90036503 | 7436273288604553766 | true | 1.83
三屏切闪 | 89308379 | 7434412782293881395 | true | 1.04
九宫格 | 89406874 | 7434746460190544411 | true | 2
交叉震动 | 12330095 | 7223227564670587452 | true | 0.466
交错闭幕 | 23387942 | 7280797214186672701 | true | 1.1
侧滑 | 14524385 | 7239559574095663671 | true | 0.4
便利贴 | 70741835 | 7379884133268328996 | true | 0.8
冬季雪花 | 96136049 | 7447044440868262410 | true | 2
冰块 | 82396222 | 7413731112406487604 | true | 1.3
冲撞 | 11325221 | 7215555273501446716 | true | 0.767
分屏横移 | 18746674 | 7257879855063110205 | true | 0.88
分屏组合 | 89406873 | 7434746460186350117 | true | 2.96
分屏翻转 | 19063130 | 7259341241031070268 | true | 0.56
分身模糊 | 89406876 | 7434746460182155827 | true | 1.5
划水 | 12811717 | 7226632692354257445 | true | 0.8
区域色块滑动 | 90036504 | 7436273288604553755 | true | 2
十字震动 | 54685998 | 7352824282289803814 | true | 0.533
卡片扫光 | 90546052 | 7437386424036381211 | true | 1.83
发光矩形 | 51093596 | 7346510998771077659 | true | 1.133
变速扩大 | 97484974 | 7450031573958660617 | true | 1
变速时空 | 90546051 | 7437386424027976230 | true | 1.21
向上滚动 | 34388502 | 7312341715220697650 | true | 1
向上闪出 | 21816912 | 7273389599978689079 | true | 0.7
向下甩动 | 47191669 | 7338638617322983976 | true | 1
四屏转换 | 48492502 | 7341284613165158921 | true | 0.9
圆形闭幕 | 11680737 | 7218210114052821561 | true | 0.9
多层环形 | 42686393 | 7329445038604161536 | true | 1.633
多屏分割I | 89192583 | 7434055685572153907 | true | 1.46
多屏分割II | 89192581 | 7434055685572137482 | true | 2.04
多维空间 | 97260826 | 7449596462645662235 | true | 1.38
幕布 | 97077809 | 7448986761297924618 | true | 2
幸运圣诞树 | 96136050 | 7447044440868262450 | true | 2
弹力分割 | 49678364 | 7343902820808004123 | true | 1.06
弹远 | 35749432 | 7314925770181186075 | true | 1.2
录像带分屏 | 90036505 | 7436273288608748041 | true | 2
心形缩小 | 1463778 | 7034346969086562824 | true | 1
快速翻页 | 27895223 | 7296416099606729225 | true | 0.2
手写云朵 | 104144380 | 7468589970832232997 | true | 1.53
扫描 | 36871694 | 7316816362305753609 | true | 0.633
抖动变焦 | 5188733 | 7153942002696983047 | true | 0.5
抖动横移 | 20437843 | 7265946879060349477 | true | 0.4
折叠 | 12091673 | 7221420528148419133 | true | 0.3
报纸拼贴 | 97255862 | 7449589619038884389 | true | 1.5
报纸拼贴Ⅱ | 97255861 | 7449589619038884378 | true | 1.5
拉丝滑出 | 3240292 | 7114172789287817758 | true | 0.5
拼图 | 64963293 | 7369889275233440265 | true | 1.1
探灯聚焦 | 89895171 | 7435897594074632730 | true | 2
斜向拉丝 | 58777523 | 7360531353458184715 | true | 0.5
旋转圆球 | 71750513 | 7381753028732260916 | true | 0.8
晃动抽帧 | 89895170 | 7435897594078827035 | true | 2.96
曝光放射 | 5529791 | 7158753896624558628 | true | 0.5
枫叶遮罩 | 90036506 | 7436273288608748058 | true | 2.3
模糊聚焦 | 47267179 | 7338742568592609801 | true | 0.833
横向模糊 | 29824130 | 7301943351320777267 | true | 0.5
水墨 | 39326538 | 7322073757080621606 | true | 2.033
水滴遮罩 | 93637552 | 7441475431309513254 | true | 1.96
油画描边变色 | 92053923 | 7439276108022813235 | true | 2
波纹弹动 | 50691424 | 7345803511390540288 | true | 1.2
流金 | 39682247 | 7322857522648322586 | true | 1.133
滑片滑动 | 96240814 | 7447351620637037106 | true | 1.2
烟雾弹 | 13090999 | 7229149181762343484 | true | 0.9
照片回忆 | 90036502 | 7436273288612942386 | true | 2
爱心碰撞 | 42112174 | 7328249133079204352 | true | 2.3
玫瑰 | 77061996 | 7397378784028004891 | true | 1.4
玻璃爆开 | 51922869 | 7347865496508699170 | true | 0.733
画出爱心 | 16231427 | 7248951676420231735 | true | 1.1
画面擦除 | 97032678 | 7448898555617497626 | true | 2
砸出波纹 | 18161234 | 7255599483226952249 | true | 1.366
空间扭曲 | 28775864 | 7298918355841323529 | true | 0.93
立体交叉 | 89406875 | 7434746460190544394 | true | 0.67
立体翻转 | 53792520 | 7351333213068857892 | true | 1.1
立方合体 | 79925188 | 7405509410396574242 | true | 1.6
竖向拼接 | 89308380 | 7434412782285492773 | true | 2.46
粒子爱心 | 104144349 | 7468589804356112946 | true | 3
翻卡 | 88301520 | 7431509039437058586 | true | 1
老电视 | 24079477 | 7283429462924857914 | true | 1.6
能量立方 | 59265410 | 7361364150229930506 | true | 1.133
脉冲 | 70764127 | 7379909625870553654 | true | 0.8
色散波纹 | 31248281 | 7305961286762762790 | true | 0.767
荧光爆闪 | 52020801 | 7347994415576650255 | true | 0.8
负片闪屏 | 89192582 | 7434055685567943194 | true | 1.5
转圈圈 | 15754757 | 7246706359381529125 | true | 0.8
迷幻流光 | 76594275 | 7395482925006852647 | true | 1.5
金沙 | 93472419 | 7441139691694330378 | true | 2
钱币遮罩 | 102049160 | 7461942340328886835 | true | 2
镜面拆分 | 79917713 | 7405495700961628683 | true | 1.5
闪屏 | 15215961 | 7243999104114627132 | true | 0.833
闪现 | 8303609 | 7186978468087730749 | true | 0.25
闪电分屏 | 90546050 | 7437386424032170506 | true | 2
雪花遮罩 | 94174789 | 7442590863349256754 | true | 1.75
震动波纹 | 31806349 | 7307196476340310554 | true | 1.5
震波 III | 25555607 | 7289005562124046907 | true | 0.733
鞭炮遮罩 | 102029466 | 7461923788343480841 | true | 2
音量大小 | 102188408 | 7462226526260433418 | true | 2
飘散 | 31245441 | 7305957010518839846 | true | 2
飞远 | 76392667 | 7394730499492549158 | true | 1.6
马赛克 | 24073041 | 7283415427328250405 | true | 1
魔法粒子I | 95912176 | 7446622476928291378 | true | 3
魔法粒子II | 95966045 | 7446673724146717221 | true | 3
黑白画中画 | 90036501 | 7436273288612942374 | true | 2
```


---

## 附录 N 视频组合动画（123 条）

- 挂载位置：materials.material_animations[*].animations[*]
- 识别字段：type=group, material_type=video, panel=video
- 草稿实际使用编号：effect_id + resource_id
- 免费 107 条，VIP 16 条
```text
name | effect_id | resource_id | is_vip | default_duration_sec
三分割 | 922958 | 6873360856541827591 | false | 0.5
三分割 II | 922957 | 6873360923646497293 | false | 0.5
上下分割 | 931224 | 6875935836177699335 | false | 0.5
上下分割 II | 3144548 | 6875935919661126157 | false | 0.5
上升旋转 | 691841 | 6813965595915063815 | false | 0.5
下降向右 | 503140 | 6781683518222111239 | false | 0.5
下降向左 | 446392 | 6759351225772151303 | false | 0.5
中间分割 | 871868 | 6856970350270353928 | false | 0.5
中间分割 II | 871867 | 6856970411352003080 | false | 0.5
叠叠乐 | 872824 | 6836319728038842894 | false | 0.5
叠叠乐 II | 872826 | 6836319649844433415 | false | 0.5
叠叠乐 III | 872828 | 6836319781004513805 | false | 0.5
叠叠乐 IV | 872830 | 6836319828656001550 | false | 0.5
叠叠乐 V | 872834 | 6836319888827486728 | false | 0.5
叠叠乐 Ⅵ | 872836 | 6839582631345000967 | false | 0.5
右拉镜 | 471347 | 6772415374165021191 | false | 0.5
向右下降 | 503138 | 6781683438396117517 | false | 0.5
向右缩小 | 471341 | 6772415063216099848 | false | 0.5
向左下降 | 447588 | 6760223716392571395 | false | 0.5
向左缩小 | 471343 | 6772415148423385607 | false | 0.5
哈哈镜 | 748348 | 6832226792556728846 | false | 0.5
哈哈镜 II | 748350 | 6832226909875606029 | false | 0.5
四格滑动 | 945730 | 6883727868451361293 | false | 0.5
四格翻转 | 1362932 | 6865578846393995784 | false | 0.5
四格转动 | 957940 | 6891835548688716302 | false | 0.5
四格转动 II | 957939 | 6891835601067184653 | false | 0.5
回弹伸缩 | 530249 | 6795425591014199822 | false | 0.5
夹心饼干 | 1362936 | 6868146033247916558 | false | 0.5
夹心饼干 II | 1362934 | 6868146123710665223 | false | 0.5
小火车 | 885144 | 6860405888784536072 | false | 0.5
小火车 II | 885143 | 6860406007160377863 | false | 0.5
小火车 III | 885142 | 6860406091700769293 | false | 0.5
小火车 IV | 885141 | 6860406196130550286 | false | 0.5
小陀螺 | 923592 | 6874487656969933325 | false | 0.5
小陀螺 II | 923591 | 6874487735059485198 | false | 0.5
左右分割 | 948476 | 6886282872680878599 | false | 0.5
左右分割 II | 948475 | 6886282936048423431 | false | 0.5
左拉镜 | 471345 | 6772415248973435395 | false | 0.5
弹入旋转 | 669963 | 6810286558826992136 | false | 0.5
形变右缩 | 813139 | 6851395907804467720 | false | 0.5
形变左缩 | 813140 | 6851395726937690637 | false | 0.5
形变缩小 | 487587 | 6777260789263766030 | false | 0.5
悠悠球 | 717346 | 6821451358101574152 | false | 0.5
悠悠球 II | 717348 | 6821451462904648200 | false | 0.5
手机 | 1362928 | 6861892418334102030 | false | 0.5
手机 II | 1362926 | 6862918279183208973 | false | 0.5
手机 III | 1362924 | 6862918366550561294 | false | 0.5
扭曲拉伸 | 1426278 | 7026278592623415822 | false | 0.5
抖入放大 | 450264 | 6761360765925462536 | false | 0.5
拉伸扭曲 | 1425496 | 7025952723027628557 | false | 0.5
放大弹动 | 1418682 | 7023931891363353101 | false | 0.5
斜转 | 872874 | 6847734302193488392 | false | 0.5
斜转 II | 872876 | 6847734360636920327 | false | 0.5
方片转动 | 968162 | 6897114113726485000 | false | 0.5
方片转动 II | 968161 | 6897114201702011405 | false | 0.5
旋入晃动 | 519840 | 6789167874511475207 | false | 0.5
旋出渐隐 | 719940 | 6824302025698710024 | false | 0.5
旋转上升 | 691843 | 6813965670716281352 | false | 0.5
旋转伸缩 | 530247 | 6795425422046663182 | false | 0.5
旋转回吸 | 669965 | 6810286613898203661 | false | 0.5
旋转缩小 | 445858 | 6759046644462785037 | false | 0.5
旋转降落 | 445856 | 6759046515521491464 | false | 0.5
晃动旋出 | 519842 | 6789167998700622350 | false | 0.5
水晶 | 1362920 | 6857333749718192654 | false | 0.5
水晶 II | 1362922 | 6857333869541069325 | false | 0.5
波动滑出 | 1392376 | 7017646605671076359 | false | 0.5
海盗船 | 1362866 | 6830302168751280648 | false | 0.5
海盗船 II | 1362868 | 6830302282995732999 | false | 0.5
海盗船 III | 1362872 | 6830302335047045639 | false | 0.5
海盗船 IV | 1362870 | 6830302424826122765 | false | 0.5
滑入波动 | 1418546 | 7023747922718102023 | false | 0.5
滑滑梯 | 741020 | 6828829568879563271 | false | 0.5
滑滑梯 II | 741022 | 6828829741013799432 | false | 0.5
百叶窗 | 467361 | 6771299961171612174 | false | 0.5
百叶窗 II | 506768 | 6782101071402635790 | false | 0.5
碎块滑动 | 490068 | 6778405418969338382 | false | 0.5
碎块滑动 II | 489860 | 6778300107113632269 | false | 0.5
立方体 | 872856 | 6837352063496622599 | false | 0.5
立方体 II | 872858 | 6834812485023830535 | false | 0.5
立方体 III | 872860 | 6834812541118452237 | false | 0.5
立方体 IV | 872864 | 6841793140949520910 | false | 0.5
立方体 V | 873096 | 6841793224663634446 | false | 0.5
绕圈圈 | 872868 | 6850287838441771534 | false | 0.5
绕圈圈 II | 872872 | 6850287920255865357 | false | 0.5
绕圈圈 III | 872918 | 6854782718975152653 | false | 0.5
绕圈圈 IV | 872920 | 6854782786553778695 | false | 0.5
缩小弹动 | 1392530 | 7017689072978104869 | false | 0.5
缩小旋转 | 447318 | 6760119657429996046 | false | 0.5
缩小转出 | 638823 | 6805018974070247950 | false | 0.5
缩放 | 446078 | 6759078592740594184 | false | 0.5
缩放 II | 493000 | 6779083172429697544 | false | 0.5
翻转 | 872838 | 6843309964732142094 | false | 0.5
翻转 II | 872840 | 6843310029689328135 | false | 0.5
翻转 III | 872842 | 6843310084743762446 | false | 0.5
翻转 IV | 872844 | 6843310129736061447 | false | 0.5
翻转 V | 872848 | 6843310237902967304 | false | 0.5
翻转 VI | 872850 | 6843310299991249421 | false | 0.5
荡秋千 | 680643 | 6811007755785081357 | false | 0.5
荡秋千 II | 680645 | 6811007833069326862 | false | 0.5
转入转出 | 638793 | 6805012562174808590 | false | 0.5
转入转出 II | 701967 | 6818747242258633224 | false | 0.5
转圈圈 | 741502 | 6829129745226011144 | false | 0.5
过山车 | 911862 | 6870060878234915342 | false | 0.5
过山车 II | 911861 | 6870060932928639501 | false | 0.5
降落旋转 | 446076 | 6759075297091392007 | false | 0.5
魔方 | 1362938 | 6870060995365048840 | false | 0.5
魔方 II | 1362940 | 6870061049559650829 | false | 0.5
分身 | 945872 | 6883761132645913096 | true | 0.5
分身 II | 945871 | 6883761226950644231 | true | 0.5
动感摇晃I | 6983415 | 7173927429394666020 | true | 0.5
动感摇晃II | 7129471 | 7175103054956466744 | true | 100
四格滑动 II | 945729 | 6883727923845534216 | true | 0.5
四格翻转 II | 1362930 | 6865579178599649806 | true | 0.5
回忆旋转 | 8300599 | 7186961278022193722 | true | 0.5
坠落 | 14020637 | 7235902373971890747 | true | 0.5
弹动冲屏 | 9491799 | 7200308690904158778 | true | 0.5
波动吸收 | 2786424 | 7107468232390349349 | true | 0.5
波动放大 | 3113716 | 7111631619768717860 | true | 0.5
相框滑动 | 10166295 | 7206139216038728248 | true | 0.5
红酒摇晃 | 1417022 | 6903771548436402702 | true | 0.8
跳跳糖 | 9432783 | 7199944821098680890 | true | 0.7
闪光放大 | 6210029 | 7166437469909422623 | true | 0.5
闪光放大 II | 6210033 | 7166437532568130055 | true | 0.5
```


---

## 附录 O 转场清单（453 条）

- 挂载位置：materials.transitions[*]
- 草稿实际使用编号：effect_id + resource_id
- is_overlap 表示这类转场是否允许重叠
- 免费 130 条，VIP 323 条
```text
name | effect_id | resource_id | is_vip | default_duration_sec | is_overlap
3D空间 | 1506926 | 7049979667406656014 | false | 1.5 | true
上下翻页 | 77055399 | 7397337005387944457 | false | 1 | true
上移 | 2917279 | 6724846395116753416 | false | 0.5 | true
下移 | 2917280 | 6724849276100284942 | false | 0.5 | true
中心旋转 | 878914 | 6858191434294497805 | false | 0.5 | false
云朵 | 2912469 | 6955722927161479694 | false | 0.5 | true
倒影 | 369691 | 6748313807031898627 | false | 0.5 | true
冰雪结晶 | 1017910 | 6919369228701143559 | false | 0.5 | false
冲鸭 | 1441672 | 7030714241359286821 | false | 0.5 | false
分割 | 4211683 | 6968372308419285540 | false | 0.5 | true
分割 II | 4211740 | 6969782622868214302 | false | 0.5 | true
分割 III | 4211739 | 6969793843403166215 | false | 0.5 | true
分割 IV | 4211738 | 6969793934356648455 | false | 0.5 | true
前后对比 II | 28895844 | 7299290706277831218 | false | 0.8 | true
动漫云朵 | 2911876 | 6777178865119793678 | false | 0.5 | false
动漫漩涡 | 878913 | 6858191448827761160 | false | 0.5 | false
动漫火焰 | 2911875 | 6777178765643485709 | false | 0.5 | false
动漫闪电 | 2911874 | 6777178696609436174 | false | 0.5 | false
压缩 | 4212466 | 6751618376780485133 | false | 0.5 | true
叠加 | 1003369 | 6914112332205396488 | false | 1 | true
叠化 | 322577 | 6724845717472416269 | false | 0.5 | true
右移 | 2917287 | 6726711296063967748 | false | 1 | true
向上 | 359459 | 6724227090872275463 | false | 1 | false
向上擦除 | 2917281 | 6724849456891564557 | false | 0.5 | true
向下 | 359449 | 6724227330190873100 | false | 1 | false
向下擦除 | 2917282 | 6724849752921346573 | false | 0.5 | true
向下流动 | 878912 | 6858191469807669773 | false | 0.5 | false
向右 | 359527 | 6724227599616184836 | false | 1 | false
向右上 | 359567 | 6724227870559834635 | false | 0.5 | true
向右下 | 359537 | 6724228621742903815 | false | 0.5 | true
向右拉伸 | 4211782 | 6987299127025472031 | false | 0.5 | true
向右擦除 | 2917284 | 6724849898857959950 | false | 0.5 | true
向右流动 | 878911 | 6858191483573375495 | false | 0.5 | false
向左 | 359529 | 6724227717195108867 | false | 0.5 | false
向左上 | 359533 | 6724230442679013902 | false | 0.5 | true
向左下 | 359535 | 6724230577211314695 | false | 0.5 | true
向左拉伸 | 4211781 | 6987201429622493732 | false | 0.5 | true
向左擦除 | 2917283 | 6724849999336706573 | false | 0.5 | true
吸入 | 15653345 | 7246288124110705209 | false | 1 | true
回忆下滑 | 33106283 | 7309840407406318117 | false | 1 | true
圆形分割 II | 37127313 | 7317206886053319194 | false | 0.8 | true
圆形扫描 | 813992 | 6851775006418932238 | false | 1 | true
圆形遮罩 | 2916676 | 6725767129519362573 | false | 0.5 | true
圆形遮罩 II | 2916675 | 6724850215364334083 | false | 1 | true
复古放映 | 14192091 | 7237068402945167909 | false | 0.6 | true
岁月的痕迹 | 1185194 | 6982750240663147044 | false | 1 | true
左下角 II | 30874190 | 7304868316252738098 | false | 0.7 | true
左移 | 2917286 | 6726711499676455435 | false | 1 | true
开幕 | 391781 | 6750893890712113677 | false | 0.5 | true
弹幕转场 | 1433950 | 7028877116259176974 | false | 4 | false
弹跳 | 368205 | 6747865141120864779 | false | 0.5 | true
打板转场 I | 1432322 | 7028143517570437668 | false | 4 | false
打板转场 II | 1437264 | 7029592645538157086 | false | 4 | false
抖动 | 17223925 | 7252544245444121148 | false | 0.8 | true
抖动 II | 17223924 | 7252544309830881851 | false | 0.8 | true
抠像旋转 | 73423370 | 7386584387128660506 | false | 0.8 | true
拉伸 | 13402655 | 7231391397717217851 | false | 1.2 | true
拉伸 II | 19137130 | 7259735372039459389 | false | 0.6 | true
拉远 | 359365 | 6724226338418332167 | false | 1 | false
拍摄器 | 2057168 | 7100849808784495135 | false | 0.5 | true
推近 | 359359 | 6724226861666144779 | false | 1 | false
撕纸拉屏 | 17934952 | 7254847807465460280 | false | 0.7 | true
放射 | 4212630 | 6724239584663704071 | false | 1 | true
故障 | 2918080 | 6725771847444468236 | false | 1 | false
故障拼贴 | 77055395 | 7397337004507140618 | false | 1 | true
斜向分割 | 4211687 | 7085250093527339557 | false | 0.5 | true
星星 | 2916678 | 6751564373317128708 | false | 0.5 | true
星星 II | 2916679 | 6789847494898487822 | false | 0.5 | true
模糊 | 4212596 | 6911569618171597320 | false | 0.5 | true
横向分割 | 4211685 | 7083771238564237861 | false | 0.5 | true
横向拉幕 | 2917278 | 6724492948144132621 | false | 1 | true
横向模糊 | 97482744 | 7450031573958660645 | false | 0.5 | true
横线 | 2918076 | 6724845810892149251 | false | 0.5 | true
气泡转场 | 1433968 | 7028880945671311903 | false | 4 | false
水墨 | 521328 | 6789847231873683976 | false | 0.5 | true
水波卷动 | 878910 | 6858191497280360973 | false | 0.5 | false
水波向右 | 878909 | 6858191510865711629 | false | 0.5 | false
水波向左 | 878908 | 6858191524312650248 | false | 0.5 | false
泛光 | 4202527 | 6914112263645303303 | false | 1 | true
泛白 | 4202528 | 6949828109663212045 | false | 1 | false
波点向右 | 878907 | 6858191541706428941 | false | 0.5 | false
渐变擦除 | 1017911 | 6919369138800431629 | false | 1 | true
滑动 | 4212349 | 6757982416649851399 | false | 1 | true
漩涡 | 4211780 | 6851810799510360583 | false | 1 | false
烟雾转场 | 97482746 | 7450031574923350555 | false | 1.5 | true
爱心 | 2916677 | 6748289440130535947 | false | 0.5 | true
爱心 II | 2916682 | 6789846472343949837 | false | 0.5 | true
爱心上升 | 2916681 | 6789846246069637640 | false | 0.5 | true
电视故障 I | 2918081 | 7046293801123451405 | false | 1.6 | true
电视故障 II | 2918082 | 7042278078415901192 | false | 1.6 | true
画笔擦除 | 2912467 | 6789846828788486664 | false | 0.5 | true
白光快闪 | 49272367 | 7343136487182963211 | false | 0.4 | true
白色墨花 | 878906 | 6858191556055142919 | false | 0.5 | false
白色烟雾 | 947664 | 6885646856672514567 | false | 0.5 | false
百叶窗 | 521326 | 6789847331060584974 | false | 0.5 | true
眨眼 | 2917719 | 6864867302936941064 | false | 0.5 | true
矩形分割 | 878905 | 6858191571196580359 | false | 0.5 | false
窗格 | 368721 | 6747989545448378888 | false | 0.5 | true
立方体 | 519784 | 6785042367498949127 | false | 0.5 | true
竖向分割 | 4211686 | 7083771107706147364 | false | 0.5 | true
竖向拉幕 | 2917285 | 6726711903684399619 | false | 1 | true
竖向模糊 | 3796327 | 7125661387568714247 | false | 0.8 | true
竖向模糊 II | 23404229 | 7280837008421818936 | false | 0.66 | true
竖线 | 2918077 | 6724846536041173511 | false | 0.5 | true
箭头向右 | 878904 | 6858191587554365966 | false | 0.5 | false
粒子 | 4212632 | 6855565313715474952 | false | 0.5 | true
翻篇 | 4212350 | 7034446419641504264 | false | 1.3 | true
翻页 | 368701 | 6747979085894390279 | false | 0.5 | true
色差逆时针 | 1069274 | 6940500629013926413 | false | 1 | false
色差顺时针 | 1069374 | 6940520116035523080 | false | 1 | false
色彩溶解 | 322583 | 6724846004274729480 | false | 0.5 | true
色彩溶解 II | 322625 | 6724866927933526542 | false | 1 | true
色彩溶解 III | 322627 | 6724867032312975875 | false | 1 | true
蓝色线条 | 878903 | 6858191605384352263 | false | 0.5 | false
逆时针旋转 | 359437 | 6724226603372515853 | false | 0.5 | true
逆时针旋转 II | 17224251 | 7252544659245765179 | false | 0.8 | true
镜像翻转 | 2917288 | 6848792278710882824 | false | 1 | false
闪白 | 322575 | 6724845376098013708 | false | 0.5 | false
闪白 II | 31619869 | 7306818286413419017 | false | 0.3 | true
闪黑 | 321493 | 6724239388189921806 | false | 0.5 | false
雪花故障 | 2918079 | 6724866446842663431 | false | 1 | false
雾化 | 11387229 | 7216171159589491259 | false | 1.2 | true
震动 | 9261771 | 7198100561235808825 | false | 1 | true
顺时针旋转 | 359421 | 6724226684721041932 | false | 0.5 | true
顺时针旋转 II | 17224317 | 7252544556799889975 | false | 0.8 | true
频闪 | 1674710 | 7083767957662208549 | false | 0.5 | true
风车 | 369485 | 6748286529921094157 | false | 0.5 | true
马赛克 | 4212631 | 6724866519022440967 | false | 1 | true
黑色块 | 2918078 | 6724866346569437710 | false | 0.5 | true
黑色烟雾 | 947663 | 6885647017452769805 | false | 0.5 | false
2024回忆流 | 97032533 | 7448898555617481225 | true | 2 | true
X形震闪 | 79087478 | 7403208545111380531 | true | 1 | true
万花筒 | 18722268 | 7257806429086552632 | true | 0.8 | true
三屏放大 | 38586528 | 7320254175466492467 | true | 1 | true
三屏滑入 | 34443818 | 7312438185261273650 | true | 1 | true
三屏闪切 | 17242682 | 7252599996254523959 | true | 0.8 | true
下滑 | 32998125 | 7309694074015977993 | true | 0.55 | true
中心切开 | 97482739 | 7450031574931739146 | true | 2 | true
二次元烟效 | 90037010 | 7436273714729062921 | true | 1.92 | true
云朵 II | 2912470 | 6955760408737092132 | true | 0.5 | true
亮点模糊 | 3705757 | 7123135366504124936 | true | 1 | true
便利贴 | 29871972 | 7302023728441856549 | true | 1.1 | true
信号故障 | 25265947 | 7288149307197231676 | true | 0.5 | true
信号故障 II | 49094731 | 7342791345162949183 | true | 0.67 | false
倾斜拉伸 | 72481265 | 7383960886131560960 | true | 0.8 | true
倾斜拉开 | 97482745 | 7450031573958660646 | true | 2 | true
倾斜模糊 | 56268173 | 7355762441533264394 | true | 0.8 | true
像素冲屏 | 1182216 | 6981689835534684702 | true | 0.8 | true
光束 | 4202531 | 6982127832042312206 | true | 0.5 | true
全息投影 | 28518430 | 7298230450768581129 | true | 0.4 | true
六边形变焦 | 7824963 | 7182413216276812346 | true | 1 | true
冲屏扭曲 | 58099421 | 7359133728313971227 | true | 0.9 | true
几何分割 | 3985085 | 7130139199394550303 | true | 0.5 | true
几何滑动 | 90546381 | 7437386424036364837 | true | 1 | true
分屏下滑 | 46873416 | 7337974537683735080 | true | 0.9 | true
前后对比 | 10139297 | 7205856572994490935 | true | 1.2 | true
剧烈摇晃 | 63047898 | 7367356130307084838 | true | 0.9 | true
卡片弹出 | 72605929 | 7384334283659285032 | true | 1 | true
发光变焦 | 79046595 | 7402999668767986191 | true | 1 | true
叠化扭曲 | 92006146 | 7439255870896083466 | true | 0.5 | true
可爱爆炸 | 8375167 | 7187674415268631101 | true | 0.8 | true
可爱龙龙 | 44314889 | 7332697146929451546 | true | 1 | true
吃掉 | 66629623 | 7372506069328728585 | true | 0.9 | true
后台切换 | 38530921 | 7320129407799005734 | true | 0.8 | true
向上波动 | 4861515 | 7148734739807998495 | true | 5 | true
向下抖动 | 47241669 | 7338709911791997480 | true | 1.3 | true
向下拖拽 | 9382531 | 7199528468244075067 | true | 0.8 | true
向左拉屏 | 1722934 | 7089311972235153950 | true | 0.5 | true
向左波动 | 3971081 | 7126772940451877406 | true | 5 | true
喜欢 | 1600478 | 7070430644563612191 | true | 0.5 | true
四屏转换 | 46644610 | 7337612480610308649 | true | 1 | true
四格展开 | 81987893 | 7412560964198863394 | true | 0.5 | true
回忆 | 4211778 | 6748220149284737550 | true | 0.5 | true
回忆 II | 4211779 | 6748220462746046989 | true | 0.5 | true
回忆拉屏 | 8027945 | 7184682990901924410 | true | 1 | true
回忆拉屏 II | 31456359 | 7306440470119322139 | true | 0.7 | true
图片放大 | 89190525 | 7434055685576348170 | true | 1 | true
圆形分割 | 4211684 | 7083435788322476581 | true | 1.5 | false
圆盘旋转 | 48516414 | 7341334144485429810 | true | 0.7 | true
圣诞光斑 | 97572058 | 7450334536455426569 | true | 1.03 | true
圣诞光斑II | 98049569 | 7451488401062105610 | true | 1.03 | true
圣诞树 | 29976594 | 7302357935902954035 | true | 0.7 | true
圣诞礼盒 | 96154390 | 7447067834628182578 | true | 1.5 | true
复古叠影 | 9529419 | 7200638304591548985 | true | 1 | true
复古放映 II | 14607947 | 7240050497804046908 | true | 1 | true
复古漏光 | 8104139 | 7181752495150993957 | true | 0.8 | true
复古漏光 II | 25193261 | 7287881053534949943 | true | 0.6 | true
复古胶片 | 19552395 | 7261814111816651322 | true | 1 | true
多层环形 | 67116644 | 7373523970538082866 | true | 1.5 | true
多屏定格 | 25184085 | 7287860606395224613 | true | 0.8 | true
大圆盘 | 59713023 | 7362104359682839055 | true | 0.8 | true
大波浪 | 86769062 | 7426688369653977638 | true | 0.833 | true
字母拼贴 | 35402126 | 7314304549575987749 | true | 1 | true
射灯 | 63886272 | 7368775489445433883 | true | 1.6 | true
小喇叭 | 1600476 | 7070430823597478407 | true | 0.5 | true
小恶魔 | 1628344 | 7075598043252265509 | true | 1 | true
左移弹动 | 34525642 | 7312690473108247078 | true | 0.8 | true
幻影 | 11634125 | 7218040359715082809 | true | 0.8 | true
幻觉 | 76465118 | 7395044376621093391 | true | 1 | true
开心 | 1610838 | 7073053544839909919 | true | 0.5 | false
弹出 | 76381219 | 7394709307842892303 | true | 0.9 | true
弹动发光 | 51950360 | 7347897562436735503 | true | 0.8 | true
彩色像素 | 4212518 | 7096015235953201701 | true | 0.5 | false
彩色滑片 | 90546380 | 7437386424036381234 | true | 1.5 | true
往上翻页 | 102053853 | 7461951141333439013 | true | 1.04 | true
微抖动 | 63860874 | 7368739347845091877 | true | 1.5 | true
心形叠化 | 20224653 | 7264829174601224764 | true | 1 | true
快涂擦除 | 97482742 | 7450031573954466331 | true | 0.5 | true
快速缩放 | 71890617 | 7382154814144123392 | true | 1 | true
快速震闪 | 79172318 | 7403364394404418074 | true | 1 | true
快门 | 2917720 | 6882983860615778823 | true | 0.5 | true
惊悚屏闪 | 86397088 | 7425528298395931187 | true | 1 | true
手机屏放大 | 96240495 | 7447351620649620005 | true | 2 | true
扫光 | 4202535 | 7106765945305043463 | true | 0.5 | true
扭曲弹动 | 79044291 | 7402970650379293199 | true | 1 | true
扭曲旋入 | 67190756 | 7373640088091103763 | true | 1 | true
扭曲溶解 | 67617874 | 7374259106502152741 | true | 1 | true
扭转弹动 | 50231600 | 7344986966145896994 | true | 1.5 | true
抖动放大 | 19272888 | 7260415521852494397 | true | 0.8 | true
抖动缩小 | 26488746 | 7291972229087105563 | true | 0.7 | true
抖动缩小  II | 36841926 | 7316783851206873651 | true | 1 | true
折痕胶带 | 90037011 | 7436273714733257225 | true | 1 | true
抽象前景 | 2459634 | 7104215831919202853 | true | 0.5 | true
抽象前景 II | 2870170 | 7108564115529929229 | true | 0.5 | true
拉开 | 72601002 | 7384323685026370098 | true | 0.6 | true
拉框入屏 | 28115429 | 7297077423487586826 | true | 1 | true
拍摄器 II | 2958464 | 7109727014780670495 | true | 0.9 | true
拍摄器 III | 2792048 | 7107542030976291336 | true | 0.8 | true
挤压分屏 | 89895302 | 7435897594074632713 | true | 0.83 | true
推近 II | 26135688 | 7290852476259930685 | true | 0.9 | true
推远 II | 59043083 | 7360987817066893862 | true | 1 | true
摄像机 | 1598384 | 7070047850960261668 | true | 0.5 | true
摇晃描边 | 66403340 | 7372137986877559335 | true | 1 | true
摇晃震动 | 49545855 | 7343618757530489379 | true | 1.3 | true
摇镜 | 31254345 | 7305969268259033609 | true | 0.7 | true
撕纸 | 2912468 | 6875627914444935694 | true | 0.5 | true
撕纸掉落 | 11661051 | 7218114518314914365 | true | 1.2 | true
收缩抖动 | 51859926 | 7347676775633130024 | true | 1 | true
放大左移 | 51784590 | 7347582471111709236 | true | 1.3 | true
放大镜 | 35244988 | 7313974602156216858 | true | 0.7 | true
故障扫描 | 86396968 | 7425528124013548059 | true | 1 | true
故障模糊 | 29927992 | 7302270954602762789 | true | 0.7 | true
数字矩阵 | 20983534 | 7268870949548593725 | true | 1 | true
斜向模糊 | 3796323 | 7125661284762128910 | true | 0.8 | true
斜向闪光 | 72603864 | 7384331194978013711 | true | 0.7 | true
斜线翻页 | 47905855 | 7339900424956154403 | true | 0.7 | true
新篇章 | 7089439 | 7174756125902901797 | true | 0.8 | true
新篇章 II | 7089435 | 7174754977544409657 | true | 1.6 | true
方形分割 | 3895735 | 7127901205820346917 | true | 0.5 | true
方形变焦 | 77388758 | 7398512469884277260 | true | 1 | true
方形模糊 | 3686479 | 7122721406210544164 | true | 1 | true
方形模糊 II | 72501238 | 7384005295770440201 | true | 1 | true
方片翻转 | 98063100 | 7451501266246570534 | true | 1.1 | true
旋焦 | 11286537 | 7215424325036282428 | true | 0.5 | true
旋转圆球 | 69481298 | 7377722094806635048 | true | 0.8 | true
旋转圆盘 | 19556167 | 7261828356386067005 | true | 1 | true
旋转圆盘 II | 19727008 | 7262674749258469949 | true | 1 | true
旋转快门 | 53358879 | 7350577049968316979 | true | 1 | true
旋转拨盘 | 63924504 | 7368844683256009242 | true | 1 | true
旋转模糊 | 44259414 | 7332480491058106943 | true | 1.2 | true
旋转穿越 | 49228871 | 7343092798993732148 | true | 1.8 | true
旋转纵深 | 63822177 | 7368687055225754153 | true | 0.9 | true
旋转翻页 | 38717232 | 7320577375752688165 | true | 0.8 | true
旋转震动 | 41492871 | 7326861725213397514 | true | 0.6 | true
无缝撕裂 | 92006145 | 7439255870896083506 | true | 1.5 | true
无限穿越 I | 1465694 | 7036984568536109581 | true | 1.6 | true
无限穿越 II | 1458828 | 7034717113130422791 | true | 1.6 | true
日历转场 | 101496138 | 7460472998944838154 | true | 2 | true
旧胶片 | 1933296 | 7099310030138118687 | true | 0.5 | false
旧胶片 II | 3114014 | 7111634884153578014 | true | 0.5 | true
时光穿梭 | 31645629 | 7306853312400200229 | true | 1.1 | true
星光 | 7339355 | 7177201869612126777 | true | 1.5 | true
星光叠化 | 39173243 | 7321658733497422363 | true | 0.8 | true
星光炸开 | 31644713 | 7306852010320466483 | true | 1.3 | true
星星 III | 26885516 | 7293358903176204851 | true | 0.5 | true
星星变焦 | 98464024 | 7452559875839627786 | true | 1 | true
星星吸入 | 34540914 | 7312716430875562506 | true | 1 | true
星星模糊 | 10169537 | 7206157339253019197 | true | 0.8 | true
春日光斑 | 43351778 | 7330599151685603875 | true | 1 | true
暧昧光晕 | 20954940 | 7268613185337299513 | true | 0.8 | true
曝光拉丝 | 32432969 | 7308617539452408358 | true | 2 | true
曝光摇镜 | 24147753 | 7283720497513108025 | true | 0.7 | true
未来光谱 | 7307905 | 7176890183940313658 | true | 0.8 | true
未来光谱II | 7312585 | 7176914791267570232 | true | 0.8 | true
条形模糊 | 3675841 | 7122387202725646862 | true | 1 | true
模糊放大 | 29614872 | 7301280654015074842 | true | 1 | true
模糊细闪 | 98464023 | 7452559875839627785 | true | 1.17 | true
模糊缩小 | 28141206 | 7297133348567126566 | true | 1.2 | true
横向分屏 | 53798168 | 7351341191184519699 | true | 1 | true
横向滑动 | 89071753 | 7433711910727455242 | true | 1.53 | true
横向震动 | 79166394 | 7403329110597964340 | true | 1 | true
横条挤压 | 64687184 | 7369507828668568116 | true | 1.2 | true
横移模糊 | 36950128 | 7316901787762430491 | true | 0.8 | true
樱花飞舞 | 102144538 | 7462198817211814426 | true | 2 | true
水滴 | 11765299 | 7218875183413596730 | true | 0.5 | true
水滴 II | 13482623 | 7231860840452854332 | true | 0.9 | true
水滴 III | 46608908 | 7337571999885038130 | true | 1.1 | true
水滴溶解 | 77055389 | 7397337004507140646 | true | 1 | true
汇聚 | 32470148 | 7308666709932511753 | true | 1 | true
泡泡模糊 | 5663559 | 7159097688955294222 | true | 1 | true
波光粼粼 | 59511491 | 7361758664182469157 | true | 1.167 | true
波动 | 6500749 | 7169480114860724773 | true | 0.5 | true
波动 II | 32459394 | 7308652550574576138 | true | 0.4 | true
波动故障 | 12349835 | 7223312837320380983 | true | 0.6 | true
泼墨晕染 | 85924530 | 7424057373741814298 | true | 0.7 | true
流光 | 36847370 | 7316789832833831461 | true | 1 | true
涂鸦放大 | 14573363 | 7239925851335168569 | true | 1.5 | true
溶解推进 | 52246665 | 7348406367394206271 | true | 0.806 | true
滑动压迫感 | 96240496 | 7447351620641231387 | true | 2 | true
滑动弹出 | 49343171 | 7343237606043292200 | true | 1 | true
滑动放大 | 41576555 | 7327132595190239759 | true | 1 | true
滑块拼贴 | 14594823 | 7239990715307004477 | true | 1.5 | true
滚动立方 | 105115378 | 7471167302029808138 | true | 0.733 | true
漩涡扭曲 | 32460372 | 7308653984888132123 | true | 0.7 | true
漫画撕纸 | 87580719 | 7429283264424055305 | true | 0.8 | true
火焰湍流 | 77055404 | 7397337005375361562 | true | 1 | true
炫光 | 4202524 | 6726707814028284423 | true | 0.5 | true
炫光 II | 4202530 | 6950255790762496548 | true | 0.5 | false
炫光 III | 4202529 | 6950255930160189988 | true | 0.5 | false
炫光弹动 | 52201950 | 7348337133838406194 | true | 1 | true
炫光扫描 | 66131585 | 7371717412736995903 | true | 1.467 | true
炫光扭动 | 89895303 | 7435897594703778330 | true | 0.7 | true
炸弹 | 1632990 | 7076321483282190878 | true | 0.5 | true
烟花光斑 | 97260760 | 7449596462670811686 | true | 2 | true
烟雾弹 | 62284094 | 7366189026677625359 | true | 1.4 | true
热成像 | 89895304 | 7435897594074632742 | true | 1 | true
燃烧 | 1722848 | 7089309494550729253 | true | 0.5 | true
燃烧 II | 1722824 | 7089307363806548510 | true | 0.5 | true
燃烧 III | 1714536 | 7088523814102897188 | true | 0.5 | true
爆米花 | 1623902 | 7075173004560306724 | true | 0.5 | true
爆闪 | 18010162 | 7255132261584998969 | true | 1 | true
爆闪 II | 19102212 | 7259635767096382011 | true | 0.6 | true
爱心冲击 | 80045036 | 7405941767867994624 | true | 1.5 | true
爱心模糊 | 12851969 | 7226945634312393274 | true | 0.6 | true
爱心气球 | 20810100 | 7267895649599754808 | true | 1 | true
爱心软糖 | 43363938 | 7330845783006122515 | true | 1.5 | true
爱心遮罩 | 104143934 | 7468589287299093029 | true | 2 | true
环回推近 | 97152408 | 7449266731089924658 | true | 1.533 | true
环形色散 | 72761824 | 7384745397022888488 | true | 0.9 | true
玻璃破碎 | 14930013 | 7242225450628420133 | true | 1 | true
玻璃破碎 II | 16373363 | 7249622034878042661 | true | 1 | true
珠光模糊 | 7738323 | 7181370814594290234 | true | 1 | true
生气 | 1600475 | 7070430937900651016 | true | 0.5 | false
电光 | 8298317 | 7186953120490983997 | true | 1 | true
电光 II | 26773684 | 7292990637350064690 | true | 1.3 | true
电流 | 78884363 | 7402545346741539365 | true | 1.167 | true
畸变回弹 | 89406897 | 7434746460186350130 | true | 2 | true
百叶窗 II | 74345085 | 7389190159989740072 | true | 0.8 | true
相机缩小 | 102354878 | 7462628239286997531 | true | 2 | true
相片切换 | 40583461 | 7324946677305971226 | true | 0.7 | true
相片拼贴 | 10917367 | 7212523710685647420 | true | 0.6 | true
礼物落下 | 102354705 | 7462627865197023782 | true | 2 | true
空间上移 | 79942985 | 7405560276180800009 | true | 0.5 | true
空间弹动 | 20330329 | 7265321906830578235 | true | 1 | false
空间弹动 II | 21121644 | 7269664953584325179 | true | 1 | false
空间弹动 III | 20330339 | 7265322078276948535 | true | 1 | false
空间弹动 IV | 21261060 | 7270393974517404215 | true | 1 | false
空间旋转 | 3878325 | 7127563142359421471 | true | 1 | true
空间旋转 II | 4360464 | 7137983390896099871 | true | 1 | true
空间旋转 III | 4382158 | 7138602593751667207 | true | 1 | true
空间翻转 | 11764147 | 7218870491400901157 | true | 1.2 | true
空间翻转 II | 12371701 | 7223591053973000761 | true | 1.2 | true
空间跳跃 | 32858947 | 7309399317662405146 | true | 0.633 | true
穿越 | 5083535 | 7152422191944962567 | true | 1 | true
穿越 II | 5076093 | 7152354215132664357 | true | 1 | true
穿越 III | 48498880 | 7341295618863665690 | true | 0.8 | true
立体旋转 | 77055394 | 7397337004511334962 | true | 1 | true
立体翻转 | 54820217 | 7353088031705797159 | true | 0.8 | true
立体翻页 | 5379189 | 7156512800867619335 | true | 0.8 | true
立体翻页 II | 5381749 | 7156527319274754568 | true | 0.8 | true
立方旋转 | 78218811 | 7400668689411871251 | true | 1 | true
竖向拉伸 | 72501228 | 7384005384349946418 | true | 1 | true
竖移模糊 | 21300860 | 7270505237935297085 | true | 0.6 | true
笔迹涂抹 | 89895305 | 7435897594078843419 | true | 2 | true
粉色反转片 | 9504701 | 7200360240393491000 | true | 0.8 | true
红包雨 | 39261991 | 7321942209752732186 | true | 1.5 | true
纵向滑动 | 89071754 | 7433711910727455259 | true | 1.33 | true
纸团 | 14451527 | 7238905266912105019 | true | 0.7 | true
翻书转场 | 92891048 | 7440002160588231194 | true | 1.6 | true
翻转冲屏 | 22253379 | 7275914638267519525 | true | 1.2 | true
翻页 II | 12108759 | 7221478593803588152 | true | 0.9 | true
聚光灯 | 40923539 | 7325700559556579878 | true | 1.1 | true
胶卷滑动 | 90546382 | 7437386424032170547 | true | 2 | true
胶片切闪 | 104151439 | 7468603557348905510 | true | 1.33 | true
胶片定格 | 10764691 | 7211146962513433147 | true | 1 | true
胶片擦除 | 32274061 | 7308265370480022026 | true | 0.8 | true
胶片融化 | 51067351 | 7346474643827462667 | true | 0.7 | true
胶片闪光 | 56656394 | 7356486482271408666 | true | 1 | true
色块故障 | 2483334 | 7104539089629614606 | true | 3 | false
色差故障 | 2918075 | 6724239785205961228 | true | 1 | false
色彩溶解 IV | 6736571 | 7171714374912971271 | true | 0.8 | true
色彩溶解 V | 6736575 | 7171714652248740365 | true | 0.8 | true
色彩负片 | 91077958 | 7438535170317095451 | true | 2 | true
色散晃镜 | 48127374 | 7340477409478578738 | true | 0.6 | true
色散波纹 | 72834771 | 7385028833356812840 | true | 1 | true
色散漩涡 | 79026278 | 7402904919188967963 | true | 0.8 | true
色散闪烁 | 13830295 | 7234416277974946365 | true | 0.8 | true
色散闪烁 II | 23586159 | 7281584246882308665 | true | 0.7 | true
草图转场 | 92006144 | 7439255870891889162 | true | 1 | true
荧光爆闪 | 48938221 | 7342499359503684150 | true | 0.8 | true
菱格翻转 | 1187052 | 6983867136510792206 | true | 1.45 | true
蓝光扫描 | 22119723 | 7275176500381356599 | true | 1 | true
蓝色反转片 | 9504705 | 7200358812316865085 | true | 0.8 | true
虹光旋入 | 78355265 | 7401039727761035815 | true | 1 | true
融化 | 9261283 | 7198096122970116663 | true | 1 | true
融化 II | 9503051 | 7200339965442527803 | true | 1 | true
课本转场 | 92924027 | 7440040705499599411 | true | 1.6 | true
负片下滑 | 29999964 | 7302412902181376539 | true | 0.6 | true
赛博马赛克 | 97482741 | 7450031573962854963 | true | 2 | true
超赞 | 1600477 | 7070430749547041293 | true | 0.5 | true
边框切换 | 89307364 | 7434412782285509157 | true | 2 | true
运镜压缩 | 96240499 | 7447351621266182665 | true | 2 | true
迷幻波纹 | 93683056 | 7441523705835950619 | true | 1 | true
迷幻频闪 | 90037012 | 7436273714733257242 | true | 1 | true
透镜故障 | 1889546 | 7097849004062413343 | true | 0.5 | true
重叠上滑 | 13582109 | 7232587870672785980 | true | 1.2 | true
金币祝福 | 41488441 | 7326856503963423282 | true | 1.5 | true
金沙 | 92634974 | 7439681605804757541 | true | 1.74 | true
金色光斑 | 37131315 | 7317211103652483621 | true | 0.8 | true
钱兔无量 | 8605167 | 7189608212193088060 | true | 1.5 | true
镜头速移 | 83974069 | 7418201851507511849 | true | 0.567 | true
长曝光 | 31452163 | 7306435255286633010 | true | 1 | true
闪光灯 | 4202532 | 6986584807543149063 | true | 1 | true
闪光灯 II | 15250161 | 7244074212158083641 | true | 1.9 | true
闪光灯 III | 15638113 | 7246234663755190839 | true | 0.8 | true
闪动光斑 | 4202525 | 6777178510050988551 | true | 0.5 | false
闪动光斑 II | 4840333 | 7148374073716773407 | true | 1 | true
闪回 | 16638473 | 7250427149318885945 | true | 0.2 | true
闪屏故障 | 52211013 | 7348352782744687130 | true | 1 | true
闪黑 II | 20257185 | 7264932863613604412 | true | 0.6 | true
闹钟 | 1621980 | 7074854214479909390 | true | 0.5 | false
雨刷转场 | 96240497 | 7447351621249405477 | true | 2 | true
雪花叠化 | 96135908 | 7447044441472242185 | true | 3 | true
雪花四散 | 95320371 | 7445177785405936165 | true | 2 | true
雪花环绕 | 95320370 | 7445177785397547547 | true | 2 | true
雪雾 | 32838061 | 7309372378096603699 | true | 1.7 | true
震动 II | 9041507 | 7195815265337086520 | true | 1 | true
震动缩小 | 47887388 | 7339865466506056207 | true | 1.1 | true
霓虹闪光 | 46839548 | 7337938801882305074 | true | 0.6 | true
霓虹闪光 II | 46846588 | 7337946710041170470 | true | 0.5 | true
顺时针三角 | 97482743 | 7450031573962854939 | true | 1.5 | true
飘雪 | 6506905 | 7169510140138230285 | true | 2 | true
飘雪 II | 6658449 | 7170983464416580133 | true | 2 | true
马赛克 II | 39369063 | 7322278354579624486 | true | 0.8 | true
马赛克III | 77055400 | 7397337004502946314 | true | 1 | true
鱼眼 | 5508285 | 7158359902950265352 | true | 0.8 | true
鱼眼 II | 5096381 | 7152723523721499167 | true | 0.8 | true
鱼眼 III | 21261750 | 7270399429297836605 | true | 1.333 | true
鱼眼波纹 | 89071756 | 7433711910731649563 | true | 0.6 | true
鸿运四叶草 | 101453156 | 7460402504589644326 | true | 2 | true
黑板擦除 | 89071755 | 7433711910723260979 | true | 2 | true
黑白摇镜 | 31620427 | 7306819191724577331 | true | 0.7 | true
黑色反转片 | 9683173 | 7202075814085530149 | true | 0.8 | true
```


---

## 附录 P 蒙版清单（6 条）

- 挂载位置：materials.masks[*]
- 草稿实际使用编号：effect_id + resource_id
- default_aspect_ratio 是默认宽高比
```text
name | effect_id | resource_id | resource_type | default_aspect_ratio
线性 | 636071 | 6791652175668843016 | line | 1
镜面 | 636073 | 6791699060140020232 | mirror | 1
圆形 | 636075 | 6791700663249146381 | circle | 1
矩形 | 636077 | 6791700809454195207 | rectangle | 1
爱心 | 636079 | 6794051276482023949 | geometric_shape | 1.115
星形 | 636081 | 6794051169434997255 | geometric_shape | 1.05
```


---

## 附录 Q 混合模式清单（10 条）

- 挂载位置：materials.effects[type=mix_mode]
- 草稿实际使用编号：effect_id + resource_id
- 免费 10 条，VIP 0 条
```text
name | effect_id | resource_id | is_vip
正片叠底 | 871333 | 6758325895519277582 | false
颜色减淡 | 871334 | 6758325800031752712 | false
颜色加深 | 871335 | 6758325724848853518 | false
线性加深 | 871336 | 6758325619253056013 | false
柔光 | 871337 | 6758325439212556814 | false
强光 | 871338 | 6758325264670790152 | false
滤色 | 871339 | 6758325170760323597 | false
叠加 | 871340 | 6758324989931295240 | false
变亮 | 871341 | 6758324919789949453 | false
变暗 | 871342 | 6758324839670354445 | false
```
