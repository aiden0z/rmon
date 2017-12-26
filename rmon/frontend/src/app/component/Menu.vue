<template>
  <el-col class="menu">
    <el-menu :default-active="this.$route.path"mode="horizontal" router>
      <el-menu-item index="/users/">
        用户管理
      </el-menu-item>
      <el-menu-item index="/servers/">
        服务器管理
      </el-menu-item>
      <li class="el-menu-item pull-right" @click="logout">
        退出
      </li>
    </el-menu>
  </el-col>
</template>

<script>
export default {
  name: 'Menu',
  methods: {
    // 退出登录
    logout() {
      sessionStorage.removeItem('RMON_TOKEN')
      this.$router.push({name: 'login'})
    }
  }
}
</script>

<style scoped>

.menu-link {
    text-decoration: none;
}

.menu {
  margin-bottom: 15px;
}

.pull-right {
  float: right;
}

</style>