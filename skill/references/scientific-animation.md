# 科学过程动画

用户要展示运输、扩散方向、装配、运动或机制步骤时使用。沿用已确认 SVG 和机制；时间、粒子数、流速来自数据时按数据编码，讲解动画标明示意时间。科学过程与“从零画出成稿”的回放分别选择。

复用 `scripts/replay_svg.mjs` 的浏览器渲染与编码，增加显式时间线：

```text
node <skill目录>/scripts/replay_svg.mjs figure.svg new-output --timeline process.json --seconds 9 --format mp4
```

运行时与格式参数见 [绘制回放](drawing-replay.md)。输出为 `process.mp4` 或 `process.gif`，原 SVG 保留。此模式按指定的最终状态结束，末帧可与源图不同。

```json
{
  "description": "水沿已确认的通路移动",
  "time_scale": "illustrative",
  "tracks": [
    {"type":"flow","id":"water-route","start":0.5,"end":8,"count":6,"radius":3,"color":"#2c9fcb"},
    {"type":"opacity","id":"explanation","start":1,"end":2,"from":0,"to":1},
    {"type":"translate","id":"carrier","start":2,"end":5,"from":[0,0],"to":[80,0]},
    {"type":"rotate","id":"rotor","start":0,"end":8,"from":0,"to":360,"center":[120,100]}
  ]
}
```

- 时间为秒。`flow` 的 ID 指向路径或其他几何元素；方向沿路径定义，粒子在该区间循环，区间外隐藏。半径使用根 SVG 的坐标单位。嵌套分组的变换会转换到根坐标。
- 平移、旋转在对象原变换后应用，坐标按该对象局部坐标系解释。渐显直接控制目标的不透明度。端点状态在区间前后保持；一个对象的同一属性使用一条轨道。
- 待移动对象的内联 CSS 变换先规范为 SVG transform 属性；逐帧先更新对象，再采样其流动路径，末帧显式呈现时间线终点。
- 运输路径由科学关系确定，入口、跨膜点、接合与出口落实到图形。该工具控制图形运动；新增器官、细胞分裂或非刚性形变需要另行构造相应状态和动画，按任务选择现有动画工具。
- 静态源图中添加的讲解路径与标注单独分组。核对关键时刻的方向、接点、遮挡及字幕，检查媒体解码、时长和实际播放。保留时间线以便返修。

已验证示范：玉米根吸水、木质部输运、叶片蒸腾，使用示意路线与时间。机制依据：[OpenStax Biology 2e 30.5](https://openstax.org/books/biology-2e/pages/30-5-transport-of-water-and-solutes-in-plants)。需要更复杂的对象动画可接入 [Manim SVGMobject](https://docs.manim.community/en/stable/reference/manim.mobject.svg.svg_mobject.SVGMobject.html)，按导入效果选择支持的 SVG 子集。
