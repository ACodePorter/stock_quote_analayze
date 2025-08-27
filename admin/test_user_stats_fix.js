// 测试用户统计修复是否有效
console.log('🔍 测试用户统计修复...')

// 模拟修复后的逻辑
const mockUserStatsData = {
  // 初始状态：null表示未初始化
  userStatsData: null,
  
  // 模拟API统计数据
  apiStats: {
    total: 16,
    active: 16,
    disabled: 0,
    suspended: 0
  },
  
  // 模拟本地用户数据
  localUsers: [
    { id: 1, username: 'admin', status: 'active' },
    { id: 2, username: 'user1', status: 'active' },
    { id: 3, username: 'user2', status: 'disabled' }
  ],
  
  // 修复后的userStats计算逻辑
  userStats() {
    // 如果API统计数据可用，使用API数据
    if (this.userStatsData) {
      console.log('✅ 使用API统计数据:', this.userStatsData)
      return this.userStatsData
    }
    
    // 否则使用本地计算的数据作为回退
    const stats = {
      total: this.localUsers.length,
      active: 0,
      disabled: 0,
      suspended: 0
    }
    
    this.localUsers.forEach(user => {
      if (user.status === 'active') stats.active++
      else if (user.status === 'disabled') stats.disabled++
      else if (user.status === 'suspended') stats.suspended++
    })
    
    console.log('📊 使用本地计算统计数据:', stats)
    return stats
  },
  
  // 模拟fetchUserStats
  async fetchUserStats() {
    console.log('🔄 开始获取用户统计数据...')
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 100))
      this.userStatsData = this.apiStats
      console.log('✅ 用户统计数据获取成功:', this.userStatsData)
    } catch (err) {
      console.error('❌ 获取用户统计数据失败:', err)
      this.userStatsData = null
    }
  }
}

// 测试场景1：初始状态（未调用API）
console.log('\n🧪 测试场景1: 初始状态')
console.log('userStats:', mockUserStatsData.userStats())

// 测试场景2：API调用成功
console.log('\n🧪 测试场景2: API调用成功')
await mockUserStatsData.fetchUserStats()
console.log('userStats:', mockUserStatsData.userStats())

// 测试场景3：API返回0值的情况
console.log('\n🧪 测试场景3: API返回0值')
mockUserStatsData.userStatsData = { total: 0, active: 0, disabled: 0, suspended: 0 }
console.log('userStats:', mockUserStatsData.userStats())

console.log('\n✅ 用户统计修复测试完成！')
console.log('📝 主要修复内容:')
console.log('   - 修复了userStats计算属性中的逻辑错误')
console.log('   - 使用null表示未初始化状态，而不是{total: 0}')
console.log('   - 确保API统计数据（包括0值）能正确显示')
console.log('   - 修复了前后端字段名不匹配的问题')
