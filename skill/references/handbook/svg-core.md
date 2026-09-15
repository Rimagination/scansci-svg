# SVG 核心：按问题查结构与几何

资料核实：2026-09-12。以下语义依据 W3C 文档；具体软件的支持与转换路线查 [渲染与兼容](rendering-compatibility.md)。

目录：[文档](#document) · [坐标](#coordinates) · [路径](#paths) · [描边](#paint) · [复用与裁剪](#reusable) · [文字](#text)

<a id="document"></a>
## 怎样组织一个可持续编辑的文件？

独立 SVG 使用 XML 命名空间，保存为 UTF-8。`viewBox` 定义绘图坐标；`width/height` 定义输出视口。`g` 表示一起变换或编辑的对象；稳定 ID 供部件修改、连线和回放引用。可见对象通常按文档顺序由后向前绘制，因此调整遮挡优先调整同级顺序。下例可直接保存为 `.svg`。结构依据：[SVG 文档结构](https://www.w3.org/TR/SVG2/struct.html)、[绘制顺序](https://www.w3.org/TR/SVG2/render.html#RenderingOrder)。

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200"
     width="120mm" height="60mm" role="img"
     aria-labelledby="fig-title" aria-describedby="fig-desc">
  <title id="fig-title">样品示意</title>
  <desc id="fig-desc">绿色圆形样品，下方标注样品 A。</desc>
  <g id="sample-a" fill="#467d68">
    <circle id="sample-body" cx="200" cy="80" r="36"/>
    <text id="sample-label" x="200" y="150" text-anchor="middle"
          font-family="sans-serif" font-size="18">样品 A</text>
  </g>
</svg>
```

SVG 标准还允许位图、脚本、动画与 `foreignObject`。本 skill 默认科研矢量交付选用原生几何、文字与语义分组；参考照片嵌入与纯矢量重建是不同交付目标，按用户任务选定。[SVG 嵌入内容](https://www.w3.org/TR/SVG2/embedded.html)

<a id="coordinates"></a>
## 为什么缩放后位置、比例或连线不对？

- `viewBox="minX minY w h"` 中的前两项是坐标原点偏移。改画布时保留它们，或把偏移真正应用到内容；只把它们改成零会移动视野。
- 默认 `preserveAspectRatio="xMidYMid meet"` 等比完整放入。`slice` 等比铺满，内容可能超出视口；是否裁去由裁剪/溢出设置决定。`none` 分别缩放两轴，圆可能变成椭圆。
- 嵌套 `<svg>` 会建立新视口，百分比随最近视口解析；`g` 不建立新视口。拼图保留源视口，或者准确计算等效矩阵后展平。[坐标与视口](https://www.w3.org/TR/SVG2/coords.html)

`matrix(a b c d e f)` 把点变成 `x'=a*x+c*y+e`、`y'=b*x+d*y+f`。列向量写法下，`translate(100 20) scale(2)` 的矩阵为 `T×S`，点 `(10,5)` 得到 `(120,30)`；调换两个变换会得到 `(220,50)`。父子变换继续相乘。连接两个不同组中的点时，先把两点换到共同坐标系，再绘制线段。[CSS 变换数学定义](https://www.w3.org/TR/css-transforms-1/#mathematical-description)

浏览器中可用 `root.getScreenCTM().inverse().multiply(node.getScreenCTM())` 得到从节点局部到根 SVG 局部的矩阵。`getBBox()` 是几何包围盒，不能直接当成屏幕坐标；描边、标记与滤镜边缘另行核对。要测文字，等字体加载完成后测量。[SVG DOM 与包围盒](https://www.w3.org/TR/SVG2/types.html#InterfaceSVGGraphicsElement)

<a id="paths"></a>
## 路径怎样既精细又便于修改？

| 指令 | 含义与使用点 |
| --- | --- |
| `M / L / H / V` | 移动、直线、水平线、垂直线；小写表示相对当前位置 |
| `C / Q` | 三次/二次贝塞尔曲线；沿轮廓切向安排控制点，转折处再加节点 |
| `S / T` | 延续前一条相应曲线的镜像控制点；接在其他指令后不能假定仍有同样切向 |
| `A rx ry angle large sweep x y` | 椭圆弧；两项标志决定长短弧和扫掠方向，终点与起点相同时不产生完整圆 |
| `Z` | 闭合当前子路径，连接处按 join 绘制；手写 `L` 回起点仍是开放子路径的端帽语义 |

命令与端点规则见 [SVG 路径](https://www.w3.org/TR/SVG2/paths.html)。一个 path 可以含多个子路径；是否拆开取决于它们是否需要独立改色、移动或命名。

开放路径也可能参与填充：填充时按隐式闭合计算，因此只画曲线线条要写 `fill="none"`。孔洞取决于 `fill-rule`：默认 `nonzero` 受绕行方向影响，`evenodd` 按穿越边界次数判断。需要可读的圆环时可用 `fill-rule="evenodd"` 配两个闭合子路径；它们仍应属于同一有孔对象。[填充规则](https://www.w3.org/TR/SVG2/painting.html#FillRuleProperty)

<a id="paint"></a>
## 描边与箭头怎样保持一致？

`stroke-width` 决定线宽，`stroke-linecap` 控制开放端点，`stroke-linejoin` 与 `stroke-miterlimit` 控制转角尖刺。`stroke-dasharray` 和 `stroke-dashoffset` 控制虚线与描线回放；回放动作另见已有 [绘制回放](../drawing-replay.md)。缩放下需要固定显示线宽时，可使用 `vector-effect="non-scaling-stroke"`，再核对目标编辑器。[描边属性](https://www.w3.org/TR/SVG2/painting.html#StrokeProperties)、[矢量效果](https://www.w3.org/TR/SVG2/coords.html#VectorEffects)

箭头通常由 `marker-end="url(#arrow)"` 引用 `<marker>`：`refX/refY` 定义与线端重合的点，`orient="auto"` 沿路径末端方向。`markerUnits` 默认 `strokeWidth`，箭头随线宽变化；需要按当前用户单位固定尺寸时显式设 `userSpaceOnUse`。先确认箭头尖端与终点对齐，再调整外观。[标记定义](https://www.w3.org/TR/SVG2/painting.html#Markers)

<a id="reusable"></a>
## 什么时候用 defs、use、裁剪与蒙版？

- **复用形状**：`defs` 保存定义，`use href="#leaf"` 实例化。修改源会影响所有实例；需要逐片改内部形状时，把该实例展开为保留继承样式与变换的独立组。实例独立命名后再绑定编辑动作。[defs 与 use](https://www.w3.org/TR/SVG2/struct.html#UseElement)
- **限制可见范围**：`clipPath` 使用几何边界，适合剖面窗口或水体内的鱼；`mask` 按透明度或亮度控制可见程度，适合柔和消退。为可移植性显式选择 `clipPathUnits`、`maskUnits`、`maskContentUnits`。黑色在亮度蒙版中隐藏内容，在 alpha 蒙版中仍可完全可见；通过 `mask-type` 指定期望语义。[CSS Masking](https://www.w3.org/TR/css-masking-1/)
- **连续明暗**：`linearGradient/radialGradient` 和 `stop` 定义渐变。默认 `gradientUnits="objectBoundingBox"` 随对象包围盒变化；共享场景光照用 `userSpaceOnUse` 并写场景坐标。裁剪和渐变定义也随素材一起提取，不能只复制可见 path。[SVG 渐变](https://www.w3.org/TR/SVG2/pservers.html)

<a id="text"></a>
## 文字怎样保持可编辑、可读与可访问？

科学标签用 `text`，同一句里的上下标用 `tspan`。常规横排下 `y` 定位基线，`text-anchor` 控制整段起点/居中/末端；换行可用独立 `tspan` 的显式 `x/y`，便于跨应用核对。示例：`<text x="20" y="40">CO<tspan dy="4" font-size="70%">2</tspan></text>`；若后面继续正文，需要恢复基线。

记录字体族、字重及实际字体；替换字体后重测标签长度、希腊字母和上下标。需要路径化交付时另存轮廓版，同时保留文字母版。网页图提供 `title/desc`；部件可用 `aria-labelledby` 指向其真实标签。装饰元素与有意义对象分开组织。[SVG 文字与可访问语义](https://www.w3.org/TR/SVG2/text.html)
