# Кинотека · A 方案改版依据

## 从公开资料核对的原则

- **Nielsen Norman Group** 的 Therese Fessenden 指出，界面上低信息量的内容会和任务信息争夺注意力。她建议用视觉层级突出必要内容，节制地使用字体、颜色和装饰。[Aesthetic and Minimalist Design](https://www.nngroup.com/articles/aesthetic-minimalist-design/)
- **GitHub Primer** 的 ActionList 指南用分组标题和分隔线帮助浏览侧栏。列表图标可以标示不同对象或状态，同一类型已由上下文说明时可以省去重复图标。[ActionList Guidelines](https://primer.style/product/components/action-list/guidelines/)
- **IBM Carbon** 把搜索、筛选、主要操作放在数据表的工具栏，并为密度不同的表格提供统一的行高规则。数据表应占用足够的主内容宽度，长记录的更多信息可以按需展开。[Data Table Guidelines](https://www.carbondesignsystem.com/building-blocks/core/components/data-table/guidelines)
- **GOV.UK Design System** 建议每页保持一个突出的主要操作，用具体动词说明按钮的结果，并以不同样式呈现次要操作。[Button](https://design-system.service.gov.uk/components/button/)
- **英国电影协会（BFI）国家档案馆** 的目录支持按片名和人名查找，档案记录包含片名、片长和演职员等字段。它的检索指南还介绍了用层级浏览器在同一档案集合内定位条目。[Collections Search 指南](https://www.bfi.org.uk/bfi-national-archive/screencraft/guide-using-collections-search) · [Filmography FAQ](https://www.bfi.org.uk/bfi-national-archive/search-bfi-archive/bfi-filmography/bfi-filmography-faq)
- **Apple Human Interface Guidelines** 说明，侧栏、记录列表和详情可以并排展示。应持续标明选中的记录，明确列表与详情的关系。窄屏需要重新安排内容，避免多栏并排造成挤压。[Split views](https://developer.apple.com/design/human-interface-guidelines/split-views?changes=_3_5&language=objc)

## 在 Demo 里的设计取舍

三版都沿用 A 的「馆藏 / 工具」导航分组。对原版的判断是，大幅胶片横幅、重复的影片图标和彩色类型胶囊分散了对电影记录的注意力。改版把视觉重点移到片名、筛选和操作状态上，并让「Добавить фильм」成为目录的主要操作，导入仍可从工具分组进入。

- **A1 · 数据登记册**。把电影表和它的工具放在首屏。类型用文字，表格负责横向比较，详情按需查看。
- **A2 · 纸本索引**。用类型分组和细横线组织记录，片名、片长和导演形成主要阅读顺序。纸本感和按类型分组是本项目对电影档案的设计取舍。
- **A3 · 双栏工作台**。在同一界面切换影片和查看详情，突出当前选中项。适合逐条复核，窄屏时点选记录单独打开详情。
