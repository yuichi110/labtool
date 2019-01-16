import Vue from 'vue'
import Router from 'vue-router'
import IndexView from '@/views/IndexView'
import ClusterDetailView from '@/views/ClusterDetailView'
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'IndexView',
      component: IndexView,
    },
    {
      path: '/cluster/:id',
      name: 'ClusterDetailView',
      component: ClusterDetailView,
    },
  ]
})
