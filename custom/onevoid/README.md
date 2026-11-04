# OneVoid / Samsung 个人模板

上游标准模板为 `cfg/Custom_Clash.ini`，个人模板为本目录的
`Custom_Clash.ini`。独立脚本 `py/apply_onevoid.py` 只读取本地上游模板，
不联网、不修改上游文件、不自动提交。

## 规则

个人规则优先于上游规则，按以下顺序匹配：

1. `mail.onevoid.me` 使用 `🎯 全球直连`。
2. `onevoid.me` 及其余子域名使用 `🌌 OneVoid` 策略组。
3. Samsung 规则集中的域名使用 `📱 Samsung` 策略组。

OneVoid 策略组提供手动选择、自动选择、香港、美国、日本、新加坡、
台湾、韩国、全球直连和订阅节点候选；默认候选为手动选择。

Samsung 策略组默认候选为 `♻️ 自动选择`，也可选择全球直连、手动选择、
香港、美国、日本、新加坡、台湾、韩国或具体订阅节点。
需要直连时，在 OpenClash 中将 `📱 Samsung` 切换为 `🎯 全球直连`。
默认候选用于首次加载或没有已保存选择时，客户端可能保留已有的策略组选择。

Samsung 域名完整跟随 [Keviin560/Shunt_Rules 的 Samsung 分类](https://github.com/Keviin560/Shunt_Rules)，
通过远程 `clash-domain` 引用其
[`Samsung.mrs`](https://raw.githubusercontent.com/Keviin560/Shunt_Rules/main/rule/Mihomo/Samsung.mrs)，
规则提供器更新间隔为 86400 秒（24 小时）。生成脚本只写入引用地址，
不下载或复制第三方规则；运行设备需能获取这个 GitHub Raw 地址。
Samsung 分类范围由规则源维护，可能包含非三星品牌域名，例如可读列表中的
`anrdoezrs.net` 和 `game-platform.net`，本模板不另行筛选。

其他规则、策略组和测速设置跟随上游标准版。

## GitHub 自动同步

GitHub 仓库为 `orivee/Custom_OpenClash_Rules`，默认分支为 `main`。
新增工作流 `.github/workflows/sync-onevoid-upstream.yml` 每两小时运行
一次（UTC 偶数小时的第 17 分钟，北京时间同为偶数小时第 17 分钟），
也支持手动触发；推送 `main` 时同样运行。

每次运行按顺序完成：

1. 将 `Aethersailor/Custom_OpenClash_Rules` 的 `main` 合并到 fork 的 `main`。
2. 将最新 `main` 合并到 `onevoid-custom`，重新生成个人模板。
3. 运行测试与一致性检查，通过后提交并推送个人分支。

`main` 只新增这份同步工作流，上游原有文件保持原样。同步使用普通合并，
不强制覆盖分支；冲突、生成或测试失败时任务失败，不推送未完成的个人分支。
无变化时不创建提交。两阶段在同一工作流中串联，使用本仓库专用的可写
Deploy Key；私钥保存在 Actions Secret `ONEVOID_SYNC_SSH_KEY` 中，
不进入 Git。内置 `GITHUB_TOKEN` 只授予读取权限，不使用个人 PAT。
Deploy Key 用于允许同步上游工作流文件；它仅能访问这一个仓库。
自动更新 `main` 的推送也会排队触发一次运行，内容已同步时不产生新提交，
因此不会持续递归。工作流队列串行执行两条分支的更新。

fork 中的上游规则生成、游戏 CDN 更新、Dependabot 自动合并工作流被停用，
避免它们独立改写 `main`；需要的上游生成结果随上游合并进入。
工作流文件本身保留不改。新增上游自动写入工作流时，应重新核对启用状态。

手动补跑或查看记录：

```bash
gh workflow run sync-onevoid-upstream.yml --ref main --repo orivee/Custom_OpenClash_Rules
gh run list --workflow sync-onevoid-upstream.yml --repo orivee/Custom_OpenClash_Rules
```

## 本地同步与生成

在仓库根目录的 `onevoid-custom` 分支执行，先保存自己的未提交改动：

```bash
git fetch origin
git merge origin/main
python py/apply_onevoid.py
python py/apply_onevoid.py --check
```

同步上游成功后再执行生成命令；合并如有冲突，先解决冲突。
本流程以 `origin/main` 已包含需要的上游更新为前提。

输出内容相同时，脚本不重新写文件。`--check` 不写文件：个人模板缺失、
过期或上游不兼容时返回非零退出码。上游缺少所需策略组、存在重复组名、
改变分段结构或引入 OneVoid / Samsung 定制时，脚本报错并保留原个人模板。
检查不能判断所有上游变化是否兼容，例如同名策略组的行为变化仍需人工审查。

确认生成结果后，可自行提交独立脚本、说明、测试与个人模板。
后续更新同样先合并上游，再运行脚本并检查差异。
不要直接编辑生成的个人模板；需要调整定制时修改独立脚本并重新生成。

## 使用模板

在 OpenClash 的在线订阅转换设置中，将模板地址改为你发布的个人分支下
`custom/onevoid/Custom_Clash.ini` 的 Raw 地址。例如 GitHub 仓库对应：

```text
https://raw.githubusercontent.com/orivee/Custom_OpenClash_Rules/refs/heads/onevoid-custom/custom/onevoid/Custom_Clash.ini
```

远程地址可用需要先提交并推送相应分支。更新订阅后，确认 OneVoid 策略组
及 Samsung 策略组和候选正常加载，确认 Samsung 规则提供器加载成功，
再分别验证邮件域名、其他 OneVoid 域名和 Samsung 域名的实际分流。
脚本检查通过只代表模板生成一致，不代表订阅转换、运行配置或实际网络
分流已验收。

## 维护范围与迁移

本目录仅提供 OpenClash 标准版个人模板，不生成 Stash 或其他版本。
旧 `main` 分支及其原有本地提交保留供查阅；`onevoid-custom` 从
`origin/main` 的 `c86aff34da6b7f9233e9b609ff5ed91155d74938` 开始，
不重放旧定制提交，不带回旧 Stash 生成器或旧个人定时同步工作流。
上游原有脚本、模板、说明和工作流保持原样；同步功能来自独立新增工作流。

## 本地验证

```bash
python -B -m unittest discover -s custom/onevoid -p 'test_*.py'
python -B py/apply_onevoid.py --check
git diff --check
```
