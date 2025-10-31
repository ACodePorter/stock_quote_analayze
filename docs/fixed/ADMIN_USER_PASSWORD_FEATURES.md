# 管理端用户密码功能新增

本次改动为管理端-用户管理模块新增二项功能：

- 修改用户密码（管理员直接设置新密码）
- 初始化用户密码（重置为默认值：`bingfengtang$91`）

## 后端

- 新增路由：`/api/admin/users/{user_id}/password` PUT
  - 请求体：`{ "new_password": "<新密码>" }`
  - 返回：`{ "message": "密码修改成功" }`

- 新增路由：`/api/admin/users/{user_id}/password/reset` POST
  - 默认密码：`bingfengtang$91`
  - 返回：`{ "message": "密码已重置为默认值", "default": "bingfengtang$91" }`

## 前端

- `用户管理`页面操作列：新增“修改密码”“初始化密码”。
- “修改密码”弹窗可直接输入新密码并提交。
- “初始化密码”提供确认提示。

## 影响范围

- 后端：`backend_api/admin/users.py`
- 前端服务：`admin/src/services/users.service.ts`
- 前端状态：`admin/src/stores/users.ts`
- 前端页面：`admin/src/views/UsersView.vue`

## 使用说明

1. 登录管理端，进入“用户管理”。
2. 在用户行“更多”下拉菜单选择“修改密码”或“初始化密码”。
3. 初始化密码默认值：`bingfengtang$91`。


