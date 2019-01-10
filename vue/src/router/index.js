import Vue from 'vue'
import Router from 'vue-router'
import Index from '@/views/Index'
import Cluster from '@/views/Cluster'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Index',
      component: Index,
    },
    {
      path: '/cluster/:id',
      name: 'Cluster',
      component: Cluster,
    },
  ]
})
