# 位图、动画、网页宿主与压缩

核实日期：2026-09-12。按目标查阅：[位图转 SVG](#raster-to-svg)、[SVG 转位图](#svg-to-raster)、[尺寸与 DPI](#size-dpi)、[动画与视频](#animation-video)、[HTML / Canvas](#html-canvas)、[SVGZ 与优化](#svgz-optimization)。

“已有实测”指本项目已有功能记录；“官方路线”指已核对文档，执行时仍需确认目标环境、输入特征和产物。以下命令用于说明调用方法，本次文档整理未执行这些转换。`<skill目录>` 换成实际安装目录，输入使用工作副本，输出选择新文件或新目录。

<a id="raster-to-svg"></a>
## PNG / JPEG / WebP / AVIF / TIFF 怎样变成 SVG？

先明确需要保留什么：原始像素、可缩放轮廓，还是能够独立修改的对象与文字。三条路线对应不同结果：

| 路线 | 得到什么 | 适合什么需求 |
|---|---|---|
| 嵌入 `<image>` | SVG 容器里的位图，缩放仍受原像素限制 | 用照片作为底图，叠加可编辑标注；交付说明中列明位图部分 |
| 自动描摹 | 根据像素色块拟合的矢量路径 | 徽标、轮廓、扁平插画；精细区域可先描摹再修整 |
| 语义重建 | 对象、文字、连接和层次重新构形 | 科研机制图、需要改标签/器官/关系的图件 |

本 skill 的“图片转可编辑 SVG”默认依据编辑目标选择描摹、重建或局部混合。简单色面合并为干净形状；羽纹、花序等有辨识意义的细节保留。文字描摹得到字形路径，需要编辑文字时重新录入 `<text>`。处理选择见 [可编辑重建工作流](../editable-workflow.md)。

JPEG 压缩边缘、缩放锯齿和透明边缘的底色可能进入描摹结果；检查形态后再调整去斑点与颜色精度。WebP / AVIF 的解码能力取决于所用库的构建；TIFF 先选定页、通道与展示范围。多页、动画帧、高位深科学图像应保留原始数据，描摹产物作为插图使用。Sharp 的输入支持及页面选择参数可用于准备单帧，实际支持以环境为准。[Sharp 输入文档](https://sharp.pixelplumbing.com/api-constructor/)

### 已有入口：VTracer 描摹

`scripts/trace_svg.py` 已使用 Pillow + VTracer 0.6.15 测过彩色透明孔洞、黑白透明底、EXIF 方向和既有文件保护。它生成整图或已分离区域的一个命名组，并给路径 ID；部件识别、OCR、遮挡后轮廓补全由后续重建处理。源代码：[trace_svg.py](../../scripts/trace_svg.py)；后端说明：[VTracer 官方项目](https://github.com/visioncortex/vtracer)。

```text
python <skill目录>/scripts/trace_svg.py input.png new-trace.svg --group-id flower --mode spline --filter-speckle 4
```

依赖在实际执行的 Python 环境中安装，脚本提示的已测版本为 `Pillow`、`vtracer==0.6.15`。输入须为可解码的单帧可见图像。`--group-id flower` 只命名输入区域；输入包含叶片时它们也在该组内。黑白模式会先合成白底，以适配后端的 alpha 行为。返回的纯转换时间与准备、检查、写出时间分别记录；完整任务还包含模型判断和视觉返修。

<a id="svg-to-raster"></a>
## SVG 怎样输出 PNG / JPEG / WebP / AVIF / TIFF？

路线为：确定画幅与输出像素 → 用合适渲染器栅格化 → 编码目标格式 → 在最终尺寸看字、线和透明边缘。

| 目标 | 常见选择 | 交付重点 |
|---|---|---|
| PNG | 透明科研插图、无损预览 | 保留 alpha；缩小后检查细线和标签 |
| JPEG | 不透明照片式预览 | 先合成指定背景；文字线条检查压缩色边 |
| WebP | 网站缩略图、透明素材预览 | 按画质选择有损或无损；保留 SVG 编辑原件 |
| AVIF | 网站静态预览的压缩候选 | 比较实际画质、编码时间及目标软件支持 |
| TIFF | 期刊规定的位图交付 | 按投稿要求设置尺寸、位深、色彩与压缩，核对实际元数据 |

Sharp 可将 SVG 渲染后输出上述格式。JPEG 小字和彩色细线可评估 `chromaSubsampling: '4:4:4'`；TIFF 明确选 `lzw` 或 `deflate` 等压缩，避免依赖默认值；TIFF 后缀本身不说明采用无损编码。[Sharp 输出选项](https://sharp.pixelplumbing.com/api-output/) WebP 支持透明、有损、无损及动画，但仍是像素图像。[WebP 官方格式说明](https://developers.google.com/speed/webp/docs/riff_container)

静态、常规路径与文字可使用 CairoSVG；浏览器 CSS、复杂滤镜、字体排版应先比较目标渲染器的结果。CairoSVG 有滤镜、ICC、复杂文本和外部字体能力限制，不执行脚本或动画。[CairoSVG 功能范围](https://cairosvg.org/documentation/)

```text
cairosvg figure.svg --format png --output-width 2400 --output figure-2400.png
```

此示例需已安装 CairoSVG 及其本地依赖；SVG 有明确画幅，输出宽 2400 px，高度随原始比例。针对简单静态输入，这是官方命令路线，不能用它捕获 CSS / JS 动画某一时刻。[CairoSVG 命令文档](https://cairosvg.org/documentation/#command-line)

本地实测（2026-09-12）：`lab_vessels.svg` 经 CairoSVG 2.9.0 导出、用 Pillow 写入 300 PPI 元数据，得到宽 180 mm 对应的 2126 × 1701 px RGBA PNG；尺寸、实际 pHYs 和透明背景检查通过。该样例覆盖简单静态路径及页面透明，字体、滤镜等按输入另验。

<a id="size-dpi"></a>
## 像素尺寸、物理尺寸与 DPI 怎么对应？

- `viewBox` 定义内部坐标范围；输出像素决定栅格图细节容量。物理宽度换算：`像素宽 = 毫米宽 ÷ 25.4 × PPI`。例如 180 mm、300 PPI 约为 2126 px；这是换算例，投稿阈值按实际要求。
- CSS 绝对单位采用 `1in = 96px`；这个比例不代表交付 PNG 必须是 96 PPI。[SVG 坐标与单位](https://www.w3.org/TR/SVG2/coords.html#Units)
- 区分**输入渲染密度**与**输出分辨率元数据**。Sharp 构造参数 `density` 影响 SVG 渲染，文档默认 72；`withMetadata({density: 300})` 设置输出密度信息。只修改已有低分辨率位图的密度标签，像素细节不会增加。[Sharp 构造参数](https://sharp.pixelplumbing.com/api-constructor/)、[输出元数据](https://sharp.pixelplumbing.com/api-output/#withmetadata)
- `width="100%"` 等相对尺寸须给容器尺寸；同时硬设宽高时确认原比例及裁切方式，不能用拉伸补足版面。

**透明与背景：**透明像素没有固定白底。JPEG 或不透明视频先在明确背景上合成；仅移除 alpha 会丢失合成关系。Sharp 使用 `flatten({background: '#ffffff'})` 可指定白底。放到深色与浅色底各看一次，可发现白边、黑边和半透明遗漏。[Sharp flatten](https://sharp.pixelplumbing.com/api-operation/#flatten)

**字体与色彩：**导出前让目标渲染器获得实际字体，检查中文、上下标与换行；浏览器采帧需等字体就绪。SVG 编辑主文件保留文字，固定字形的交付副本才按需求转曲。网页预览通常采用 sRGB；印刷需要指定配置文件时走可管理 ICC 的工具链并核对颜色，改扩展名不完成色彩转换。Sharp 提供 ICC 保留/转换接口；其默认输出会转 sRGB 并移除元数据。[Sharp ICC 与元数据](https://sharp.pixelplumbing.com/api-output/#withiccprofile)

<a id="animation-video"></a>
## SVG 怎样生成 GIF / MP4 / WebM？

静态 SVG 只给出图形状态。要“从零画出来”或“水沿通路运动”，先建立步骤或时间线，再在固定时刻渲染为帧，最后编码。已有动画可能来自 SMIL、CSS 或 JavaScript，支持范围随宿主变化；采用实际播放宿主捕获。[SVG 动画方式](https://www.w3.org/TR/SVG2/animate.html)

本 skill 已有两条流程：

- [绘制回放](../drawing-replay.md)：线稿、固有色、细节与标注的制作展示；默认离散步骤，最后恢复完整成稿。根据成稿编排时称“重建回放”，真实操作记录另作来源。
- [科学过程动画](../scientific-animation.md)：按确认机制编排运输、旋转、平移等，保存时间线，说明数据时间或示意时间；末帧可以不同于源图。

```text
node <skill目录>/scripts/replay_svg.mjs figure.svg new-replay --style steps --format mp4
```

已有实现使用 Node.js、Playwright、Chromium 和 FFmpeg；当前格式为 `mp4|gif|both|html`，默认媒体宽 640 px、20 fps、9 秒、白底。HTML 交付保留内联 SVG 与播放器。脚本接受规范的静态自包含 SVG；已有 CSS / SMIL / JS 动画要先用其原宿主控制时间与取帧，不能直接套进此入口。源码：[replay_svg.mjs](../../scripts/replay_svg.mjs)。

捕获已有动画时固定浏览器、视口、像素比例、字体和资源；让各动画在同一时间基准上定位到 `t = 帧号 / fps`。CSS / Web Animations、SMIL 与自定义 JS 各自的时钟须一起控制；实际等待若受负载影响可能漏帧。检查起点、关键状态、终点及循环接缝，保存源文件与编排以便重做。

| 交付 | 建议与边界 |
|---|---|
| MP4 + H.264 | 常规播放候选；现有导出采用 `yuv420p`，透明背景须先合成，细彩线检查抽样后的画质 |
| GIF | 需要图片式循环时使用；调色板最多 256 色，半透明变为透明/不透明，渐变与细节可能出现抖动 |
| WebM + alpha | 网页透明动画候选；先保留透明帧，再选支持 alpha 的编码及播放器；此路线尚未接入现有回放 CLI |
| HTML + SVG | 需要播放控制、逐步查看、可缩放图形时使用；接收方需浏览器 |

GIF 的调色板与 alpha 阈值见 [FFmpeg palettegen / paletteuse](https://ffmpeg.org/ffmpeg-all.html#palettegen)。WebM alpha 有 Chrome 官方实现说明，该文为历史能力资料，目标浏览器及嵌入场景需实际播放确认。[Chrome WebM alpha](https://developer.chrome.com/blog/alpha-transparency-in-chrome-video/)

已有不透明、同尺寸且宽高均为偶数的 PNG 帧，从 `frame-00000.png` 连续编号，环境具有 `libx264` 时，可用以下官方参数路线编码：

```text
ffmpeg -n -framerate 20 -start_number 0 -i "frames/frame-%05d.png" -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -movflags +faststart replay.mp4
```

`-framerate` 决定输入帧的播放速度；`-crf` 控制编码质量，`-n` 保留既有输出。来源：[FFmpeg 图像序列](https://ffmpeg.org/ffmpeg-formats.html#image2)、[H.264 编码选项](https://ffmpeg.org/ffmpeg-codecs.html#libx264_002c-libx264rgb)。哪个更省空间应以同画幅、时长和可接受画质比较实际字节数；可从降低不必要的分辨率、帧率和时长入手，不承诺固定格式排名。

<a id="html-canvas"></a>
## HTML / Canvas 与 SVG 是什么关系？

HTML 可承载内联 SVG，并用 CSS / JS 控制布局和交互；保存独立 SVG 时把所需样式与资源落实到交付文件。Canvas 2D 的输出是位图，截图或 `toBlob()` 不携带器官分组、文字对象或原始绘制命令。若绘图库本身维护场景树并提供 SVG 导出，优先使用其原生导出；只有像素时回到本页的描摹或重建路线。[HTML Canvas 标准](https://html.spec.whatwg.org/multipage/canvas.html#the-canvas-element)

<a id="svgz-optimization"></a>
## SVGZ、gzip 与 SVG 优化怎么选？

SVGZ 是经过 gzip 压缩的 SVG 字节流，等同于 `.svg.gz`。它保留解压后的 XML 内容；缩小传输体积不减少路径数量和渲染成本。网页分发按服务器配置正确的 SVG 类型与压缩响应，编辑交付优先提供目标工具可打开的 SVG。[SVG MIME 注册](https://www.w3.org/TR/SVG2/mimereg.html)

结构优化另作用于发布副本：去掉冗余内容、适度减少数值精度，逐项看实际收益。稳定 ID、语义组、锚点元数据、`href` / `url()`、外部场景配方和回放时间线共同构成编辑关系。SVGO 的 `cleanupIds` 会删除未引用 ID、缩短被引用 ID，并提供 `preserve` / `preservePrefixes`；外部配方用到的 ID 可能在 SVG 内看似未引用，应显式保留或关闭该处理。[SVGO cleanupIds](https://svgo.dev/docs/plugins/cleanupIds/)

优化后检查实际渲染、一次目标编辑及受影响的连接/回放。相同外观不足以证明编辑关系仍在；保留可编辑主文件，将体积收益记录在发布副本上。
