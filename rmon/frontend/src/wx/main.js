import Vue from 'vue'

import VueResource from 'vue-resource'
// 引入 weui 组件
import WeVue from 'we-vue'

// 主页面
import App from './App.vue'

// 注册各种插件
Vue.use(VueResource)
Vue.use(WeVue)

new Vue({
  el: '#app',
  render: h => h(App),
})
