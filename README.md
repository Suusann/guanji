# 观己 · Agent 使用说明

**Slogan**：应无所住而生其心
**一句话**：把每一次冥想，观成一幅内在风景。

## 这是什么

「观己」是一个高保真的移动端冥想 App 原型。它根据你的心率、呼吸节奏、情绪、音乐、当前所处环境与期望到达的环境，为你生成一幅属于此刻的「心境画」。

原型完全使用原生 HTML / CSS / JavaScript，不依赖任何 CDN、后端或外部图片，本地即可运行。

## 目录结构

```
观己/
├── index.html                      单页面结构与样式
├── app.js                          交互、计时、音乐、心境画生成
├── assets/
│   ├── guqin-spring.m4a            中式水韵 · 李祥霆 · 春风又绿江南岸
│   ├── wuxing-jin-xiyangxiaogu.m4a 五行 · 金 · 夕阳箫鼓
│   ├── wuxing-mu-manliuban.m4a     五行 · 木 · 慢六板
│   ├── wuxing-shui-liushuixingyun.m4a 五行 · 水 · 流水行云
│   ├── wuxing-huo-caiyunzhuiyue.m4a 五行 · 火 · 彩云追月
│   ├── wuxing-tu-shimianmaifu.m4a  五行 · 土 · 十面埋伏
│   ├── japan-haru-no-umi.m4a       日本留白 · 吉村七重 · Haru no Umi
│   ├── west-mozart-k448-andante.m4a 欧美氛围 · 莫扎特 K.448 II. Andante
│   └── bali-bacchanale.m4a         印尼流光 · Sanggar Ceraken of Bali · Bacchanale
└── avatar.jpg                      Agent 头像
```

> 注：印尼流光曲目为 John Cage《Bacchanale》（预备钢琴），由 Sanggar Ceraken of Bali 演绎，源 FLAC 已转为 AAC 内置，可直接试听。

## 本地启动

任意一个静态服务器都可以，不要直接双击 `index.html`（浏览器会阻止本地音频加载）。

```bash
cd 观己
python3 -m http.server 8765
```

浏览器打开 `http://127.0.0.1:8765/index.html` 即可。

## 在线访问（GitHub Pages）

固定地址，永久有效，手机可直接打开：

**https://suusann.github.io/guanji/**

- 源码仓库：https://github.com/Suusann/guanji
- 托管分支：`main` 根目录，纯静态、无需构建
- 更新方式：改完代码后

```bash
git add -A && git commit -m "update" && git push
```

推送后约 1 分钟线上自动生效（Actions → pages build and deployment 可看构建进度）。

## 使用流程

1. **首页**：查看今日心境推荐，右上角金色 ＋ 号可以导入你自己的本地音乐；三个「放松 / 专注 / 睡前」快捷键切换文案与推荐主题。
2. **准备页**：选择时长、意图、当前所处、想去往的环境，以及音乐主题。
   - 选中「五行灵感」后会展开金木水火土 5 个子选项，颜色对应五行。
   - 播放器（深墨绿 → 金色渐变）可以试听所选曲目。
3. **冥想页**：进入后底部导航自动隐藏，屏幕底部固定「暂停 / 结束」两个按钮；倒计时按系统真实时间运行；呼吸阶段固定 4-7-8。
4. **结束报告**：查看心率变化、生成心境画。
5. **心境画**：根据音乐风格决定画风，节奏决定笔触细腻度。
   - 中式水韵 / 五行灵感 → 国风水墨
   - 日本留白 → 日本画
   - 印尼流光 → 印尼海洋椰林
   - 欧美氛围 → 油画

## 常见操作

- **换音乐**：准备页音乐主题卡片直接切；或右上角 ＋ 号导入本地 mp3。
- **暂停/继续**：冥想页底部左侧按钮，或播放器上的圆形按钮。
- **收藏心境画**：结束报告 → 生成心境画 → 收藏画作。

## 已知限制

- 心率、连续静坐天数为原型演示数据，未接入真实健康数据。
- 音乐版权归各自权利人所有，本原型仅作演示，请勿用于公开分发。
