<div align="center">

<a href="https://github.com/Rimagination/scansci-svg/blob/main/assets/brand/scansci-svg-banner.svg"><img src="https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@59f10882605358a124e987622d4a594c5ced800d/assets/brand/scansci-svg-banner.png" width="100%" alt="ScanSci SVG — 让科学表达生动可见"></a>

<p><a href="#quick-start">开始使用</a> · <a href="#use-cases">能做什么</a> · <a href="#photo-to-svg">照片到 SVG</a> · <a href="#botanical-ink">植物墨线图</a> · <a href="https://www.scansci.com/symbols/">浏览素材库</a> · <a href="#installation">安装</a></p>

</div>

# ScanSci SVG

让一张科研图，从想法走到可以使用、可以继续修改的作品。

ScanSci SVG 是供 Codex 等 AI Agent 使用的科研绘图 skill。你可以描述一个对象、附上一张参考图片，或拿出已有的图件，让它协助绘制、还原、修改和排版，最后交付用于论文、教学或演示的文件。

默认交付 **SVG 源文件和预览图**。SVG 可以放大，也便于继续调整图中的文字、颜色和部件。开始时说明“哪些部分以后还要改”，能让结果更贴合你的工作。

<a id="quick-start"></a>

## 从一句话开始

安装后，把需求直接交给 Agent：

> 使用 $scansci-svg，画一株开花期水稻，根、茎、叶和穗分别可编辑，用于课堂展示。

也可以附上参考图：

> 使用 $scansci-svg，把这张科研示意图重建成 SVG。保留构图、标签和箭头方向，让主要对象能单独修改。

通常说明**画什么、用在哪里、希望保留什么、以后要改什么**就足够。物种、发育阶段、参考图片或目标期刊等已有信息，也可以一起提供。影响结果的关键条件不清楚时，Agent 会进一步确认。

还没有安装？把下面这句话发给支持安装 skill 的 Agent：

```text
帮我安装 https://github.com/Rimagination/scansci-svg，
使用仓库中的 skill/ 目录作为安装内容。
```

<a id="use-cases"></a>

## 从画出对象，到讲清一件事

### 画你研究的对象

植物、鸟类、昆虫、鱼类、微生物、人体器官，以及环境、仪器和工程设施，都可以作为绘图起点。你可以选择简洁的科研示意、自然插画、植物黑白线稿或精细墨线图，并说明需要展示的结构。

涉及具体物种时，绘制会结合可追溯的影像与形态描述，核对外形、器官和着生关系。素材库里没有的物种，也可以借助 iNaturalist、GBIF 等影像来源寻找参考。

> 画一只戴胜，参考实拍和形态描述，保留羽冠、喙和翅膀的识别特征。

### 把参考图变成可继续编辑的图

照片、已有插画、截图和生成图片都可以作为输入。根据用途，可以提取对象、忠实还原画面，也可以重建其中的文字、箭头和主要部件。

需要精细临摹时，重点保留轮廓、斑纹、线条和明暗；需要后续修改时，重点组织好要一起移动或调整的部件。参考图中看不清的部分和重建后的可见差异，会在交付时说明。

> 把这张鸟类插画重建成 SVG，保留羽毛斑纹，翅膀与尾羽分别可编辑。

<a id="photo-to-svg"></a>

### 一只麻雀，从照片走进你的图里

左边是 Laitche 在大阪拍摄的树麻雀，右边是根据这张照片重新绘制的 SVG。保留它站立时的体态、栗色头冠、白颊中的黑斑和折叠的翅膀，去掉石台与背景，就能把这只鸟放进自己的课件或生态场景。

| 原始照片 | SVG 重建预览 |
| --- | --- |
| ![Laitche 拍摄的树麻雀原始照片](https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@5a3b35cdf0ec07cf45da0c0d13e722ea71f5704f/assets/examples/sparrow-photo-svg/source-photo.jpg) | ![根据同一照片重建的树麻雀 SVG，白底预览](https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@311cd880518b5a36e089e090aca0f18bbe56bedc/assets/examples/sparrow-photo-svg/rebuilt-preview.png) |

SVG 背景透明，头部、喙、眼、翅膀、尾羽和腿足可以分别选中修改。这个案例采用简化的自然插画风格，羽毛边界与细纹经过概括，局部比例与照片仍有差异。

[下载麻雀 SVG](assets/examples/sparrow-photo-svg/sparrow-rebuilt.svg) · [查看照片原作](https://commons.wikimedia.org/wiki/File:Tree_Sparrow_August_2007_Osaka_Japan.jpg) · [案例与来源说明](assets/examples/sparrow-photo-svg/README.md)

照片：Laitche，公有领域。SVG：ScanSci，AI 辅助绘制，[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。

### 让多个对象组成一张完整的图

单件素材可以继续组成论文多面板图、生态场景或过程示意。已有图件也能制作不同配色、强调区域和展示版本，保持整套图的风格一致。

> 用植物、鸟类和监测设备组成河岸生态示意图，再把采样位置标出来。

> 把这三种植物排成一张论文图，统一标签和留白，注明各图非等比例。

### 把图带到你真正使用的地方

成稿后，可以继续要求导出透明 PNG、PDF 或可编辑 PPTX，也可以处理导入后的缺字、箭头错位、透明背景和显示差异。可编辑 PPTX 的交付会结合当前环境可用的导出工具，核对需要编辑的文字和图形。

需要动态展示时，可以制作科学过程动画，或把成稿编排为逐步出现的绘制回放，用于课程和汇报。绘制回放根据成稿重建步骤，不代表原始创作过程的录屏。

> 把这张图放进一页可编辑 PPT，文字和箭头需要在 PowerPoint 里继续调整。

> 让图中的颗粒沿已标出的运输路线移动，导出 GIF。

<a id="botanical-ink"></a>

## 植物墨线图：先看画面，再重建 SVG

墨线图用细致的轮廓、排线和点描表现植物。叶片的翻折、花序的疏密、刚毛的方向，以及器官之间的连接，共同决定图件是否清楚、自然。

ScanSci SVG 支持**先生成墨线参考，再重建可编辑 SVG**。从物种影像与形态资料出发，先确定画面的笔法和构图，再重建茎、叶、花果和细节，最后对照参考检查形态、连接和还原效果。已有满意的参考图时，可以直接进入重建。

> 画一幅狗尾草墨线图。参考实拍与形态描述，先生成精细参考，再重建 SVG；叶片、叶鞘、花序和刚毛分别可编辑，不加字母标注。

### 狗尾草案例

下面展示同一案例的生成参考与原生 SVG 重建结果。重建稿保留了三枝茎秆的构图，并将叶片、叶鞘和花序组织成可以继续修改的部件。

| 生成的墨线参考 | SVG 重建结果 |
| --- | --- |
| ![狗尾草生成墨线参考](https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@59f10882605358a124e987622d4a594c5ced800d/assets/examples/setaria-ink/generated-reference.png) | ![狗尾草 SVG 重建预览](https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@59f10882605358a124e987622d4a594c5ced800d/assets/examples/setaria-ink/rebuilt-preview.png) |

[下载重建 SVG](assets/examples/setaria-ink/setaria-viridis-rebuilt.svg) · [查看已发布素材 SVG](https://www.scansci.com/api/symbols/5651aa85-74a0-48a3-a1ca-0d9bef28f711/file?download=1) · [了解墨线图制作流程](skill/references/botanical-ink-reconstruction.md)

这也是一个仍可继续打磨的案例：重建后的叶片曲线和花序排列偏规整，与参考图存在可见差异；网站发布版经过精简，局部曲线也有变化。两图均为 AI 辅助插画，尚未经过分类学专家审定。形态参考包括 [Flora of New Zealand](https://www.nzflora.info/factsheet/taxon/Setaria-viridis.html)。

普通植物黑白线稿也有独立的[使用说明](skill/references/botanical-line-art.md)。提出“墨线图”时，作品名称和投稿标签会保留这一风格名称。

## 第一版之后，继续把它改到合用

一次对话可以持续围绕同一张图推进。你可以指出具体部位，也可以逐步把用途说得更清楚：

> 把根系标注改成中英双语。

> 再做一版突出根系的配色，保持原来的姿态。

> 把两版并排，统一标题和间距，导出论文用 PDF。

修改会沿用已有源稿和部件组织。涉及标签、引线或相接的器官时，一起核对它们的位置与连接。你也可以指定 Illustrator、Inkscape 或 PowerPoint 等后续使用环境，让检查围绕实际用途展开。

## 从现成素材开始，也把作品分享出去

[ScanSci 科研素材库](https://www.scansci.com/symbols/)提供按对象浏览、搜索和下载的入口。你可以先找接近需求的素材，再让 Agent 修改或组合。

仓库也附有植物、动物、环境和仪器等 SVG 素材，以及可复用的自然插画与场景。点击下图可以打开源文件。

<table>
  <tr>
    <td align="center" width="33%"><a href="https://github.com/Rimagination/scansci-svg/blob/main/skill/assets/library/animal_bird.svg"><img src="https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@59f10882605358a124e987622d4a594c5ced800d/assets/examples/gallery/animal-bird.png" height="230" alt="枝上鸣禽 SVG"></a><br>枝上鸣禽</td>
    <td align="center" width="33%"><a href="https://github.com/Rimagination/scansci-svg/blob/main/skill/assets/plants/whole-maize.svg"><img src="https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@59f10882605358a124e987622d4a594c5ced800d/assets/examples/gallery/whole-maize.png" height="230" alt="玉米全株 SVG"></a><br>玉米全株</td>
    <td align="center" width="33%"><a href="https://github.com/Rimagination/scansci-svg/blob/main/skill/assets/library/animal_bony_fish.svg"><img src="https://cdn.jsdelivr.net/gh/Rimagination/scansci-svg@59f10882605358a124e987622d4a594c5ced800d/assets/examples/gallery/animal-bony-fish.png" height="230" alt="硬骨鱼 SVG"></a><br>硬骨鱼</td>
  </tr>
</table>

[按类别找素材](skill/references/taxonomy.md) · [全株植物](skill/assets/plants/catalog.json) · [自然插画](skill/assets/nature/catalog.json)

作品完成后，可以继续说：

> 把这幅墨线图上传到 ScanSci，署名和许可沿用我已确认的设置。

Agent 会根据你的明确指令准备投稿，并返回网站实际给出的发布或审核状态。素材网站由独立项目维护，账号、许可选择和投稿规则以网站当前服务为准。

## 使用前，了解这几点

绘图效果取决于模型的观察与构形能力、参考资料，以及后续核对。**推荐使用 GPT-6 Astra**；宿主需要支持看图、读写文件和预览，先生图后重建还需要图像生成能力。

用于物种鉴别、分类学发表或其他正式科研表达时，请结合原始材料审定关键特征。可编辑性、视觉还原和科学准确性都需要各自核对；提供更清晰的参考与具体反馈，有助于持续改进结果。

默认交付 SVG 和预览图。PPTX、动画及其他格式按任务调用当前环境的工具；目标软件中的字体和显示效果，需要在相应软件中确认。

<a id="installation"></a>

## 安装

优先使用上面的对话安装方式。手动安装时，将本仓库的 `skill/` 目录安装为宿主可识别的 `scansci-svg` skill，再重新加载技能列表。

<details>
<summary>Windows · PowerShell 7</summary>

```powershell
git clone https://github.com/Rimagination/scansci-svg.git
cd scansci-svg
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
./sync.ps1 -Destination (Join-Path $skillRoot 'scansci-svg')
```

同步脚本会先备份已有安装，再复制更新。

</details>

<details>
<summary>macOS / Linux · Codex</summary>

```bash
git clone https://github.com/Rimagination/scansci-svg.git
cd scansci-svg
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/scansci-svg"
cp -R skill/. "${CODEX_HOME:-$HOME/.codex}/skills/scansci-svg/"
```

更新已有安装前，可先备份其中的个人修改。

</details>

## 需要进一步了解时

- [SVG 与格式转换](skill/references/svg-handbook.md)：查导出、兼容和显示问题。
- [文字与部件编辑](skill/references/editable-workflow.md)：了解还原图片和继续修改的方式。
- [组图与场景](skill/references/figure-composition.md) · [成套变体](skill/references/variation-and-learning.md)：把单图发展成一套图。
- [可编辑 PPTX](skill/references/pptx-delivery.md) · [绘制回放](skill/references/drawing-replay.md) · [科学过程动画](skill/references/scientific-animation.md)：用于演示和教学。
- [Skill 入口](skill/SKILL.md) · [效果评测记录](skill/references/evaluation.md)：供希望了解或参与维护的人阅读。

## 来源与许可

请按每件素材的声明使用和署名。标明 CC BY 4.0 的 ScanSci 素材须保留署名；本页狗尾草案例采用 CC-BY-4.0，署名 ScanSci。参考文献、照片和风格参考的权利独立保留。

本仓库尚未指定覆盖全部文件的统一许可，具体来源与授权见对应素材记录。
