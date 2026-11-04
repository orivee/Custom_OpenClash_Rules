# 个人模板定制

本词汇表定义个人分流定制与上游模板之间的关系。

## Language

**上游模板**：随上游项目维护的 OpenClash 订阅转换模板，是个人模板的基础。

**个人模板**：在上游模板基础上加入 OneVoid、Samsung 等个人分流定制的 OpenClash 订阅转换模板。
_Avoid_: 上游模板

**OneVoid 定制**：针对 `onevoid.me` 域名的分流规则与出口选择策略，其中 `mail.onevoid.me` 始终直连，其余域名使用 OneVoid 策略组。

**OneVoid 策略组**：用于选择其余 `onevoid.me` 域名出口的策略组，提供手动选择、自动选择、地区节点、直连和订阅节点候选。

**Samsung 规则集**：由 Keviin560/Shunt_Rules 的 Samsung 分类定义的域名集合，用于识别需要统一选择出口的 Samsung 分类流量。

**Samsung 策略组**：用于选择 Samsung 规则集匹配流量出口的策略组，默认自动选择，也可切换直连、手动选择、地区节点和订阅节点。
