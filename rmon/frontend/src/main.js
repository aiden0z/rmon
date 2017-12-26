import Vue from 'vue'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-default/index.css'

import VueRouter from 'vue-router'
import VueResource from 'vue-resource'
import Moment from 'vue-moment'

import App from './App.vue'
import Server from './views/Server.vue'
import Metric from './views/Metric.vue'

Vue.use(VueRouter)
Vue.use(ElementUI)
Vue.use(VueResource)
Vue.use(Moment)

const routes = [
  // 访问 / 时重定向到 /servers/ 
  {path: '/', redirect: '/servers/'},
  {path: '/servers/', name: 'servers', component: Server}, 
  {path: '/servers/:serverId', name: 'metric', component: Metric}
]

const router = new VueRouter({routes: routes})

new Vue({
  el: '#app',
  router: router,
  render: h => h(App)
})
