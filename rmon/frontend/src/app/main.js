import Vue from 'vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-default/index.css'

import VueRouter from 'vue-router'
import VueResource from 'vue-resource'
import Moment from 'vue-moment'

// 各个页面
import App from './App.vue'
import Server from './views/Server.vue'
import Metric from './views/Metric.vue'
import User from './views/User.vue'
import Login from './views/Login.vue'

// 组件
import Menu from './component/Menu.vue'

// 注册组件
Vue.component('Menu', Menu)

// 注册各种插件
Vue.use(VueRouter)
Vue.use(ElementUI)
Vue.use(VueResource)
Vue.use(Moment)

const routes = [
  // 访问 / 时重定向到 /servers/ 
  {path: '/', redirect: '/servers/'},
  {path: '/servers/', name: 'servers', component: Server}, 
  {path: '/servers/:serverId/metrics', name: 'metric', component: Metric},
  {path: '/users/', name: 'users', component: User},
  {path: '/login', name: 'login', component: Login}
]

const router = new VueRouter({routes: routes})

// 设置 Vue-Resource 每次发起请求时携带的头部
Vue.http.interceptors.push((request, next) => {

  if (request.url != '/login') {
    request.headers.set('Authorization', `JWT ${sessionStorage.getItem('RMON_TOKEN')}`)
  }

  // 检测返回代码, 如果返回代码是 401 或者 403 则认为未认证需要跳转到登录页面
  next((resp) => {
    if (resp.status == 401 || resp.status == 403) {
      router.push('/login')
    }
  })
})

new Vue({
  el: '#app',
  router: router,
  render: h => h(App),
  methods: {
    checkLogin() {

      console.log(this.$route)
      if (!(sessionStorage.getItem('RMON_TOKEN'))) {
        this.$router.push('/login')
      } else if (this.$route.name == 'login') {
        this.$router.push('/servers')
      }
    }
  },

  created() {
    this.checkLogin()
  },

  watch: {
    "$router": 'checkLogin'
  }
})
