# 项目指南

## 代码风格
- 所有新建立的页面都在src\views新增，并且对应的在src\router编写对应的路由注册
- 所有新建立的页面对应的CSS代码都在src\assets\css新增，需要进行导入引用
- 本项目的数据库为mysql，数据库的域名、账号、密码配置均在src\settings.js，新增表结构等操作直接在create.sql中进行追加编写，严禁覆盖原有内容
- 本项目使用的组件是Element plus
- 严格遵循 Element Plus 官方设计规范和组件使用。所有 UI 交互元素（按钮、输入框、表单、弹窗、提示等）必须使用 Element Plus 组件（如 `<el-button>`, `<el-input>`），严禁使用原生 HTML 标签编写样式。参考文档：https://element-plus.org/en-US/component/overview，严禁二次封装 Element Plus 组件以及重写 Element Plus 组件的样式。
- 本项目是使用的python + Flask + Vue3的前后端架构，不可改变架构语言
- 在 models.py 定义新的表模型。
- 在 routes/ 下新建对应页面的 *_routes.py 文件写后端逻辑。
- 在 app.py 中注册新的蓝图。
- 所有的代码注释均采用中文，函数、类、方法等均需要添加注释，注释内容需中文描述其功能、参数、返回值等。
- 所有新增方法均需要检查是否符合项目的代码规范，是否存在重复代码、冗余代码等问题。
- 所有新增的字段定义均需要检查是否正确定义，是否正确引用。
- 在 Python 的 f-string（格式化字符串）中，花括号 {} 用于变量替换。如果在字符串中需要使用字面量的花括号（例如 CSS 样式块），必须使用双花括号 {{}} 进行转义。
- 所有的代码在定义了新的函数方法名称引用后，严格遵循逻辑进行函数方法构建，不得进行空引用。
- 当前代码已经实现 Celery + Redis，用于异步任务处理和消息队列。

## 架构
- 遵循仓储（Repository）模式
- 将业务逻辑放在服务层
- 项目的所有api服务逻辑都在src\api下进行对应页面功能的编写
- 项目的数据库为mysql，数据库的域名、账号、密码配置均在src\settings.js
- 项目的数据库表结构在create.sql中
- FastApi后端的结构需要和现有的 backend Flask结构一致，文件夹以及文件结构以及文件名要完整一一对应，不能有任何差异

## 权限模型
- 采用 RBAC（Role-Based Access Control）模型：用户 -> 角色 -> 菜单/按钮
- 支持按钮级权限控制，权限标识格式如 `system:user:add`
- 支持数据权限范围控制（全部、本部门、仅本人等）
- 核心表结构：
  - `sys_user`: 用户表
  - `sys_role`: 角色表
  - `sys_menu`: 菜单与按钮权限表（menu_type: M目录/C菜单/F按钮）
  - `sys_dept`: 部门表
- 预置角色：超级管理员、前端工程师、后端工程师、产品经理、测试工程师
