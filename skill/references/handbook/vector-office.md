# SVG 与矢量编辑器、PDF、Office 互转

官方资料核实日期：2026-09-12。下列菜单和命令是选路依据；除文末注明的本地案例外，各路线的当前文件仍需在目标应用验证。记录软件版本、操作系统和导入方式，避免把桌面版能力套用到网页版。

<a id="edit-levels"></a>
## 先确定需要保留什么

| 编辑目标 | 实际含义 | 一次有用的检查 |
| --- | --- | --- |
| 外观嵌入 | SVG 作为一个图形对象，可整体缩放、替换 | 看裁剪、透明区、字体和导出尺寸 |
| 矢量部件编辑 | 路径、色块、组能分别选择修改；文字可能已转轮廓 | 改一个部件的填色，检查邻近对象 |
| 原生对象与关系 | 目标软件的文本框、形状、连接器、组件或数据关系 | 改文字、移动关联对象，保存重开 |

同为矢量格式，数据模型也会变化。需要长期返修时同时保留原 SVG、场景配方和目标应用原稿。具体操作验收复用 [目标编辑器交付](../editable-workflow.md#目标编辑器交付)。以下“典型损失”用于选择转换参数和定位差异，不要求每张简单图都跑完整检查表。

<a id="pdf"></a>
## SVG ↔ PDF

**SVG → PDF：** Inkscape 的 PDF 导出适合静态科研图；Illustrator 可另存 PDF。先确定纸张／绘图边界、物理尺寸和文本是否继续编辑。Inkscape 可选择保留文本或导出时转路径；过滤器效果可能局部栅格化。`--export-ignore-filters` 会省去过滤器效果，应在用户接受外观变化时采用。[Inkscape 导出参数](https://inkscape.org/fr/doc/inkscape-man-1.2.x.html)

常规自包含静态图也可直接用已安装的 CairoSVG 输出 PDF，按实际需要设物理尺寸。2026-09-12 本地 `lab_vessels.svg` 案例通过 CairoSVG 2.9.0 导出 180 × 144 mm PDF：12 条矢量绘制记录、0 个图像对象，透明区域和独立渲染对照通过；该样例不含文字与滤镜。[CairoSVG 输出能力](https://cairosvg.org/documentation/)

**PDF → SVG：** 在 Inkscape 导入指定页后另存 SVG；优先比较当前版本提供的导入方式。官方文档记录的 Poppler/Cairo 路线会将文字作为字形路径导入。PDF 原有路径、图像和部分文本可以转移；原 SVG 的 ID、语义组、源图表数据通常需要重新组织。扫描 PDF 应转入图片重建任务，PDF 导入本身只会得到已有像素内容。[Inkscape PDF 导入与 CLI](https://wiki.inkscape.org/wiki/Using_the_Command_Line)

文档命令模板，执行前以已安装版本的 `--help` 核对；使用新的输出路径：

```sh
inkscape input.svg --export-area-page --export-filename=figure.pdf
inkscape input.pdf --pdf-page=1 --export-type=svg --export-filename=page-1.svg
```

**保留与验证：** 对齐同一页框检查透明叠色、裁切、细线、公式和字体；需要可编辑文字时实际改一处。PDF 内能选中文字也需检查是否被拆成许多字形定位片段。SVG 动画、脚本和交互状态按选定静态状态交付。

箭头变黑时检查 marker 的上下文颜色与导出器实现；已有 [CairoSVG 彩色箭头恢复案例](rendering-compatibility.md#context-paint-recovery)，按每条连线分别落实颜色，保持路径、文字及原稿。

<a id="eps-ps"></a>
## SVG ↔ EPS／PS

**SVG → EPS／PS：** 用 Inkscape 导出或 Illustrator 的 EPS 保存入口；适合对接明确要求 PostScript 的排版链。路径和基本填色可保留，透明度、模糊等特性可能转成位图或被拼合；EPS 的边界框还可能改变留白。文字转轮廓可减少字体依赖，同时失去文本编辑。[Inkscape PS／EPS 选项](https://inkscape.org/fr/doc/inkscape-man-1.2.x.html)、[Illustrator 保存格式](https://helpx.adobe.com/illustrator/using/saving-artwork.html)

**EPS／PS → SVG：** 可用 Ghostscript 的 `pdfwrite` 先生成 PDF，再按上一节导入 SVG；先确认本机可用解释器。这个中间过程重组页面绘制指令，原始对象组织和非绘制信息可能丢失。对已经混入位图的 EPS，转换保持的是已有内容。[Ghostscript 高级输出设备](https://ghostscript.readthedocs.io/en/latest/VectorDevices.html)

**验证：** 检查边界框、透明对象交叠处、字体替代、曲线细节和混合位图分辨率。若接收方同时接受 PDF，用同一代表性图比较两种输出后选定路径。

<a id="illustrator"></a>
## SVG ↔ AI／Adobe Illustrator

**SVG → AI：** 在 Illustrator 中打开 SVG，检查图层和文字，再另存 `.ai`。目标是原生编辑时使用“打开”；置入图像的编辑范围需根据链接／嵌入状态另查。保存成 AI 后仍要确认关键对象已成为可选部件。

**AI → SVG：** 保留 AI 主稿，使用 SVG 保存或导出入口生成交换副本。基本路径、组、填色可迁移；网格、部分效果可能栅格化。需要文字可改时选文本输出，需要统一字形外观时选轮廓输出。`Preserve Illustrator Editing Capabilities` 会在 SVG 中嵌入 AI 数据；官方明确指出，直接修改 SVG 代码后，Illustrator 再打开可能读取旧 AI 部分。代码持续编辑的交付应检查并处理这项选项。[Adobe 保存与 SVG 选项](https://helpx.adobe.com/illustrator/using/saving-artwork.html)

**验证：** 在 Illustrator 中改文字、移动一个语义组，保存重开，再在浏览器查看交换 SVG。关注文字度量、剪切蒙版、混合／渐变效果和意外 `<image>`。批量处理使用实际安装版本支持的自动化接口；先跑一张代表图确认效果。

<a id="figma"></a>
## SVG ↔ Figma Design

**SVG → Figma：** 从支持的编辑器复制为 SVG，粘贴到 Figma 画布；也可使用当前界面的矢量导入入口。官方说明 `marker`、`pattern` 不包含在这条 SVG 导入中：科研箭头和图案填充应在交换副本中展开为普通几何，并检查引用坐标。[Figma 跨工具复制](https://help.figma.com/hc/en-us/articles/360040030374-Copy-assets-between-design-tools)

**Figma → SVG：** 选中图层／Frame，在 Export 中选择 SVG，或 `Copy/Paste as → Copy as SVG`。要保留文字编辑，关闭默认的 `Outline text`；需要可定位名称时开启 `Include id attribute`。描边可能展开为填充，内外描边的 `Simplify stroke` 也会改变表达。[Figma SVG 导出设置](https://help.figma.com/hc/en-us/articles/13402894554519-Export-formats-and-settings-for-static-designs)

**保留与验证：** 主要矢量轮廓和层叠适合交换；组件实例、Auto Layout、原型交互和变量绑定要保留在 Figma 文件中。导入后试改文字，核对箭头、填充图案、蒙版和渐变；再导出的 SVG 检查名称冲突、文字元素与画布范围。当前 skill 的配方关系仍由配方驱动，不能据静态 SVG 导入推定 Figma 原生约束已建立。

<a id="pptx"></a>
## SVG ↔ PPTX／PowerPoint

**SVG → PPTX 的两种交付：** 只需整图展示时 `插入 → 图片`；需要拆分部件时，可在支持的 Office 中使用 `Convert to Shape`。微软对逐部件填色转换明确提示使用 Windows 版 Microsoft 365，其他平台先检查实际入口。SVG 图片本身也能缩放、调整整体样式。[Microsoft 365 SVG 编辑](https://support.microsoft.com/en-us/office/graphics-visuals/edit-svg-images-in-microsoft-365)

科研图需要文本框、分组自由形状等原生对象时，复用 [PPTX 交付流程](../pptx-delivery.md) 中已有导出器和实际 PowerPoint 检查。SVG 中画出的箭头导出为自由形状后，连接语义需另外建立；分组名称和自定义 ID 也以导出结果为准。

**PPTX → SVG：** 单个形状／图组可右键 `另存为图片 → SVG`；官方记录该选项用于 Microsoft 365 1909 及以后版本，也列出 Office LTSC／2021。整页 SVG 导出见 Windows 的另存单页流程；macOS 菜单和支持格式按实机确认。[对象另存为图片](https://support.microsoft.com/office/save-a-picture-or-other-graphic-as-a-separate-file-3c4f9ca4-945a-4c33-af91-d10e4e3ea715)、[幻灯片导出](https://support.microsoft.com/en-us/powerpoint/save-a-slide-as-an-image-or-as-a-separate-presentation-file)

**保留与验证：** 页面可见内容可转移；动画、备注、母版关系、SmartArt 和图表数据另随 PPTX 保留。重点看嵌套视口、复合变换、渐变、裁剪与字体。实际改一段文本，移动一个多成员对象并保存重开；包内存在形状只能证明结构，视觉对照仍需执行。

<a id="docx"></a>
## SVG ↔ DOCX／Word

**SVG → DOCX：** 用 Word `插入 → 图片` 放入 SVG，适合论文插图和报告。可保留缩放后的矢量显示，编辑范围默认是图形对象。需要论文正文可编辑的图注、编号和交叉引用时，在 Word 中另设对应原生文字；逐部件图形编辑沿用 Office 的目标版本转换能力。[Microsoft 365 SVG 插入与编辑](https://support.microsoft.com/en-us/office/graphics-visuals/edit-svg-images-in-microsoft-365)

**DOCX → SVG：** 对选中的图片／图形使用支持版本的 `另存为图片 → SVG`。要转换完整排版页时，先输出 PDF，再按页处理；正文段落、表格结构、域和自动编号将成为页面视觉表达，继续排版仍用 DOCX。[Word 对象导出](https://support.microsoft.com/office/save-a-picture-or-other-graphic-as-a-separate-file-3c4f9ca4-945a-4c33-af91-d10e4e3ea715)

**验证：** 检查插图的实际厘米尺寸、环绕位置、分页和 PDF 打印结果；对字体及透明度做代表性对照。文字已经轮廓化时按路径编辑，若需修改词句则恢复独立文本。

<a id="visio"></a>
## SVG ↔ Visio VSDX／VDX

**SVG → VSDX：** 桌面 Visio `文件 → 打开` 支持 SVG／SVGZ，或插入已有图形后保存为 VSDX。微软说明多数导入图形显示为图元文件；导入成功只确认图形内容进入文档。目标是流程节点、可吸附连接器或 Shape Data 时，按图意建立原生形状和关系。[Visio 图形导入](https://support.microsoft.com/en-US/Visio/import-or-insert-graphics-into-visio-drawings)

**VSDX／可打开的旧 VDX → SVG：** 在桌面 Visio 打开源文件，通过 `文件 → 导出 → 更改文件类型 → SVG` 输出可见页面。当前官方网页版说明列出 PDF、PNG、JPEG，SVG 路线采用桌面版。[Visio 图形导出](https://support.microsoft.com/en-US/Visio/save-a-visio-diagram-as-a-graphic-or-image-file)

**VDX 方向：** VDX 是旧式独立 XML 绘图格式；Visio 2013 起使用基于 OPC 的 VSDX。两者扩展名和封装不可互换。用户指定 VDX 时，确认目标旧版本或已有转换器确实支持写出 VDX；现有文档依据不足以把当前 Visio 的 VDX 保存列为通用能力。[微软 VSDX 格式说明](https://learn.microsoft.com/zh-cn/office/client-developer/visio/introduction-to-the-visio-file-formatvsdx)

**验证：** 对比页尺寸、文字、箭头和分组；原生编辑另检查移动节点后连接器是否跟随、Shape Data 是否存在。导出的普通 SVG 适合视觉交换，Visio 母版、ShapeSheet 公式及连接关系保留在原文件。

<a id="metafile-odg"></a>
## SVG ↔ EMF／WMF／ODG

**SVG ↔ EMF／WMF：** Inkscape 文档列出这两种输出类型；用本机文件过滤器确认反向导入后另存 SVG。它们记录绘制指令，也能含位图；基本轮廓、填色和文字能否保留取决于实际记录和导入器。用于旧 Office／Windows 工作流时先用含文字、透明度和曲线的小样验证，重点看字体替代、渐变、描边和边界框。[Inkscape 输出类型](https://wiki.inkscape.org/wiki/Using_the_Command_Line)、[LibreOffice 图元格式实现说明](https://dev.blog.documentfoundation.org/2022/04/26/supporting-metafile-formats-wmf-emf-emfplus/)

**SVG → ODG：** 在 LibreOffice Draw 插入 SVG，保存 ODG。插入的图形可整体移动；需要内部编辑时，在副本检查 `Shape → Break` 对当前输入是否可用及结果，再重建必要的文本与组。**ODG → SVG：** 用 Draw `文件 → 导出`，按目标选择整页或 Selection；该版导出列表须包含 SVG。[Draw 26.2 导入与导出](https://books.libreoffice.org/en/DG262/DG26206-EditingImages.html)

**保留与验证：** ODG 保留 Draw 工作结构；交换 SVG 后核对可见对象、文字、分组和选区边界。链接插入要随源文件保持路径，独立交付可使用嵌入。滤镜列表中列有 VDX／VSDX 等导入格式，不等于同名格式支持导出。[LibreOffice 格式过滤器表](https://help.libreoffice.org/latest/en-US/text/shared/guide/convertfilters.html)

<a id="evidence"></a>
## 已有实测如何使用

2026-09-10 本地番茄案例已通过 SVG → 原生 PPTX → PowerPoint 编辑／保存重开：3110 个原生形状或文本、745 个组、0 个图片对象。首次导出的复合变换造成错位，修复导出副本后视觉检查通过；这一结果只覆盖该案例及其变换范围。具体修复办法沉淀于 [PPTX 保真与操作验证](../pptx-delivery.md#保真与操作验证)。

2026-09-12 的场景配方联动验证发生在 SVG 重新生成阶段；它为跨格式关系映射提供明确端点来源，尚不能作为 PowerPoint／Visio 原生连接器通过验证的证据。交付记录分别写明：生成了什么、目标应用中实际操作了什么、哪些关系仍依赖配方。
