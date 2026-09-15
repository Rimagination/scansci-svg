# SVG 百科与格式转换手册

更新与官方资料核实：**2026-09-12**。面向绘制、修改、排错和格式选择；按问题读取相关条目。每篇提供原理、操作入口、保留信息、典型变化与验证办法，来源链接放在对应说明附近。

目录：[按问题查](#lookup) · [转换速查](#conversion-map) · [实际执行](#choose) · [失真与工具缺失](#recover) · [现有工具](#tools) · [扩充条目](#maintain)

<a id="lookup"></a>
## 按问题查

| 主题 | 常见问题与查询入口 |
| --- | --- |
| **结构与几何** | [viewBox、单位、矩阵](handbook/svg-core.md#coordinates) · [路径、曲线、孔洞](handbook/svg-core.md#paths) · [描边和箭头](handbook/svg-core.md#paint) · [defs / use / 裁剪 / 蒙版](handbook/svg-core.md#reusable) · [文字与无障碍](handbook/svg-core.md#text) |
| **渲染与兼容** | [跨应用交换](handbook/rendering-compatibility.md#profiles) · [字体和样式](handbook/rendering-compatibility.md#portable) · [精度与尺寸](handbook/rendering-compatibility.md#precision) · [透明与滤镜](handbook/rendering-compatibility.md#effects) · [故障排查表](handbook/rendering-compatibility.md#troubleshooting) |
| **矢量编辑与办公** | [PDF](handbook/vector-office.md#pdf) · [EPS / PS](handbook/vector-office.md#eps-ps) · [Illustrator / AI](handbook/vector-office.md#illustrator) · [Figma](handbook/vector-office.md#figma) · [PPTX](handbook/vector-office.md#pptx) · [Word](handbook/vector-office.md#docx) · [Visio](handbook/vector-office.md#visio) · [EMF / WMF / ODG](handbook/vector-office.md#metafile-odg) |
| **位图与动画** | [图片转矢量](handbook/raster-motion.md#raster-to-svg) · [PNG / JPEG / WebP / AVIF / TIFF](handbook/raster-motion.md#svg-to-raster) · [DPI](handbook/raster-motion.md#size-dpi) · [GIF / MP4 / WebM](handbook/raster-motion.md#animation-video) · [HTML / Canvas](handbook/raster-motion.md#html-canvas) · [SVGZ / 优化](handbook/raster-motion.md#svgz-optimization) |
| **CAD 与制作** | [DXF / DWG](handbook/cad-manufacturing.md#cad) · [切割 / 绘图机 / G-code](handbook/cad-manufacturing.md#toolpaths) · [Blender / STL](handbook/cad-manufacturing.md#three-d) · [刺绣 DST / PES](handbook/cad-manufacturing.md#embroidery) |
| **代码与数据** | [Python / R](handbook/code-and-data.md#plots) · [Mermaid / Graphviz](handbook/code-and-data.md#diagrams) · [LaTeX / TikZ](handbook/code-and-data.md#latex) · [GeoJSON / GIS](handbook/code-and-data.md#gis) · [HTML / React](handbook/code-and-data.md#web) · [恢复数据与语义](handbook/code-and-data.md#recovery) |

绘图判断继续使用既有专题：[参考图还原与精细临摹](editable-workflow.md) · [形态与结构依据](morphology-evidence.md) · [素材类别](taxonomy.md) · [场景与组图](figure-composition.md) · [成套变体](variation-and-learning.md)。

<a id="conversion-map"></a>
## 转换速查：源 → 目标

每个方向独立判断。**实测流程**表示项目已有相应案例或工具检查；**官方路线**表示有文档依据，实际软件和当前文件需验证；**重建路线**表示还要补充语义、数据或工艺。具体范围见链接条目，同一路线的不同输入可能需要不同处理。

| 源 → 目标 | 首选入口 | 要保留或补充什么 | 依据 |
| --- | --- | --- | --- |
| PNG / JPEG 等 → 可编辑 SVG | [描摹、重建或局部混合](handbook/raster-motion.md#raster-to-svg) | 文字恢复、完整部件与关系，清理来源噪声 | 实测流程＋重建 |
| SVG → PNG / JPEG / WebP / AVIF / TIFF | [匹配输入的渲染器＋编码器](handbook/raster-motion.md#svg-to-raster) | 像素宽高、背景、字体、颜色与投稿要求 | PNG 简单路径已有实测；其余按官方路线 |
| SVG → PDF | [CairoSVG / Inkscape / Illustrator](handbook/vector-office.md#pdf) | 页框、文字、透明效果和物理尺寸 | CairoSVG 简单路径已有实测；其余按官方路线 |
| PDF → SVG | [逐页导入](handbook/vector-office.md#pdf) | 区分扫描页和矢量页，整理文字及对象 | 官方路线＋重建 |
| SVG → EPS / PS | [对应静态导出](handbook/vector-office.md#eps-ps) | 透明与滤镜处理、边界框、字体 | 官方路线 |
| EPS / PS → SVG | [PDF 中间格式](handbook/vector-office.md#eps-ps) | 保留绘制外观，重新检查对象组织 | 官方路线 |
| SVG ↔ AI / Figma | [目标编辑器打开与导出](handbook/vector-office.md#illustrator) · [Figma](handbook/vector-office.md#figma) | 文字、蒙版、标记与应用私有结构 | 官方路线 |
| SVG → 原生可编辑 PPTX | [现有原生形状导出器](pptx-delivery.md) | 文本框、形状和组；连接器关系另外处理 | 实测流程，见限定案例 |
| SVG → Office 中整图展示 | [插入 SVG 图形](handbook/vector-office.md#pptx) | 整图外观、缩放和字体 | 官方路线 |
| PPTX / DOCX → SVG | [对象导出或逐页转换](handbook/vector-office.md#pptx) · [Word](handbook/vector-office.md#docx) | 页内可见内容；原生数据和排版留在源文件 | 官方路线 |
| SVG ↔ Visio VSDX；旧 VDX → SVG | [桌面导入导出与原生重建](handbook/vector-office.md#visio) | 节点、连接器和 Shape Data；写出旧 VDX 另核实目标版本/工具 | 官方路线＋重建 |
| SVG ↔ EMF / WMF / ODG | [实际安装的格式过滤器](handbook/vector-office.md#metafile-odg) | 图元、文字与当前应用支持范围 | 官方路线 |
| SVG → GIF / MP4 绘制回放 | [现有回放工具](drawing-replay.md) | 编排步骤、时长、分辨率和背景 | 实测流程 |
| SVG → 科学过程动画 | [部件时间线](scientific-animation.md) | 确认机制、对象行为与时间含义 | 实测流程＋编排 |
| 已有 SVG 动画 → 视频 / WebM | [按宿主采帧后编码](handbook/raster-motion.md#animation-video) | 动画时钟、资源与 alpha 支持 | 官方路线；需编排采帧 |
| GIF / 视频 → SVG | [选择帧后重建](handbook/raster-motion.md#raster-to-svg) | 静态帧或动态图形的目标范围、对象与时间线 | 重建路线 |
| SVG ↔ SVGZ | [gzip 压缩或解压](handbook/raster-motion.md#svgz-optimization) | 保留 XML；确认分发和编辑器支持 | 官方路线 |
| SVG ↔ HTML / React | [内联、组件化或提取](handbook/code-and-data.md#web) | 样式、资源、实例 ID；交互代码单独保留 | 官方路线＋整理 |
| Canvas → SVG | [绘图库原生输出或像素重建](handbook/raster-motion.md#html-canvas) | 有无原始场景树与绘制数据 | 按输入选路 |
| SVG ↔ DXF；涉及 DWG | [二维 CAD 交换](handbook/cad-manufacturing.md#cad) | 物理单位、曲线、闭合轮廓和约束 | 官方路线＋CAD 整理 |
| SVG → 切割 / 走针 / 简单 STL | [已有制作工具](fabrication-and-layers.md) | 毫米尺寸、拓扑、针法或厚度 | 实测范围有限，见条目 |
| SVG → G-code | [设备对应 CAM](handbook/cad-manufacturing.md#toolpaths) | 机器、工艺、刀具与后处理器 | 工艺路线 |
| SVG ↔ 三维视图 | [平面曲线建模或指定投影](handbook/cad-manufacturing.md#three-d) | 厚度、隐藏结构、相机与剖面 | 官方导入＋建模 |
| Matplotlib / ggplot2 → SVG | [原始绘图脚本导出](handbook/code-and-data.md#plots) | 文本、单位、图像面板与原始数据 | Matplotlib 标签已有实测；R 按官方路线 |
| Mermaid / DOT ↔ SVG | [原生导出或关系恢复](handbook/code-and-data.md#diagrams) | 节点边与标签；逆向核对拓扑 | 官方导出＋重建 |
| TeX / TikZ ↔ SVG | [PDF / DVI 中间格式](handbook/code-and-data.md#latex) | 字形、公式源、布局；逆向恢复参数 | 官方导出＋重建 |
| GeoJSON / GIS ↔ SVG | [地图导出或坐标标定](handbook/code-and-data.md#gis) | CRS、地图框、比例和要素属性 | 官方导出＋数据重建 |

<a id="choose"></a>
## 从用户要求执行到目标文件

先读当前文件与已确认要求，确定**实际源内容 → 目标应用/格式 → 要进行的编辑**。例如“在 PowerPoint 中改单片叶子的颜色”需要部件级形状，“在 Word 放一张插图”通常只需整图展示。原始绘图代码或数据存在时优先从源导出；已有矢量对象直接复用，扫描页或像素图再进行重建。

只补会改变结果的缺项。“转成可编辑文件”需确定目标软件及要改的内容；“导出宽 2400 像素的透明 PNG”已有足够信息，保持原比例直接执行。文件能查出的字体、尺寸、图像/矢量组成、页数和资源依赖先自行检查。

选择满足目标的最短可行链：复用已知可用环境，必要时查看相关工具版本与参数；仅探测当前路线需要的工具。涉及软件更新、插件或投稿要求时，核实对应官方文档。使用输出副本，按实际需要处理字体、变换、裁剪和分组，然后调用工具生成文件。

在交付目标中验收本题要求：PNG 检查实际像素和 alpha；PDF 检查页框、文字及矢量内容；原生编辑文件完成一次指定修改并保存重开；CAD 检查已知物理尺寸和拓扑；视频检查关键状态与播放。明确的遗漏、乱码或错位进入下节修复。结构检查和实际渲染各验证其对应范围，[具体方法](handbook/rendering-compatibility.md#verification) 随任务启用。

完成后交付所需文件及适用的预览，简述实际检查与剩余差异。用户明确只要目标格式时按该要求交付。仅询问知识时解释核心区别和适用路径，无需生成文件。

<a id="recover"></a>
## 转换失真或工具缺失时怎样继续

| 实际情况 | 下一步动作 | 保留的完成条件 |
| --- | --- | --- |
| 首选程序未安装 | 查找宿主其他可用渲染器、目标应用或原生导出接口；只尝试能满足当前要求的候选 | 例如透明 PNG 的替代仍保留透明及指定尺寸 |
| 原生导出器缺少某项支持 | 在副本中整理该项结构，或用现有目标格式库表达所需对象；简单适配按当前输入实现 | 文字、部件与关系按用户指定粒度继续可编辑 |
| 文件生成了但缺字、错位、裁剪错误 | 定位字体、矩阵、引用或导出选项，修复原因后重导并检查受影响区域 | 当前输出恢复应有的内容与位置 |
| 全图基本正确、局部复杂效果失真 | 处理对应效果或局部重建，保留已正确内容；需要改变编辑粒度或图意时确认具体取舍 | 外观与编辑能力的变化由当前用途决定 |
| 输入缺少隐藏结构、原始数据或地理参考 | 先查已给资料与源文件；缺项影响目标时向用户索取具体信息，同时完成独立部分 | 重建内容有依据，来源和估计信息可区分 |
| 替代路线会损失用户明确要求 | 说明具体影响并请求相关选择；继续完成不依赖该选择的部分 | 部件编辑、透明、尺寸等明确要求得到保留或重新确认 |

失败后用日志和实际产物区分问题发生在输入、工具调用、转换还是验证环节。没有新依据时不重复同一失败命令；修复后只复查受影响内容。安装、授权或外部服务仅在当前任务确有需要且得到相应授权时进行。

能修复或用等价路线继续时完成目标。确有环境/信息阻塞时，交付已经完成的部分，明确尚缺的目标文件或能力及下一项必要动作；把这次结果记录为部分完成。目标文件实际生成且任务对应检查通过后，再报告该转换完成。

<a id="tools"></a>
## 哪些已有工具可以直接接着用

| 动作 | 现有入口与使用说明 |
| --- | --- |
| 描摹轮廓 | [trace_svg.py](../scripts/trace_svg.py) · [描摹整理](editable-workflow.md#描摹与部件整理) |
| 检索组件、复用素材、重排关联场景 | [compose_scene.py](../scripts/compose_scene.py) · [场景配方](figure-composition.md#用素材库组织场景) |
| 批量拼版、部件修改 | [compose_svg.py](../scripts/compose_svg.py) · [edit_svg.py](../scripts/edit_svg.py) · [修改说明](editable-workflow.md#按部件执行修改) |
| 原生 PPTX | [PPTX 流程](pptx-delivery.md)，运行环境需有其中指定的外部导出器 |
| 绘制回放、过程动画 | [回放](drawing-replay.md) · [机制时间线](scientific-animation.md) |
| 制作路径与几何 | [路径提取、刺绣及有限 STL](fabrication-and-layers.md) |

条目中列出的外部软件按实际安装情况使用。新增格式首先寻找该软件现有导入导出器；确需补代码时只补当前任务缺少的一段，并用真实输入验证。

<a id="maintain"></a>
## 如何继续扩充百科

遇到新问题先搜索已有条目，仅加载相关章节。可用 `rg -n "关键词" <skill目录>/references/handbook` 定位；格式名、软件名、症状都可作为入口。

新知识归入相应专题，保留六项：**问题/方向、保留目标、适用条件、工具与步骤、实际变化和验证、官方来源与核实日期**。实际跑通后补软件版本、输入特征、关键选项和验收结果；只核对过文档时标为官方路线。小案例足够说明问题时直接留在条目，无需另建工具或索引系统。

改动某一目标格式时同步更新速查表和对应条目，保留其他已有效内容。长期按真实转换失败、用户编辑需求和新软件支持补充。
