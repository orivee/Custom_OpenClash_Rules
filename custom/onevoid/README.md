# OneVoid 个人模板

上游标准模板为 `cfg/Custom_Clash.ini`，个人模板为本目录的
`Custom_Clash.ini`。独立脚本 `py/apply_onevoid.py` 只读取本地上游模板，
不联网、不修改上游文件、不自动提交。

## 规则

两条规则优先于上游规则，按以下顺序匹配：

1. `mail.onevoid.me` 使用 `🎯 全球直连`。
2. `onevoid.me` 及其余子域名使用 `🌌 OneVoid` 策略组。

OneVoid 策略组提供手动选择、自动选择、香港、美国、日本、新加坡、
台湾、韩国、全球直连和订阅节点候选；默认候选为手动选择。
其他规则、策略组和测速设置跟随上游标准版。

## 同步与生成

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
改变分段结构或引入 OneVoid 定制时，脚本报错并保留原个人模板。
检查不能判断所有上游变化是否兼容，例如同名策略组的行为变化仍需人工审查。

确认生成结果后，可自行提交独立脚本、说明、测试与个人模板。
后续更新同样先合并上游，再运行脚本并检查差异。
不要直接编辑生成的个人模板；需要调整定制时修改独立脚本并重新生成。

## 使用模板

在 OpenClash 的在线订阅转换设置中，将模板地址改为你发布的个人分支下
`custom/onevoid/Custom_Clash.ini` 的 Raw 地址。例如 GitHub 仓库对应：

```text
https://raw.githubusercontent.com/<owner>/<repo>/refs/heads/onevoid-custom/custom/onevoid/Custom_Clash.ini
```

远程地址可用需要先提交并推送相应分支。更新订阅后，确认 OneVoid 策略组
及其候选正常加载，再分别验证邮件域名和其他 OneVoid 域名的实际分流。
脚本检查通过只代表模板生成一致，不代表订阅转换、运行配置或实际网络
分流已验收。

## 维护范围与迁移

本目录仅提供 OpenClash 标准版个人模板，不生成 Stash 或其他版本。
旧 `main` 分支及其原有本地提交保留供查阅；`onevoid-custom` 从
`origin/main` 的 `c86aff34da6b7f9233e9b609ff5ed91155d74938` 开始，
不重放旧定制提交，不带回旧 Stash 生成器或个人定时同步工作流。
上游原有脚本、模板、说明和工作流保持原样。

## 本地验证

```bash
python -B -m unittest discover -s custom/onevoid -p 'test_*.py'
python -B py/apply_onevoid.py --check
git diff --check
```
