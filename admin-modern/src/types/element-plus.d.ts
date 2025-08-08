// Element Plus 全局组件类型声明
// 解决模板中 <el-*> 组件的类型报错（TS2339）
import type { Component } from 'vue'

declare module 'vue' {
  export interface GlobalComponents {
    ElRow: typeof import('element-plus/es')['ElRow']
    ElCol: typeof import('element-plus/es')['ElCol']
    ElCard: typeof import('element-plus/es')['ElCard']
    ElIcon: typeof import('element-plus/es')['ElIcon']
    ElAvatar: typeof import('element-plus/es')['ElAvatar']

    ElForm: typeof import('element-plus/es')['ElForm']
    ElFormItem: typeof import('element-plus/es')['ElFormItem']
    ElInput: typeof import('element-plus/es')['ElInput']
    ElSelect: typeof import('element-plus/es')['ElSelect']
    ElOption: typeof import('element-plus/es')['ElOption']
    ElDatePicker: typeof import('element-plus/es')['ElDatePicker']
    ElButton: typeof import('element-plus/es')['ElButton']

    ElTable: typeof import('element-plus/es')['ElTable']
    ElTableColumn: typeof import('element-plus/es')['ElTableColumn']
    ElPagination: typeof import('element-plus/es')['ElPagination']
    ElDialog: typeof import('element-plus/es')['ElDialog']
    ElTag: typeof import('element-plus/es')['ElTag']

    ElTabs: typeof import('element-plus/es')['ElTabs']
    ElTabPane: typeof import('element-plus/es')['ElTabPane']
    ElAlert: typeof import('element-plus/es')['ElAlert']
    ElTimeline: typeof import('element-plus/es')['ElTimeline']
    ElTimelineItem: typeof import('element-plus/es')['ElTimelineItem']
    ElDropdown: typeof import('element-plus/es')['ElDropdown']
    ElDropdownMenu: typeof import('element-plus/es')['ElDropdownMenu']
    ElDropdownItem: typeof import('element-plus/es')['ElDropdownItem']
  }
}

export {}
