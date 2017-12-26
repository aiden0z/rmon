<template>
  <div id="app" class="container">
    <el-row>
      <el-col :span="20" :offset="2">
        <router-view></router-view>
      </el-col>
    </el-row>
     </div>
  </div>
</template>

<script>
</script>

<style>

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  margin-top: 60px;
}
</style>