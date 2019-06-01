import Vue from 'vue'
import Router from 'vue-router'
import IndexView from '@/views/IndexView'
import ClusterListView from '@/views/ClusterListView'
import ClusterDetailView from '@/views/ClusterDetailView'
import AssetListView from '@/views/AssetListView'
import AssetDetailView from '@/views/AssetDetailView'
import SegmentListView from '@/views/SegmentListView'
import SegmentDetailView from '@/views/SegmentDetailView'

import TaskListView from '@/views/TaskListView'

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
      name: 'ClusterListView',
      component: ClusterListView,
    },
    {
      path: '/clusters/:uuid',
      name: 'ClusterDetailView',
      component: ClusterDetailView,
    },

    {
      path: '/assets',
      name: 'AssetListView',
      component: AssetListView,
    },
    {
      path: '/assets/:uuid',
      name: 'AssetDetailView',
      component: AssetDetailView,
    },

    {
      path: '/segments',
      name: 'SegmentListView',
      component: SegmentListView,
    },
    {
      path: '/segments/:uuid',
      name: 'SegmentDetailView',
      component: SegmentDetailView,
    },
    {
      path: '/tasks',
      name: 'TaskListView',
      component: TaskListView,
    },
  ]
})
