# SVG 绘制回放

用户要求回放时启用，沿用当前明确的 SVG 成稿；多个候选无法定位时先问用哪张。默认按离散步骤重建绘制过程：每次直接应用一个有意义的笔画、色面或部件变化。已有真实录屏或编辑事件记录时可按真实记录回放。

## 编排与表现

按图件选择符合绘制直觉的顺序，例如整体线稿、分部件固有色、阴影、纹理、高光和标注；也可先完成一个主体再绘制附属对象。组顺序表示编辑归属，源文件层叠表示遮挡，回放步骤表示制作顺序，三者分别保留。

精细区域可分成多个完整笔画或细节组，避免一块无意义碎片对应一个事件。保持原始比例和足够细节；为合理的阶段展示增加的临时线稿在相应色面完成时退出，末帧恢复完整源图。

“播放不要渐变”默认解释为时间上直接切换：没有淡入淡出、路径插值或补间。源图本来具有的渐变色、半透明色面和阴影保留在各步骤中。用户明确要求平面纯色时再按对应要求制作。

## 工具与交付

复用 `scripts/replay_svg.mjs`，依赖 Node.js、Playwright 与 Chromium。视频/GIF 额外使用 FFmpeg，单文件 HTML 无需编码器。通过 `--playwright` / `PLAYWRIGHT_MODULE` 和 `--chrome` / `CHROME_PATH` 定位已有浏览器运行时。

```text
node <skill目录>/scripts/replay_svg.mjs figure.svg new-output --style steps --format mp4
node <skill目录>/scripts/replay_svg.mjs figure.svg new-demo --steps drawing.json --format html
```

常规回放交 MP4；用户指定 GIF 时使用 `--format gif`；`both` 生成这两种媒体。用户要可播放 Demo、离线或 HTML+CSS 单文件时使用 `html`，交付完整 `replay.html`，包含内联 SVG、CSS 和原生 JavaScript 播放器，支持播放、暂停、重播、逐步定位与速度选择，不依赖网络资源。成稿 SVG 保持原生图形与可编辑文字。只要 HTML 时不自动再导出视频。

- 默认 9 秒，媒体为 20 fps、宽 640 px，比例来自 viewBox，白底。`--seconds`、`--fps`、`--width` 可按用途调整。HTML 自适应容器宽度。
- `--steps` 明确指定绘制阶段；未提供时按具名部件生成轮廓/成形步骤。新图需要细分阴影和高光时在构形时给它们稳定 ID，避免从颜色自动猜测图层含义。
- `--style smooth` 保留原有逐步勾勒/填色模式，只在用户需要平滑表现时使用；`--order` 用于该模式。科学机制动画使用独立的 `--timeline`，见 [科学过程动画](scientific-animation.md)。
- 每次使用新输出目录，原稿保持不变。工作帧和检查文件留在工作目录，用户接收请求的格式和预览。

显式步骤示例：

```json
{
  "steps": [
    {"label":"主体线稿","mode":"outline","ids":["body"]},
    {"label":"固有色","mode":"show","ids":["base-colors"]},
    {"label":"阴影","mode":"show","ids":["shadows"]},
    {"label":"纹理与高光","mode":"show","ids":["details","highlights"]}
  ]
}
```

`outline` 显示临时矢量轮廓，`show` 直接显示对应源图对象；节点在原有层叠位置显示，子对象可独立入场。播放器最后恢复全部原图对象。主体组包含阴影等子组时，用更具体的基本轮廓 ID 安排线稿，避免提前画出所有内部装饰。

## 输入与验收

工具读取静态、自包含 SVG，并保留有效渐变、局部引用、分组和变换。外链、嵌入位图、脚本、已有动画及 style 样式表先在副本中规范；根内联尺寸整理为 width/height 属性与 viewBox。离散回放的 use 定义放入 defs，文字整体直接出现；真实手部或铅笔纹理根据具体要求另行制作。

对照开场、线稿、色面、细节和末帧，确认阶段有绘制意义，成稿完整，步骤之间直接切换。工具将结束画面与同一浏览器的源图渲染比较。HTML 检查离线打开、播放、拖动和重播；视频/GIF 检查解码、时长与实际画质。文件大小按实际结果报告，完整任务耗时和纯导出耗时分开记录。
