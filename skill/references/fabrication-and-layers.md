# 实体制作与分层展示

## 从明确的 SVG 部件开始

用户要切割、绘图机、刺绣或实体轮廓时，确定设计尺寸、选中的轮廓/中心线与目标用途。制作参数来自用户、设备或材料资料；未给定时可交设计样例并标注所用尺寸。执行机器作业需要对应设备与工艺设置。

使用现有浏览器采样路径，再生成制作文件。依赖 Node.js、Playwright/Chromium；Python 侧使用 Shapely 2.1+，刺绣额外使用 pyembroidery。优先复用已装依赖，缺项安装到当前项目运行环境。运行时定位沿用 [绘制回放](drawing-replay.md)。

```json
{
  "width_mm": 80,
  "sample_mm": 0.25,
  "paths": ["outer-contour", "centerline"],
  "layers": [
    {"id":"silhouette","label":"轮廓"},
    {"id":"details","label":"细节"}
  ]
}
```

```text
node <skill目录>/scripts/svg_workshop.mjs figure.svg workshop.json new-workshop
python <skill目录>/scripts/fabricate_svg.py new-workshop/geometry.json new-fabrication --solid-id outer-contour --thickness 2 --embroidery --stitch-mm 2 --hoop-mm 120
```

`width_mm` 是整个 viewBox 的设计宽度；高度按比例计算，几何尺寸使用毫米。`sample_mm` 控制采样段长，曲线会近似为折线。选独立的几何 ID；复合路径先拆成显式轮廓，裁剪与蒙版先解析到实际几何。封闭边界需无自交，源 SVG 保持不变。输出目录使用新路径。

## 三种实体输出

| 用途 | 本工具交付 | 下一步需要落实的内容 |
| --- | --- | --- |
| 切割 | `cut.svg`：选中路径中全部闭合轮廓，毫米尺寸、名义轮廓 | 在 CAM 中设定材料、切缝补偿、功率/速度与切割顺序；内部装饰中心线保留在绘图版 |
| 绘图机 | `plot.svg`：全部选中路径的中心线或轮廓 | 检查笔宽、页面方向、落笔与抬笔顺序；填色图形按轮廓输出，需要排线填充时另行规划 |
| 刺绣 | 可选的单色平针 `running-stitch.dst/.pes` 及 `stitches.svg` 针迹预览 | 确认绣框、面料、衬布、线材和收尾设置，并实际试绣；缎面针与填充针使用 Ink/Stitch 按区域配置 |

刺绣是显式路径上的平针，采用给定针长，路径之间跳针并修剪。DST 不携带完整线色信息，配色随说明或 PES 交付。文件生成后读回检查针迹数、尺度与位移，避免把格式生成报告当作实物打样记录。

适用工具：[Ink/Stitch](https://inkstitch.org/docs/basic-usage/)、[pyembroidery](https://github.com/EmbroidePy/pyembroidery)、[AxiDraw](https://axidraw.com/doc/py_api/)。复杂机械连接与材料自适应参考 [LaserSVG](https://arxiv.org/abs/2209.00116)，按实际制作任务引入。

## 分层立体与实体挤出

`svg_workshop.mjs` 在指定 `layers` 时生成离线 `layers.html`：控制图层距离、俯视与旋转，并单独隐藏图层。源路径和颜色保留在各层矢量视图中。选择互不嵌套的部件，层序从底到顶排列。图层拆解按编辑结构命名；表达解剖层次时另需明确的结构依据。

采样前展开带裁剪视口的嵌套 SVG。分层中跨部件的 use 引用先整理到 defs；裁剪、蒙版和标记的定义随各层保留。

`fabricate_svg.py --solid-id <闭合轮廓ID> --thickness <毫米>` 生成 `profile.stl`。当前挤出单个无孔、无自交的平面轮廓，厚度显式指定；曲面器官建模按三维任务另行处理。STL 没有内置单位，本工具按毫米写入，在切片/CAD 软件中沿用毫米。

验收包括：原图部件与拆层显示对应，滑块、隐藏与合拢操作有效；挤出网格每条边连接两个面，体积等于轮廓面积乘厚度；重新读取序列化 STL 核对网格。交付交互页面、用户需要的实体文件和预览；说明实际完成的数字检查与打样状态。
