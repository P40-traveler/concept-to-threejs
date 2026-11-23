# Concept to Three.js

给 Codex 一张美术概念图，让它为同一个世界画出三种布局，选定其中一种，协调不同区域的建模，交付一个可以断网打开、自由飞行和切换灯光的 Three.js HTML。下面的《裂时之城》是用这套流程做出的完整实例。

**[在线试玩《裂时之城》](https://p40-traveler.github.io/concept-to-threejs/)** · **[下载 skill 安装包](https://github.com/P40-traveler/concept-to-threejs/releases/latest/download/concept-to-threejs.zip)** · **[下载离线 HTML](https://github.com/P40-traveler/concept-to-threejs/releases/latest/download/chronotown.html)** · **[看案例和原始提示词](examples/chronotown/README.md)**

![《裂时之城》离线实机演示。镜头绕到断廊侧面，在河谷市集切换灯光和光追，然后飞近西岸钟楼。](examples/chronotown/media/tour.webp)

## 安装与第一次使用

1. 解压上方的安装包，把里面的 `concept-to-threejs` 文件夹放入个人 Codex skills 目录。Windows 默认为 `%USERPROFILE%\.codex\skills\`，macOS 或 Linux 默认为 `~/.codex/skills/`。若已设置 `CODEX_HOME`，使用其下的 `skills/`。安装后的入口应是 `skills/concept-to-threejs/SKILL.md`。
2. 开一个新的 Codex 会话，附上概念图，输入下面的请求。完整制作需要能生成图像、启动建模子 agent、写入工作目录并运行浏览器验证的环境。体验已完成的示例只需要支持 WebGL2 的浏览器。

> 用 $concept-to-threejs 把这张概念图做成可以自由探索的世界。先生成三个布局并替我选一个。我想从街面走到高处，再回头看入口。最后给我一个有可选光照和光追的离线 HTML。

想自己挑方案时，加一句「三张布局出来后先给我看，等我选定再建模」。已有场景也能只改局部，例如「把横穿走道的拱肋接到外侧边梁，修完用原机位、原光照复拍」。

## 玩一下《裂时之城》

下载上方的 HTML 后直接双击。按 **2** 跳到错时断廊，拖动镜头转到侧面，观察两段拱廊如何错开。按 **3** 进入市集，再按 **L** 在斜阳、夜灯、单灯与原始照明之间切换。选中单灯试光后按 **G** 开关体素光追，停一下观察桥底暗部。**F** 切换自由飞行，**WASD** 移动，**Q / E** 下降或上升，**R** 返回总览。界面里的「设计手册」收录布局、分区参考和提示词。

## 六步制作流程

| 阶段 | 要做的决定 | 可回看的产物 |
| --- | --- | --- |
| 读概念与选案 | 哪些意象必须保留？三条路线让玩家看到什么不同的东西？ | 三张布局、各自的提示词、选案理由 |
| 搭灰模 | 地标放在哪里？站在桥底、街口或屋顶还能认路吗？ | 统一尺度的灰模、各区机位 |
| 分区派工 | 每组负责哪一段几何？跨区接缝由谁收口？ | 分区参考图、完整提示词、坐标与任务单 |
| 合场 | 从街道到桥头再到平台，入口、高差、通行净空是否连续？ | 能环绕和飞行的城镇 |
| 单灯与光追 | 用强侧光找穿插、错台与错误法线；几何修完后更新光追数据 | 同机位修前修后图、光追开关实测 |
| 离线交付 | 成品脱离源码目录、缓存和网络后还能操作吗？ | 单个 HTML 和交互验收 |

## 修改与验证

选案和生图方法在[美术参考](skills/concept-to-threejs/references/art-direction.md)，分工、坐标和接缝在[交接模板](skills/concept-to-threejs/references/model-handoff.md)，光追与交付标准在[渲染验收](skills/concept-to-threejs/references/render-and-test.md)。改好后可用 Python 3 重新生成只含 skill 的 ZIP。

```sh
python tools/package_skill.py
```

可选的离线启动检查依赖 Python、Playwright 和 Chromium。它会把 HTML 单独复制到空目录，以断网的新浏览器上下文启动，检查本地旁文件、网络请求、页面或着色器错误，以及可见的 WebGL 画布。换灯、导航和光追的画面变化还需操作验证。

```sh
python -m pip install playwright
python -m playwright install chromium
python skills/concept-to-threejs/scripts/check_offline.py docs/index.html
```

后续建议以可比较的实验整理在[工作流优化讨论](WORKFLOW-IDEAS.md)。示例内嵌 Three.js，随附其 [MIT 许可](notices/threejs-LICENSE.txt)。案例里的布局、分区参考和天空由图像模型生成，演示动图取自运行中的场景。
