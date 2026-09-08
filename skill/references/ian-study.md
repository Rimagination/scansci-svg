# IAN 样本观察记录

## 分类扩展记录：2026-09-08

本次读取 [IAN Symbols](https://ian.umces.edu/media-library/symbols/) 页面的相册筛选器，核对 6 个主题组、55 个相册；页面 PDF 目录说明为 56 albums。完整名称与 ID 见 [IAN 相册对应表](ian-albums.md)，在线快照存维护项目 `.local/research/ian-categories-20260908/albums.json`。

[本地分类](taxonomy.md)扩展为 16 个主题领域、149 个子类，每类记录典型对象、构形及编辑部件、核对重点和来源映射，55 个在线相册均有对应入口。此次增加的是分类与构形卡，样本观察数量沿用下方逐批记录。生命、环境、工程和人类活动卡分别附本次核对的专业来源入口；具体图件按任务记录来源和实际验证结果。

## 既有绘图研究

后续维护：2026-09-07 做了直接绘图与冻结 skill 的三题对照，未发现全面质量优势，入口改为短约定与按需参考。详细实验位于 `.local/research/scientific-vector-ab-20260907-111528/report.md`，旧入口保存在同目录 `skill-before/`。类别研究保留，结论适用于本次三题对照。

随技能提供的 `assets/incubator.svg` 是新版单独应用生成的原创通用培养箱示意，无 IAN 路径来源，未用于原 A/B 胜负。已看实际渲染并检查整机与观察窗组，玻璃/边框/反光同组；未验证真实型号或目标编辑器 UI，不预设所有科研装置外形。

首批核查日期：2026-09-06，分析下列三个样本的 SVG 元素结构及实际渲染。后续批次另列；未遍历整个素材库，未训练神经网络。

| 样本 | 实际结构与观察 | 提炼的画法 |
| --- | --- | --- |
| [Generic tree: spring](https://ian.umces.edu/media-library/generic-tree-spring/) | 14 个 path、14 个线性渐变；分叉树干与前后多层花叶团，无逐叶描摹 | 用树干骨架与叶团遮挡表达季节和体积 |
| [Urban: city building 01](https://ian.umces.edu/media-library/urban-city-building-01/) | 18 个 polygon、2 个线性渐变；顶面、明暗侧面与窗列；整体有手绘式透视 | 用共享体块和重复窗户表达建筑，先保证比例和一致投影 |
| [River 3D: cross section 1](https://ian.umces.edu/media-library/river-3d-cross-section-1/) | 水面、岸边、远近陆地、水下空间和底质；有细描边、曲线与渐变 | 以共享岸线与层叠曲面表达连续水陆和剖面 |

这些样本的顶层绘图元素需补充语义分组以支持整对象拖动。语义分组、唯一 ID、窗格约束和轻量验证为本地新增。

原素材署名：树木与河流为 Tracey Saxby / Integration and Application Network；建筑为 Catherine Collier / Healthy Waterways Partnership。许可逐资产不同：第一批三样本页面列示 CC BY-SA 4.0；第二批 34 个样本中 32 个内嵌元数据为 CC BY-SA 3.0、2 个（大肠杆菌、灰狐）为 4.0。实际使用或改编具体素材时核对并保留对应版本的许可与署名；路径复用按实际改编记录来源。

本技能不捆绑 IAN 源路径，也不提供官方认证风格。绘制时原创建立几何；若作品实际依赖某份原图的表达细节，应如实记录为改编并按来源要求处理。

## 本轮要纠正的已观察失败

- 面对“学习画法”的需求，助手先前推荐检索和替换素材，未回应原创绘图能力。
- 从位图推断树形时，通过颜色分割和局部轮廓拼接得到不自然的树冠与过细树干。
- 针对单图现场编写大量代码，导致约13分钟交付局部试验，却突出几秒的脚本运行时间。

应对：自然语言→部件关系→原创几何→少量细节→一次渲染核验；调用既有画法，不默认下载素材或重新搭建识别系统。此处记录单次行为失败，供后续流程修正对照。

## 第二批：34 个样本（2026-09-07）

按 [taxonomy](taxonomy.md) 相册为 7 个指南各选代表样本（flora 5、fauna 5、ecosystems 5、human 5、microbes 4、processes 6、research 4）。方法：全部 34 个做了元素计数统计（path/polygon/渐变/描边等）+ 渲染核对；generic fish 与大肠杆菌的路径另做逐条阅读；相册清单（580 条目）来自在线检索，样本即下即用，未爬全库。样本 SVG 与统计留在 skill 外的工作目录，不捆绑入库。

| 指南 | 样本 | 关键观察 |
| --- | --- | --- |
| flora | [Bamboo 1](https://ian.umces.edu/media-library/bamboo-1/) | 119 路径 57 渐变；堆叠节间+节环+上部细枝披针叶 |
| flora | [Generic fern](https://ian.umces.edu/media-library/generic-fern/) | 仅 11 路径；每片复叶一条锯齿闭合轮廓 |
| flora | [Giant kelp 1](https://ian.umces.edu/media-library/macrocystis-pyrifera-giant-kelp-1/) | 98 路径 43 渐变；细波浪柄+沿线交替叶片+固着器，竖幅 114×501 |
| flora | [Oryza spp. (Rice)](https://ian.umces.edu/media-library/oryza-spp-rice/) | 21 路径；基部扇形锥形叶+下垂穗，双色绿+赭穗 |
| flora | [Red Mangrove](https://ian.umces.edu/media-library/rhizophora-mangle-red-mangrove/) | 11 路径；拱形支柱根+椭圆叶团 |
| fauna | [Generic fish](https://ian.umces.edu/media-library/generic-fish/) | 3 路径：单条闭合全身轮廓（鳍并入）+白色眼圈/鳃弧；CC BY-SA 3.0 |
| fauna | [Gray fox](https://ian.umces.edu/media-library/urocyon-cinereoargenteus-gray-fox/) | 44 路径 28 渐变 8 圆；大渐变面块叠合，无外描边；CC BY-SA 4.0 |
| fauna | [Great blue heron 2](https://ian.umces.edu/media-library/ardea-herodias-great-blue-heron-2/) | 97 路径 89 渐变；多层羽片翼+S 颈+拖后腿 |
| fauna | [Monarch butterfly](https://ian.umces.edu/media-library/danaus-plexippus-monarch-butterfly/) | 133 路径 131 渐变；橙翅室+粗黑脉+白点列，近镜像对称 |
| fauna | [Rock crab](https://ian.umces.edu/media-library/grapsus-tenuicrustatus-thin-shelled-rock-crab/) | 78 路径 52 渐变；甲壳+分节折角步足+双螯，灰白斑纹 |
| ecosystems | [Coastline 2D: barrier island](https://ian.umces.edu/media-library/coastline-2d-barrier-island-with-mixed-energy/) | 41 路径 23 渐变；平面图模式：平色水底+岸块+潮沟脉络+白浪脊 |
| ecosystems | [Estuary 3D: braided river](https://ian.umces.edu/media-library/estuary-3d-braided-river-and-mudflat/) | 仅 6 路径 4 多边形 4 渐变；切块体：顶面+两侧面+地层条带 |
| ecosystems | [Cumulus 1](https://ian.umces.edu/media-library/low-clouds-cumulus-1/) | 1 路径 1 渐变；单凸弧云，白→灰 |
| ecosystems | [Weather: wind 3](https://ian.umces.edu/media-library/weather-wind-3/) | 4 路径；圆头粗描边螺线+流线，纯线构 |
| ecosystems | [Mountain range 3D](https://ian.umces.edu/media-library/mountain-range-3d/) | 31 路径 18 渐变；地形板+坡向明暗+火山口 |
| human | [Factory](https://ian.umces.edu/media-library/factory/) | 4 路径；黑剪影+反色窗格镂空 |
| human | [Fish cages](https://ian.umces.edu/media-library/fish-cages/) | 358 路径 364 渐变；虚线边界+构件符号+5 条写实鱼（写实质感是有意点缀） |
| human | [Outrigger canoe 1](https://ian.umces.edu/media-library/outrigger-canoe-1/) | 15 路径 13 渐变；梭形船体+条带+舷外浮筒斜撑 |
| human | [Tractor 5](https://ian.umces.edu/media-library/tractor-5/) | 106 路径 27 渐变；车轮同心圆+绿色机身分面+驾驶舱乘员剪影 |
| human | [Pickup truck](https://ian.umces.edu/media-library/vehicle-pickup-truck/) | 64 路径 1 渐变；3/4 视角分面+深色玻璃 |
| microbes | [Escherichia coli](https://ian.umces.edu/media-library/escherichia-coli/) | 20 路径无渐变；圆端弯杆散布；CC BY-SA 4.0。接续源码核对纠正：开放中心曲线与闭合加宽轮廓成对，原“细锥鞭毛”解释撤回 |
| microbes | [Anabaena](https://ian.umces.edu/media-library/anabaena/) | 398 路径 81 渐变；重复细胞链+大个灰色异形胞 |
| microbes | [Coccoid bacterium](https://ian.umces.edu/media-library/coccoid-bacterium/) | 2 路径：大圆+内偏移轮廓线 |
| microbes | [Adenovirus](https://ian.umces.edu/media-library/adenovirus/) | 138 路径无渐变；鹅卵石簇衣壳（非几何二十面体）+6 根黑色带端体纤维 |
| processes | [Process; (x = element) in](https://ian.umces.edu/media-library/process-x-element-in/) | 5 路径；波浪箭头一条闭合轮廓+暗纹叠加+矢量化字母 X |
| processes | [Inputs: nutrients 2](https://ian.umces.edu/media-library/inputs-nutrients-2/) | 10 路径；大弧锥形箭头，标签沿曲线（已矢量化） |
| processes | [Photosynthesis](https://ian.umces.edu/media-library/photosynthesis/) | 13 路径；成对反向波浪条带箭头（绿下/蓝上） |
| processes | [Mixing](https://ian.umces.edu/media-library/mixing/) | 8 路径 4 渐变；嵌套描边弧+独立箭头三角 |
| processes | [Concentration: high chlorophyll](https://ian.umces.edu/media-library/concentration-high-chlorophyll/) | 18 路径；粗描边圆+点阵密度 |
| processes | [Uncertainty](https://ian.umces.edu/media-library/uncertainty/) | 3 路径；厚描边墨团+矢量化 ? |
| research | [Microscope](https://ian.umces.edu/media-library/microscope/) | 26 路径+15 圆 64 渐变；C 臂+斜目镜+载物台，黑旋钮重音 |
| research | [Field station](https://ian.umces.edu/media-library/field-station-3/) | 6 路径；深灰剪影：锅面+信号弧+窗格建筑 |
| research | [Meteorological tower](https://ian.umces.edu/media-library/meteorological-tower/) | 81 路径+50 线+145 渐变；桁架线构+拉线放射+横臂仪器 |
| research | [Box corer](https://ian.umces.edu/media-library/box-corer/) | 9 路径+21 多边形；夹爪箱体+细缆绳 |

跨批结构结论：34 个中仅 4 个有 `<g>` 分组（河口 4、云 1、山脉 18、网箱 5），均非语义分组——第一批结论在更大样本上成立。路径预算跨度极大（2 到 398），完成度由用途决定，不设统一标准。

## 第二批原创验证（2026-09-07）

每指南 1 张全新对象、双尺寸（展示+约 96 px 缩略图）渲染检查。首轮 7 张中 4 张有实际缺陷并修正后复检通过：

| 测试 | 首轮缺陷 | 修正 | 结果 |
| --- | --- | --- | --- |
| 玉米（flora） | 叶短且对称，读作针叶树 | 改长拱形垂叶、加宽雄穗 | 通过 |
| 企鹅站姿（fauna） | 无 | — | 通过 |
| 荒漠块体（ecosystems） | 干河床溢出顶面边缘像破洞 | 收进顶面范围 | 通过 |
| 风机（human） | 无 | — | 通过 |
| 螺旋菌（microbes） | 闭合曲线拼 S 形断裂成月牙块 | 改粗圆头描边沿中心线+内侧高光描边 | 通过 |
| 沉积输入+浓度档（processes） | 箭头轮廓臃肿不成箭头 | 重画锥形弯箭头+独立三角头 | 通过 |
| 培养皿（research） | 无 | — | 通过 |

验证沉淀的新技法：螺旋体的稳健构造是"描边中心线"而非闭合胶囊（已写进 [microbes](microbes.md)）。其余测试确认对应指南规则可直接执行。一次通过不保证任意对象都成功；这 7 个测试只证明该指南语法在各自一个新对象上可迁移。

## 接续核对与变体改进（2026-09-07）

上面的第二批 34 样本与 7 次应用结果沿用 zcode 留下的记录。本次接续已阅读全部指南，但第二批产物目录尚待定位，未声称重新执行上述测试。第一批和本次独立核对的素材位于 `.local/research/ian_drawing_study/references/`；原 SVG 保留来源元数据，PNG 为学习渲染，不作为原创交付。

本次实际读取源结构并查看渲染的补充样本：

| 来源 | 本地文件 | 本次观察 |
| --- | --- | --- |
| [White Perch](https://ian.umces.edu/media-library/morone-americana-white-perch/) | fish.svg / fish.png | 149 path、1 polygon、10 linearGradient；平滑鱼体叠加独立鳍、鳍条与少量鳞纹。可与 generic fish 的低细节完成度对照，路径少并非自然感的充分条件 |
| [Smooth cordgrass 2](https://ian.umces.edu/media-library/spartina-alterniflora-2-smooth-cordgrass/) | grass.svg / grass.png | 300 path、300 linearGradient；渐尖长叶共同形成丛状轮廓，长短/角度/明暗有层次。此画法对应该样本的基生叶丛；其他植物按各自叶序构形 |
| [Escherichia coli](https://ian.umces.edu/media-library/escherichia-coli/) | bacteria.svg / bacteria.png | 20 path、10 g、无渐变；圆端弯杆以近邻品红色散布。与第二批条目重复，不作为新增独立样本。仅凭渲染不推断真实附属结构分布 |
| [Inputs: bacteria](https://ian.umces.edu/media-library/inputs-bacteria/) | flow.svg / flow.png | 2 path；大弧形箭身接完整箭头。粉色和页面朝向属于该图表达选择；新图依对象关系和图例设置 |

新增 `variation-and-learning.md`，修正叶位、车轮投影、透明镂空、开放曲线填充、过程赋义、专业结构核实与放大/输运关系的混用。具体物种、设备的自然事实仍需针对请求核对；本批改进不等同于已扩展到所有科研学科。

源结构纠错：大肠杆菌首对路径中，开放路径从 `(116.1,223)` 沿曲线到 `(186,149.5)`；对应闭合路径围绕同一条中心轨迹加宽并封口。两者同色，前者没有 stroke。结合实际渲染，它不能支持“从细胞极部长出鞭毛”的旧解释。该解释已从微生物指南与上表撤回，避免将导出时保留的中心路径误当作生物部件。

### 新变体应用：沿茎对生叶幼苗

产物：`.local/research/ian_drawing_study/seedling_opposite_leaves.svg`，同目录同名 PNG 为预览。描述要求三个不同高度各一对叶，共六片完整叶，连续略弯茎与细根系，无文字和土块。

应用代理结构检查：六个单叶组、41 个唯一 ID、单一整株组、自包含透明 SVG。正常尺寸及约 96 px 高缩略图已看；主代理查看实际预览和 SVG，确认六叶分三层、叶柄接茎。仅证明该描述变体可绘制，不提供物种鉴定或编辑器交互保证。遗留：缩略图细根辨识弱，茎根颜色交界偏硬。

本次技能格式验证通过，35 个本地引用链接有效，55 个相册 ID 唯一。后续仅补来源 URL/观察记录，未重复执行未受影响的格式测试。无生产代码变更，未跑 EasySlides 全量测试/构建、哈希；采用一次独立应用验证，无额外独立代码审查。
