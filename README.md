# scansci-svg

从文字、照片和示意图创作可编辑的科研 SVG，支持科学结构核对、整图语义重建、部件修改及可编辑 PPTX 交付。

> **强烈推荐使用 GPT-6 Astra。** 其他模型的成图质量可能大打折扣，尤其是复杂生物形态、自然轮廓、部件连接和局部重绘。本项目将 GPT-6 Astra 作为优先推荐配置。

[在线素材库](https://www.scansci.com/symbols/) · [Skill 入口](skill/SKILL.md) · [完整分类索引](skill/references/taxonomy.md)

## 能做什么

- **文字绘图**：按描述直接构造 SVG，结合需要核对物种形态、结构及机制关系。
- **图片转绘**：理解整张图的对象与关系，再重建路径、文字和叠放顺序。
- **部件编辑**：按根、茎、叶、花，或头、翼、足等编辑意图组织具名分组。
- **局部重绘**：修正轮廓、接合、比例与残留杂色，保留正确区域。
- **可编辑 PPTX**：复用宿主可用的原生形状导出工具，检查文字和部件编辑；具体依赖见 [PPTX 交付](skill/references/pptx-delivery.md)。

类别参考覆盖 **16 个主题领域、149 个 SVG 子类**。仓库包含 149 件分类代表图、10 件全株植物及7件重绘基础素材，另有鸟类和部件编辑范例。在线素材库按对象重新归类，便于浏览与搜索。

## 素材预览

| 枝上鸣禽 | 支柱根型红树 | 硬骨鱼 |
| --- | --- | --- |
| ![枝上鸣禽](skill/assets/library/animal_bird.svg) | ![支柱根型红树](skill/assets/library/plant_mangrove.svg) | ![硬骨鱼](skill/assets/library/animal_bony_fish.svg) |

## 安装

下载本仓库，将 `skill/` 目录的内容放入宿主的 `skills/scansci-svg/`，确保最终入口为 `skills/scansci-svg/SKILL.md`。

```bash
git clone https://github.com/Rimagination/scansci-svg.git
cd scansci-svg
```

Codex 用户可使用下列方式安装。设置了 `CODEX_HOME` 时使用该目录，否则使用用户目录下的 `.codex`。

**Windows · PowerShell 7**

```powershell
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex/skills' }
./sync.ps1 -Destination (Join-Path $skillRoot 'scansci-svg')
```

同步脚本先备份已有安装，再复制更新；`-WhatIf` 可预览操作。

**macOS / Linux**

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills/scansci-svg"
cp -R skill/. "${CODEX_HOME:-$HOME/.codex}/skills/scansci-svg/"
```

安装后重新加载宿主的 skill 列表，并选择 **GPT-6 Astra**。

## 使用示例

```text
使用 $scansci-svg，画一株开花期水稻，根、茎、叶、穗分别可编辑。
```

```text
使用 $scansci-svg，把这张科研示意图重建为可编辑 SVG，保留文字和对象关系。
```

```text
使用 $scansci-svg，修正这只青蛙的后肢连接，保留身体、配色和整体姿态。
```

```text
使用 $scansci-svg，把这张图转成可编辑 PPTX，文字和主要部件能单独修改。
```

默认交付 SVG 和实际渲染预览。模型需要能读取参考图、写文件并查看渲染结果；PNG 渲染与 PPTX 导出按宿主现有工具使用。

## 仓库结构

```text
skill/SKILL.md       绘制与交付入口
skill/agents/        宿主界面元数据
skill/references/    形态证据、类别画法、编辑与交付参考
skill/assets/        可编辑 SVG 与教学范例
skill/scripts/       Python 结构和局部编辑检查器
skill/evals/         轻量评测题
sync.ps1             Windows 安装与更新脚本
```

检查器使用 Python 3 标准库：

```bash
python skill/scripts/check_svg.py skill/assets/library/animal_bird.svg
python skill/scripts/test_edit_scope.py
```

维护源码位于 `skill/`。个人照片、实验输出及安装备份保存在被 Git 忽略的 `.local/`。素材网站在独立的 [scansci-portal](https://github.com/Rimagination/scansci-portal) 项目维护。

## 来源与许可

来源信息随各素材和参考记录保留，鸟类生成范例附独立提示词及生成记录。标明 CC BY 4.0 的基础素材沿用该许可并署名 ScanSci；其余文件的使用授权以各自声明为准，本次发布未额外指定统一开源许可。
