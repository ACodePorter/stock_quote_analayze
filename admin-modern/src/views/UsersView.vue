<template>
  <div class="users-view">
    <div class="page-header">
      <h1>用户管理</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增用户
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><User /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userStats.total }}</div>
                <div class="stat-label">总用户数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon active">
                <el-icon><Check /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userStats.active }}</div>
                <div class="stat-label">活跃用户</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon inactive">
                <el-icon><Close /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userStats.inactive }}</div>
                <div class="stat-label">禁用用户</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon suspended">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ userStats.suspended }}</div>
                <div class="stat-label">暂停用户</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-section">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索用户名或邮箱"
            :prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="statusFilter"
            placeholder="状态筛选"
            clearable
            @change="handleStatusFilter"
          >
            <el-option label="全部" value="" />
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="暂停" value="suspended" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="roleFilter"
            placeholder="角色筛选"
            clearable
            @change="handleRoleFilter"
          >
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="用户" value="user" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <div class="actions">
            <el-button @click="refreshUsers">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 用户表格 -->
    <el-card class="table-section">
      <el-table
        :data="filteredUsers"
        :loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag
              :type="getRoleTagType(row.role)"
              size="small"
            >
              {{ getRoleText(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag
              :type="getStatusTagType(row.status)"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="160">
          <template #default="{ row }">
            {{ row.last_login ? formatDate(row.last_login) : '从未登录' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              @click="editUser(row)"
            >
              编辑
            </el-button>
            <el-dropdown @command="(action) => handleUserAction(action, row)">
              <el-button size="small" type="primary">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-if="row.status === 'active'"
                    command="disable"
                  >
                    禁用
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="row.status !== 'active'"
                    command="enable"
                  >
                    启用
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-if="row.status !== 'suspended'"
                    command="suspend"
                  >
                    暂停
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建用户对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="新增用户"
      width="500px"
      @close="resetCreateForm"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="createForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="createForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" placeholder="选择用户角色">
            <el-option label="用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleCreateUser">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑用户"
      width="500px"
      @close="resetEditForm"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="editForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="editForm.role" placeholder="选择用户角色">
            <el-option label="用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="editForm.status" placeholder="选择用户状态">
            <el-option label="活跃" value="active" />
            <el-option label="禁用" value="inactive" />
            <el-option label="暂停" value="suspended" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleUpdateUser">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Refresh,
  User,
  Check,
  Close,
  Warning,
  ArrowDown
} from '@element-plus/icons-vue'
import { useUsersStore } from '@/stores/users'
import type { User as UserType, CreateUserRequest, UpdateUserRequest } from '@/types/users.types'
import type { FormInstance, FormRules } from 'element-plus'

const usersStore = useUsersStore()

// Refs
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()

// State
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const searchKeyword = ref('')
const statusFilter = ref('')
const roleFilter = ref('')
const currentEditUser = ref<UserType | null>(null)

// Forms
const createForm = ref<CreateUserRequest>({
  username: '',
  email: '',
  password: '',
  role: 'user'
})

const editForm = ref<UpdateUserRequest & { username: string }>({
  username: '',
  email: '',
  role: 'user',
  status: 'active'
})

// Form rules
const createRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ]
}

const editRules: FormRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择用户角色', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择用户状态', trigger: 'change' }
  ]
}

// Computed
const { 
  users, 
  loading, 
  total, 
  currentPage, 
  pageSize,
  filteredUsers,
  userStats
} = usersStore

// Methods
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString()
}

const getRoleText = (role: string) => {
  const roleMap = {
    admin: '管理员',
    user: '用户',
    guest: '访客'
  }
  return roleMap[role as keyof typeof roleMap] || role
}

const getRoleTagType = (role: string) => {
  const typeMap = {
    admin: 'danger',
    user: 'primary',
    guest: 'info'
  }
  return typeMap[role as keyof typeof typeMap] || ''
}

const getStatusText = (status: string) => {
  const statusMap = {
    active: '活跃',
    inactive: '禁用',
    suspended: '暂停'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getStatusTagType = (status: string) => {
  const typeMap = {
    active: 'success',
    inactive: 'danger',
    suspended: 'warning'
  }
  return typeMap[status as keyof typeof typeMap] || ''
}

const handleSearch = () => {
  usersStore.setSearchKeyword(searchKeyword.value)
}

const handleStatusFilter = () => {
  // 实现状态筛选逻辑
  usersStore.fetchUsers()
}

const handleRoleFilter = () => {
  // 实现角色筛选逻辑
  usersStore.fetchUsers()
}

const refreshUsers = () => {
  usersStore.fetchUsers()
}

const handleSizeChange = (size: number) => {
  usersStore.setPageSize(size)
}

const handleCurrentChange = (page: number) => {
  usersStore.setPage(page)
}

const resetCreateForm = () => {
  createForm.value = {
    username: '',
    email: '',
    password: '',
    role: 'user'
  }
  createFormRef.value?.resetFields()
}

const resetEditForm = () => {
  editForm.value = {
    username: '',
    email: '',
    role: 'user',
    status: 'active'
  }
  editFormRef.value?.resetFields()
  currentEditUser.value = null
}

const handleCreateUser = async () => {
  if (!createFormRef.value) return
  
  try {
    await createFormRef.value.validate()
    await usersStore.createUser(createForm.value)
    showCreateDialog.value = false
    resetCreateForm()
  } catch (error) {
    console.error('创建用户失败:', error)
  }
}

const editUser = (user: UserType) => {
  currentEditUser.value = user
  editForm.value = {
    username: user.username,
    email: user.email,
    role: user.role,
    status: user.status
  }
  showEditDialog.value = true
}

const handleUpdateUser = async () => {
  if (!editFormRef.value || !currentEditUser.value) return
  
  try {
    await editFormRef.value.validate()
    const { username, ...updateData } = editForm.value
    await usersStore.updateUser(currentEditUser.value.id, updateData)
    showEditDialog.value = false
    resetEditForm()
  } catch (error) {
    console.error('更新用户失败:', error)
  }
}

const handleUserAction = async (action: string, user: UserType) => {
  try {
    switch (action) {
      case 'enable':
        await usersStore.updateUserStatus(user.id, 'active')
        break
      case 'disable':
        await usersStore.updateUserStatus(user.id, 'inactive')
        break
      case 'suspend':
        await usersStore.updateUserStatus(user.id, 'suspended')
        break
      case 'delete':
        await ElMessageBox.confirm(
          `确定要删除用户 "${user.username}" 吗？此操作不可恢复。`,
          '确认删除',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        await usersStore.deleteUser(user.id)
        break
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

// Lifecycle
onMounted(() => {
  usersStore.fetchUsers()
})
</script>

<style scoped>
.users-view {
  padding: 24px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 20px;
}

.stat-icon.total {
  background-color: rgb(219 234 254);
  color: rgb(37 99 235);
}

.stat-icon.active {
  background-color: rgb(220 252 231);
  color: rgb(22 163 74);
}

.stat-icon.inactive {
  background-color: rgb(254 226 226);
  color: rgb(220 38 38);
}

.stat-icon.suspended {
  background-color: rgb(254 249 195);
  color: rgb(202 138 4);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.search-section {
  margin-bottom: 24px;
}

.actions {
  text-align: right;
}

.table-section {
  margin-bottom: 24px;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style> 