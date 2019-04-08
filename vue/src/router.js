import Vue from 'vue'
import Router from 'vue-router'
import IndexView from '@/views/IndexView'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'IndexView',
      component: IndexView,
    },
    {
      path: '/clusters',
      name: 'ClusterView',
      component: IndexView,
    },
    {
      path: '/assets',
      name: 'AssetView',
      component: IndexView,
    },
    {
      path: '/segments',
      name: 'SegmentView',
      component: IndexView,
    },
  ]
})
