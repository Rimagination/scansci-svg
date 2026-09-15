# SVG 与程序、数据图、地图及网页

资料核实：2026-09-12。目录：[Python / R](#plots) · [Mermaid / Graphviz](#diagrams) · [LaTeX / TikZ](#latex) · [GeoJSON / GIS](#gis) · [HTML / React](#web) · [反向恢复](#recovery)。

以下命令为官方文档用法，使用对应已安装工具执行；本次知识库整理未运行这些转换。输入数据与绘图代码保留为可更新源稿，SVG 用于展示、局部编辑和跨应用交换。

<a id="plots"></a>
## Python / R 数据图 → SVG

**Matplotlib：**直接从 figure 导出 SVG。需要标签保留为文字时设置 `svg.fonttype = 'none'`；默认 `path` 将字形写成路径，外观较少依赖目标字体。设为 `none` 后，在目标程序安装相应字体。[Matplotlib SVG 配置](https://matplotlib.org/stable/users/explain/customizing.html)

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['svg.fonttype'] = 'none'
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot([0, 1, 2], [1, 3, 2])
ax.set_xlabel('Time (h)')
fig.savefig('figure.svg', format='svg', bbox_inches='tight')
plt.close(fig)
```

`bbox_inches='tight'` 按内容收紧边界，严格版面尺寸时应决定是否使用。SVG 中的栅格化对象仍受分辨率影响；查看 `imshow`、复杂点阵或指定 rasterized 的 artist 是否产生 `<image>`。有真实图像数据的面板可保留像素，并在交付中明确。需要全矢量时按数据与展示目的选择矢量画法。[savefig 参数](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html)

**R / ggplot2：**`svglite` 将文字保留为 `<text>`，适合后续编辑。给 `ggsave` 指定设备和物理宽高，输出后核对实际字体、图例、线宽与裁剪。[svglite 文字输出](https://svglite.r-lib.org/)、[ggsave 参数](https://ggplot2.tidyverse.org/reference/ggsave.html)

```r
library(ggplot2)
p <- ggplot(mtcars, aes(wt, mpg)) + geom_point() + theme_classic()
ggsave("figure.svg", plot = p, device = svglite::svglite,
       width = 160, height = 100, units = "mm")
```

重复更新数据时修改原脚本；要与照片、器官或仪器组成复合图时，按 [科研组图](../figure-composition.md) 复用导出的 SVG，保持数据轴、数值与图例含义。图内识别出的路径数量不能替代数据点数量核验。

本地实测（2026-09-12）：Matplotlib 3.10.9 从五个示例数据点导出 SVG，设置 `svg.fonttype='none'` 后保留 18 个 `<text>`、0 个图像对象；包含 μ 的标签及实际渲染通过检查。此项验证源导出与 SVG 文本结构，目标编辑器内的操作另验。

<a id="diagrams"></a>
## Mermaid / Graphviz → SVG；SVG → 图描述

已有流程或网络描述时使用其原生布局器：

```sh
mmdc -i workflow.mmd -o workflow.svg
dot -Tsvg network.dot -o network.svg
```

第一条需要 Mermaid CLI 及其浏览器环境；第二条需要 Graphviz。流程节点和边来自源描述，SVG 承载布局结果。[Mermaid CLI](https://github.com/mermaid-js/mermaid-cli)、[Graphviz SVG 输出](https://graphviz.org/docs/outputs/svg/)

科研交换版应检查标签是否使用 `foreignObject`。Mermaid 支持 `htmlLabels` 配置；需要纯 SVG 文字时按当前版本设置为 `false`，再检查公式、换行和导出的实际节点。参数位置沿用当前版本 schema。[Mermaid 标签配置](https://mermaid.js.org/config/schema-docs/config)

反向由 SVG 恢复 Mermaid / DOT 时，先找到原 `.mmd` / `.dot`。只有图形时识别节点、边、标签和箭头方向，再生成描述，并核对每条连接；原布局参数与自动排版约束需重新确定。需要继续移动节点后自动重排，交付源描述与生成图；只改一个图面标签可直接编辑 SVG。

<a id="latex"></a>
## LaTeX / TikZ / 数学公式 ↔ SVG

已有 `.tex` 时用原编译链生成 PDF 或 DVI，再交给 `dvisvgm`。例如已得到 PDF 的单页图：

```sh
dvisvgm --pdf --page=1 --output=figure.svg figure.pdf
```

`--pdf` 路线是否可用与 dvisvgm 构建和后端有关；先用本机版本说明确认。DVI 的 special、字体及 PDF 后端支持各有范围，遇到缺失先查转换日志。字体转路径可稳定字形，但公式字符与排版宏仍保留在 TeX 源文件中。[dvisvgm PDF、页码与字体选项](https://dvisvgm.de/Manpage/)

**SVG → LaTeX 文档**可先转 PDF，由文档以图件方式排版。**SVG → TikZ 可编辑代码**则需按几何、文字和关系建立 TikZ 对象；已有路径能辅助生成轮廓，公式语义、宏和参数不随轮廓自动恢复。两种目标用不同的交付说明。

检查公式上下标、基线、字形、包围盒和裁剪；用户需要修改数学内容时交付 `.tex`，需要统一论文图形样式时同时提供 SVG。通用 PDF 交换路线见 [SVG ↔ PDF](vector-office.md#pdf)。

<a id="gis"></a>
## GeoJSON / GIS 图层 → SVG；SVG → 地理要素

用 QGIS 加载数据，确认 CRS、比例尺和图层样式，再从布局导出 SVG。导出项包括按地图图层建 SVG 组、文字/轮廓选择、几何简化；强制矢量可能改变原有渲染效果。栅格底图继续作为像素内容，线面要素可按导出器能力保留矢量。[QGIS 3.44 SVG 布局导出](https://doc.qgis.org/3.44/en/docs/user_manual/print_layout/create_output.html#export-as-svg)

对照最终地图的比例尺、图例、文字和边界；需要精确轮廓时评估简化阈值，避免以展示用途的简化结果替换分析数据。

**SVG → GeoJSON**需要坐标对应关系和要素含义。先确认地理参考、源 CRS、像素/用户坐标到地图坐标的变换，再提取路径与属性、处理孔洞和多部件几何。页面中可能有图例和多个不同尺度的地图框，应逐框处理。只有装饰地图时无法据形状确定真实经纬度；请用户提供数据或控制点。这是由坐标与数据模型差异得到的转换条件。原 GeoJSON / 项目仍在时直接使用原数据。

交付符合 RFC 7946 的 GeoJSON 时，坐标使用 WGS84，按**经度、纬度**顺序，以十进制度表示；投影坐标先转换到该目标坐标约定，再写入要素。[RFC 7946 坐标系统](https://www.rfc-editor.org/rfc/rfc7946#section-4)

<a id="web"></a>
## SVG ↔ HTML / React 组件

网页纯展示可用 `<img src="figure.svg" alt="…">`；要通过页面 CSS 或脚本操作内部部件，使用内联 SVG 或合适的文档嵌入方式。图片模式、独立文档模式对脚本、交互和外部资源的规则不同：放入 `<img>` 的 SVG 按受限图像模式处理，不能假定独立打开时的交互会保留。[SVG 处理模式](https://www.w3.org/TR/SVG2/conform.html)

SVG 转 React 可使用 SVGR，也可直接整理少量 JSX 属性；保留 `viewBox`、语义部件及无障碍名称。SVGR 的优化会加前缀降低 ID 冲突，但同一组件重复挂载仍需要实例级唯一标识；可用 React `useId` 为渐变、裁剪及 `aria-labelledby` 生成一致引用，或由调用方传入稳定前缀。[SVGR 配置](https://react-svgr.com/docs/options/)、[React useId](https://react.dev/reference/react/useId)

网页里选中器官、切换图层或改变变量时，让控件修改已有 SVG 对象。键盘操作与文字说明覆盖相同信息；同一组件放两次、切换深浅背景并缩放检查引用与样式。用户要求离线演示时将运行所需代码和资源一并交付，动画媒体路线见 [HTML / Canvas](raster-motion.md#html-canvas)。

反向从网页提取 SVG 时，保留引用定义、实际样式和字体条件，把当前状态写到独立文件；React props、状态管理与事件逻辑继续保留在组件源码。Canvas 只有像素时按图片重建处理。

承接用户上传的 SVG 时，把它作为能包含活动内容的文档输入：使用可信解析与清理流程处理脚本、事件属性和外部引用，选择合适的隔离展示方式，并限制解析与渲染资源。SVGO 的体积优化不承担上传内容清理。这些措施用于开发上传/预览功能，普通离线绘图无需扩展成站点安全项目。

<a id="recovery"></a>
## 能从 SVG 找回原始数据或工程文件吗？

按现有信息选择恢复层级：

| SVG 中保留的内容 | 可恢复的目标 | 需要补充的信息 |
| --- | --- | --- |
| 文本、几何、稳定 ID 与来源元数据 | 文字和可编辑图形、部分部件关系 | 检查元数据是否完整且仍与图形一致 |
| 轴线、刻度和数据标记 | 标定后的估计数据 | 轴类型、单位、刻度映射与重叠点；记录提取误差 |
| 节点、引线和箭头 | 经核对的流程图描述 | 含糊端点、边方向、隐藏关系 |
| 轮廓和色块 | 视觉重绘或几何交换 | 原始统计模型、测量数据、设计参数与约束 |

已有数据和脚本优先复用。做图表数据提取时，交付估计值及其坐标标定方法；做语义恢复时逐项核对标签、关系和来源。先确定用户要恢复哪一层，再选择工具。
