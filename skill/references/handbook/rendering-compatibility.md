# 渲染与兼容：定位跨应用变化

资料核实：2026-09-12。软件选项来自官方文档；下列编辑器行为未在本轮逐软件实测。转换结果按实际目标程序与版本验收。

目录：[使用环境](#profiles) · [可移植源文件](#portable) · [单位与精度](#precision) · [颜色与效果](#effects) · [优化](#optimization) · [故障查询](#troubleshooting) · [箭头变黑实测修复](#context-paint-recovery) · [验证](#verification)

<a id="profiles"></a>
## 先确认文件在哪里使用

| 目标 | 文件组织与核对点 |
| --- | --- |
| 网页内联 SVG | 可访问内部 DOM；检查宿主 CSS 是否覆盖同名类、`path` 或 `text` 样式 |
| HTML `img` / CSS 背景图 | 作为图像加载；脚本、交互和外部资源受到不同处理模式限制，适合自包含展示文件 |
| Illustrator 持续编辑 | 留 AI 工作母版，另存 SVG 交换版；核对保存选项中的私有编辑数据 |
| Inkscape 持续编辑 | 留 Inkscape SVG 工作母版；交换副本可用 Plain SVG，复查专有对象的编辑行为 |
| PPT / PDF 等转换 | 先确定要保留外观、文字还是原生可编辑对象，再查对应格式路线；在实际消费程序中打开 |

网页处理模式依据 [SVG 一致性与嵌入环境](https://www.w3.org/TR/SVG2/conform.html#processing-modes)。不能由浏览器能显示直接推断某编辑器能保留全部结构。

Illustrator 的 **Preserve Illustrator Editing Capabilities** 会把 AI 编辑数据存入 SVG；官方说明再次打开时可能读取 AI 部分，手改 SVG 文本不会反映进去。由代码持续修改的交换文件应另存不含该私有副本的 SVG，并保留 AI 母版。[Adobe 保存选项](https://helpx.adobe.com/illustrator/using/saving-artwork.html)

Inkscape 扩展可保存图层、节点或参数形状信息。手改由专有参数生成的 `d` 后，旧参数可能再次生成旧形状；修改时同时处理对应参数，或在交换副本中固化为普通路径。Plain SVG 仍可保留对象层级。[Inkscape SVG 与 Plain SVG](https://wiki.inkscape.org/wiki/Inkscape_SVG_vs._plain_SVG)

<a id="portable"></a>
## 什么源文件更容易交换？

1. 对布局写明根尺寸、`viewBox`、必要的 `preserveAspectRatio`；把变换和资源引用留在明确的对象层级中。
2. 对关键颜色、字体和线条使用明确属性或内联样式。普通样式规则可覆盖 presentation attribute，内联 `style="fill:red"` 也会覆盖同节点的 `fill="blue"`；修改前先定位实际生效声明。[SVG 样式级联](https://www.w3.org/TR/SVG2/styling.html)
3. 提取素材时连同祖先变换、继承样式及引用的 `defs` 一起提取。跨文件合并给实例 ID 加前缀，并同步更新 `href`、`url(#...)`、ARIA 引用；现有 `compose_svg.isolate()` 可复用，输入的 stylesheet 规则先解析到元素。[SVG 引用与实例](https://www.w3.org/TR/SVG2/struct.html#UseElement)
4. 交换文字写出实际字体族和字重；精确排版时使用显式行位置。字体未安装或字形缺失时先解决字体，再判断坐标是否出错。需要外观固定的路径字另存版本，保留可编辑文字母版。[SVG 字体](https://www.w3.org/TR/SVG2/text.html#FontsAndGlyphs)

SVG 允许外链图片与字体；需要离线自包含或纯矢量时，在当前任务中明确该交付条件。网页交互版与静态交换版可由同一母版派生，按用户请求交付。

<a id="precision"></a>
## 尺寸和小数位怎么选？

SVG 使用 CSS 单位关系：`1in = 96px = 72pt`。物理宽度与内部坐标分开管理，例如 1200 单位宽的 `viewBox` 交付为 `180mm`；内部 20 单位字高对应物理 3mm，约 8.50pt。PNG 的像素宽度再由输出分辨率决定：`px = mm / 25.4 × dpi`。[CSS 绝对单位](https://www.w3.org/TR/css-values-4/#absolute-lengths)

小数位依据最终尺寸与最大放大倍数选取。初估：局部坐标保留 `p` 位、轴向放大 `S` 倍，单坐标舍入误差上界约为 `0.5 × 10^-p × S`；这是单次量化估算，曲线简化、连续矩阵误差要另外测。细胞膜细线、相邻拼接边和箭头尖端应重点对照。Adobe 导出提供精度设置，但具体数值应由当前图验证，不能统一用最少小数位。[Adobe SVG 导出](https://helpx.adobe.com/illustrator/using/exporting-artwork.html)

<a id="effects"></a>
## 透明、滤镜和颜色为何变化？

- **组透明度**：组上 `opacity="0.5"` 是先合成组再整体透明；把 0.5 分散到每个子对象，会改变交叠区域。保留原来的合成边界。[SVG 合成模型](https://www.w3.org/TR/SVG2/render.html)
- **阴影被截断**：先查 `filter` 的作用区域，再查外层裁剪和视口。按效果范围扩大 `x/y/width/height`，显式写 `filterUnits`；扩大画布不能修复内部滤镜截断。
- **同一效果颜色变暗**：`color-interpolation-filters` 默认 `linearRGB`，其他常规颜色插值默认 `sRGB`。根据设计明确滤镜颜色空间，再对照输出；不要把不同插值的结果直接视为错误。[Filter Effects](https://www.w3.org/TR/filter-effects-1/#FilterProperty)
- **透明蒙版表现反转**：先查亮度或 alpha 语义、蒙版单位与内容坐标。逐层隐藏蒙版和裁剪，定位真正变化的一层。[CSS Masking](https://www.w3.org/TR/css-masking-1/)

屏幕交换先用明确的 sRGB 颜色值；印刷中的 CMYK、专色和输出配置文件在目标排版/印前流程核验，改扩展名不能完成色彩管理。此项是交付策略，具体印刷路线按承印方要求确定。

<a id="optimization"></a>
## 怎样缩小文件而保留编辑意义？

先清理确实未使用的资源、冗余数据与过密采样，再评估路径合并、组折叠和实例化对返修的影响。对象 ID 可能被配方、回放和外部程序引用，即使当前 XML 内没有引用，也有用途。

SVGO `cleanupIds` 会移除未被引用的 ID、缩短被引用的 ID；可配置 `preserve` / `preservePrefixes`，或在可编辑母版中关闭该步骤。`prefixIds` 可辅助多图同页避免 ID 冲突；使用稳定且区分实例的前缀。现有 skill 合成器已处理本地引用隔离，避免重复做两套重命名。[cleanupIds](https://svgo.dev/docs/plugins/cleanupIds/)、[prefixIds](https://svgo.dev/docs/plugins/prefixIds/)

优化交付副本后，挑一个实际任务验收：移动一只鸟、改一条标签，或从配方重新生成。视觉相同却失去这些能力时，需要恢复对应编辑结构。

<a id="troubleshooting"></a>
## 常见症状 → 原因 → 修复 → 验证

这些是定位起点，具体原因由源文件确认；原理见上方对应条目。

| 症状 | 优先排查 | 修复动作 | 最小验证 |
| --- | --- | --- | --- |
| 粘贴后变黑或变色 | 外部 CSS、继承丢失、重复渐变 ID | 固化必要样式，保留 defs，隔离 ID | 与原图同尺寸并排，改色一次 |
| 导入后整体偏移 | 非零 viewBox、嵌套视口、矩阵顺序 | 保留源视口或正确求等效矩阵 | 对照三个不共线基准点 |
| 移动对象后连线留在原地 | 两端未绑定对象，坐标系不同 | 用配方端点绑定并重新生成 | 同时移动与缩放一个端对象 |
| 开放曲线中出现色块 | 默认填充触发隐式闭合 | 线条对象设 `fill="none"` | 检查其他需要填充的对象 |
| 箭头忽大忽小或离端点有缝 | markerUnits、refX/refY、端帽 | 定义尺寸单位和尖端参考点 | 改线宽，再看箭头方向与端点 |
| 字符缺失、换行不同 | 字体/字重缺失、复杂排版实现差异 | 解决字体，显式定位必要行 | 检查中英、希腊字母和上下标 |
| 半透明交叠区域变深 | 组透明度被拆散 | 恢复组级合成 | 对照交叠区和非交叠区 |
| 保存再打开后修改消失 | AI 私有副本或参数形状旧数据 | 保留工作母版，更新/移除交换副本旧参数 | 重新打开并读取目标对象属性 |

<a id="context-paint-recovery"></a>
## 实测修复：PDF 中的彩色箭头变黑

2026-09-12，在 CairoSVG 2.9.0 中复现：两条不同颜色的连线共用一个 `fill="context-stroke"` 的 marker，原 SVG 在 Chrome 152 中按各条线着色，PDF 的两个箭头均变为黑色。该例的 μ 标签正常，问题定位到 marker 的上下文颜色处理。

遇到同类实际失真时，在导出副本中按引用对象落实颜色：

1. 找到失真箭头的 marker 和引用它的连线，解析每条线的实际 stroke；简单固色可读明确属性，CSS、继承及渐变须按其实际来源求值。
2. 为不同颜色的引用分别复制 marker，给定义及内部具名资源设置独立 ID、更新相关引用，将当前的 `context-stroke` 填色落实为对应连线的颜色。一个共享 marker 被多色引用时，分别处理各实例。
3. 保留 marker 的单位、尺寸、refX/refY、方向及路径几何，重定向连线的 marker 引用。原 SVG 继续保留共享定义和动态着色能力；转换副本表达当前静态状态。
4. 重新导出，检查各个箭头的颜色、尖端与方向，同时确认标签和正确区域。采用其他渲染器时也验证同样的目标内容。

本例修复后：原稿与导出副本在 Chrome 中的像素一致；PDF 恢复两种箭头颜色、保留 μ、0 个图像对象；连线几何、标签和 150 × 60 mm 页框保持。此结果覆盖固色上下文 marker；渐变、透明度、复杂 CSS 与其他渲染器随实际输入核对。

<a id="verification"></a>
## 怎样证明转换确实可用？

检查与当前目的对应：结构检查确认引用和文件完整；实际渲染看缺失、字体、裁剪与颜色；目标程序里完成一次指定修改并保存重开，确认可编辑性。无需对每个文件重跑所有软件。

记录源/目标文件、程序版本、转换选项、实际检查与已知差异。已有脚本 `check_svg.py` 只提供其实现范围内的结构诊断；跨格式验收仍以目标程序行为为准。本页提供知识与排错路线，不把文档能力算作本机实测结果。
