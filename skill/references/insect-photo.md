# 昆虫实拍参考与可编辑绘制

昆虫任务沿用 [影像数据库入口](species-image-reference.md)，支持 iNaturalist、GBIF。成虫可直接执行：

```text
python scripts/species_reference.py "Papilio machaon" <输出目录> --adult --limit 6
python scripts/species_reference.py "Coccinella septempunctata" <输出目录> --adult --limit 6
```

`--adult` 使用 iNaturalist Life Stage=Adult 注释筛选，不推断图片年龄。仅支持 iNaturalist；未加参数时沿用原有检索，已缓存请求保持可复用。注释较少的物种可能返回空结果，此时可另查未筛选候选并逐张核实阶段。幼虫、若虫、蛹、羽化初期和成熟成虫分别处理。

查看实际照片后挑选姿态与阶段相容的参考。数据库记录可能同时包含人物、环境、重复照片或多个个体；这些记录仍可能通过物种/阶段筛选，绘图时按实际画面选择。2026-09-15 实测金凤蝶与七星瓢虫，候选中确实出现幼虫、刚羽化未显斑成虫、人物照片和遮挡个体。

构形前将实际照片与专业物种条目、分类描述或解剖资料共同核对，按 [图像与描述共同约束生物绘图](morphology-evidence.md#图像与描述共同约束生物绘图) 落实器官与连接。核对头、胸、腹及附肢着生处，成虫三对足属于胸部；触角属于头部。翅数、退化翅、鞘翅、尾突、口器及显著性别差异按物种核实。足段与翅脉为展示性概括时保留连接及方向，避免将概括线条解释为完整解剖图。

- 蝶类分别组织左右前翅、后翅及对应斑纹，核对背腹面；颜色和斑纹随物种变化。金凤蝶实拍可见黄黑翅面、后翅蓝斑、红色眼斑与尾突，不将这一画法推广为所有蝴蝶。
- 七星瓢虫成熟成虫常见红色鞘翅及七个黑斑，前胸背板黑色、前侧角有浅色斑；背面成对鞘翅相接，中间共有斑可拆成两半随各侧编辑。新羽化成虫可能尚未显斑，不能据此绘制典型成熟色型。

本次专业核对：[UK Beetle Recording](https://coleoptera.org.uk/species/coccinella-septempunctata)。金凤蝶形态按本次已查看的 iNaturalist 成虫照片构形；亚种未指定。来源记录及许可独立保存，成稿使用语义部件组，实际渲染验收。

可复用图件：`assets/library/animal_insect.svg`（金凤蝶）、`assets/insects/seven-spot-ladybird.svg`（七星瓢虫）。

新增 10 种常见昆虫保存在 `assets/insects/`；名称、学名与图件路径见该目录 `catalog.json`，实际查看的照片来源及原照片许可见 `references.json`。覆盖蜜蜂、蜻蜓、螳螂、飞蝗、家蝇、蚊、蚁、蝉、蟑螂和蛾。图件公开署名 ScanSci，许可 CC BY 4.0。
