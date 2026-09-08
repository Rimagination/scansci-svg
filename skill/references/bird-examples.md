# 鸟类画法参考：独立生成参考 → 可编辑 SVG

这组样例用于学习构形、羽区分组和无支撑物展示足姿。按任务选一只鸟，先查看生成参考和 SVG 预览；需要曲线细节时才定位 SVG 中的部件。避免把两只鸟当作覆盖其他鸟类的换色模板。

| 样例 | 生成参考 | SVG 结果 | 学习重点 |
| --- | --- | --- | --- |
| 树麻雀 *Passer montanus*，左向站姿 | [参考 PNG](bird-examples-ai/sparrow-reference.png) | [预览](bird-examples-ai/sparrow-preview.png) · [SVG](bird-examples-ai/sparrow-naturalist.svg) | 栗色冠、白颊黑斑、黑喉斑独立分组；两道翼带与折叠翼层次；短粗锥形喙 |
| 欧亚鸲 *Erithacus rubecula*，左向闭喙站姿 | [参考 PNG](bird-examples-ai/robin-reference.png) | [预览](bird-examples-ai/robin-preview.png) · [SVG](bird-examples-ai/robin-naturalist.svg) | 橙色脸胸、灰色边界与淡腹；细喙；舒展足趾与轻弯爪 |

## 学什么、保留什么判断

- `bird` 包含整鸟；`body`、`wing`、`tail`、`head`、`foot-near`、`foot-far` 按部件联动。足组包含需要随足调整的可见腿段。
- 麻雀的 `chestnut-crown`、`ear-patch`、`black-bib`；欧亚鸲的 `orange-face-and-breast`、`grey-face-border`，示范识别性斑纹独立归属。
- 翼内按飞羽、次级飞羽和覆羽组织；羽片内部的明暗与边缘同组。路径数量只表达可见层次，不作解剖计数。
- 渐变使用 `paint-` 前缀，避免与部件 ID 重名。
- 生成图的背景光晕不进入 SVG。脚趾按独立展示用途重构。照片忠实、飞行、悬停等任务仍按 [姿态规则](bird-photo.md) 处理，不自动套站姿。

## 质量边界与生物学依据

本组采用概括的自然主义画法，可用于学习构形和分组。新对象重新量取比例、核对斑纹，并细化羽缘、胸腹色区和足趾透视。

树麻雀的物种特征来源见 [识别约束卡](bird-photo.md)。欧亚鸲核对橙红脸胸、灰色侧缘、橄榄褐上体、淡腹和细喙，参考 [RSPB](https://www.rspb.org.uk/birds-and-wildlife/robin) 与 [Natural History Museum](https://www.nhm.ac.uk/discover/robin-erithacus-rubecula.html)。这些资料用于核对形态，本组未复制其图片。性别、亚种等不从生成图反推。

## 来源记录

2026-09-07 使用内置 imagegen，分别按文字描述生成两只鸟；图像输入为空。之后依据新生成图重新构造 Bézier 路径，未复用此前用户照片转绘的路径。完整提示词与生成方式见 [provenance.json](bird-examples-ai/provenance.json)；工具未披露具体模型版本。

原照片衍生的三个 SVG 与三个预览保存在项目私有输出中。本组独立生成的参考图及原创 SVG 随本仓库发布，保留生成记录和实际输入来源。
