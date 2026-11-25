# depthmapX v0.10.0 简体中文版

本仓库是 [SpaceGroupUCL/depthmapX](https://github.com/SpaceGroupUCL/depthmapX) v0.10.0 的汉化分支：
在原版基础上增加了中文界面支持，其余功能与上游完全一致。

上游官方发行包**无法显示中文**——界面文案虽然都用 `tr()` 包裹，但从入口到主窗口都没有
安装 `QTranslator`，仓库里也没有任何 `.ts` 翻译源文件，所以放一个 `.qm` 进 `translations/`
目录也不会有任何效果。本分支补上了这条缺失的链路。

## 相对上游的改动

| 文件 | 改动 |
| --- | --- |
| `depthmapX/main.cpp` | 启动时加载 `qt_zh_CN`（Qt 自带标准对话框）与 `depthmapX_zh_CN.qm`（本项目界面） |
| `depthmapX/GraphDoc.cpp` | 两处拼接前缀 `"Shape Graphs: "` / `"Data Maps: "` 改为可翻译 |
| `translations/depthmapX_zh_CN.json` | 中文词典，源字符串 → 中文（约 560 条） |
| `translations/_part*.json` | 词典分片（按主题拆分，便于维护） |
| `tools/extract_strings.py` | 离线抽取界面文案，用于校验覆盖率 |
| `tools/fill_ts.py` | 把词典填入 `lupdate` 生成的 `.ts` |
| `tools/build_zh.py` | 合并分片 + 校验占位符/加速键/空格 |
| `.github/workflows/zh-cn.yml` | 在 GitHub Actions 上生成 `.qm` 并编译 Windows 版 |

翻译覆盖率：`653` 条源码文案中已翻译 `557` 条（另外 98 条是文件名后缀、内部标识符、
纯扩展名、许可证原文与 HTML 片段，故意保留英文，翻译它们会破坏文件命名或界面状态）。

## 如何构建

推送到 `zh-cn` 分支（或手动触发 `zh-cn windows build`）即可，产物在 Actions 的
artifact `depthmapX-zhCN-win64` 中。工作流内部依次执行：

```bash
lupdate -recursive depthmapX -ts i18n/depthmapX_zh_CN.ts   # 抽取文案
python tools/fill_ts.py i18n/depthmapX_zh_CN.ts translations/depthmapX_zh_CN.json
lrelease i18n/depthmapX_zh_CN.ts -qm i18n/depthmapX_zh_CN.qm
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --target depthmapX --parallel 4
```

需要 Qt 5.15.2（含 `qttools`，即 `lupdate`/`lrelease`）+ MSVC 2019/2022 + CMake ≥ 3.16。

## 使用

解压后直接运行 `depthmapX.exe`，界面即为简体中文。翻译文件位于
`translations/depthmapX_zh_CN.qm`，程序启动时按以下顺序查找：

1. `<exe 目录>/translations/depthmapX_zh_CN.qm`
2. `<exe 目录>/depthmapX_zh_CN.qm`
3. 编译期资源 `:/translations/depthmapX_zh_CN.qm`

**恢复英文界面**：删除或重命名 `depthmapX_zh_CN.qm`，或设置环境变量
`DEPTHMAPX_LANG=en` 后启动。

## 术语对照

按国内空间句法（Space Syntax）文献惯例固定，未逐条替换成意译：

| 英文 | 中文 |
| --- | --- |
| Axial | 轴线 |
| Segment | 线段 |
| Convex | 凸空间 |
| Pesh | Pesh（保留原名） |
| Isovist | 等视域 |
| Visibility Graph (VGA) | 视域图 |
| Integration | 整合度 |
| Choice | 选择度（介数） |
| Connectivity | 连接度 |
| Depth / Step Depth | 深度 / 步进深度 |
| Metric / Angular / Topological | 度量 / 角度 / 拓扑 |
| Agent | 智能体 |
| Occlusion | 遮挡 |
| Bin | 分区 |
| Fill / Pencil | 填充 / 铅笔 |
| Link / Unlink | 连接 / 断开连接 |
| Gate | 门 |
| Tulip | Tulip（保留原名） |

## 已知未汉化

- 关于对话框中的 HTML 富文本与 GPL 许可证原文（法律文本，保留原文更稳妥）；
- 少量内部标识符（`AttributesList`、`3DView` 等，用于保存界面布局状态）；
- 文件后缀与数据列名（`connectivity`、`points`、`links`、`mid` 等，参与文件命名，不能翻译）；
- 命令行工具 `depthmapXcli` 的输出（本分支只汉化图形界面）。

## 许可证

与上游一致，GPL v3。
