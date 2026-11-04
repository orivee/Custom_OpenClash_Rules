# OneVoid 模板定制

本词汇表定义个人分流定制与上游模板之间的关系。

## Language

**上游模板**：随上游项目维护的 OpenClash 订阅转换模板，是个人模板的基础。

**个人模板**：在上游模板基础上加入 OneVoid 定制的 OpenClash 订阅转换模板。
_Avoid_: 上游模板

**OneVoid 定制**：针对 `onevoid.me` 域名的分流规则与出口选择策略，其中 `mail.onevoid.me` 始终直连，其余域名使用 OneVoid 策略组。

**OneVoid 策略组**：用于选择其余 `onevoid.me` 域名出口的策略组，提供手动选择、自动选择、地区节点、直连和订阅节点候选。
