<template>
  <div class="logs-pagination">
    <el-pagination
      :current-page="current"
      :page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup lang="ts">
interface Props {
  current: number
  pageSize: number
  total: number
}

interface Emits {
  (e: 'update:current', value: number): void
  (e: 'update:pageSize', value: number): void
  (e: 'change', page: number, pageSize: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 处理页码变化
const handleCurrentChange = (page: number) => {
  emit('update:current', page)
  emit('change', page, props.pageSize)
}

// 处理每页条数变化
const handleSizeChange = (size: number) => {
  emit('update:pageSize', size)
  emit('change', 1, size) // 重置到第一页
}
</script>

<style scoped>
.logs-pagination {
  @apply flex justify-center mt-6;
}
</style> 