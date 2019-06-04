import Vue from 'vue'
import Router from 'vue-router'
import IndexView from '@/views/IndexView'
import ClusterListView from '@/views/ClusterListView'
import ClusterDetailView from '@/views/ClusterDetailView'
import AssetListView from '@/views/AssetListView'
import AssetDetailView from '@/views/AssetDetailView'
import SegmentListView from '@/views/SegmentListView'
import SegmentDetailView from '@/views/SegmentDetailView'
import AnsibleView from '@/views/AnsibleView'
import TaskListView from '@/views/TaskListView'

const DEFAULT_TITLE = 'Founder';

Vue.use(Router)

const router = new Router({
  routes: [
    {
      path: '/',
      name: 'IndexView',
      component: IndexView,
      meta: { title: 'Home' }
    },

    {
      path: '/clusters',
      name: 'ClusterListView',
      component: ClusterListView,
      meta: { title: 'Clusters' }
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
      meta: { title: 'Assets' }
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
      meta: { title: 'Segments' }
    },
    {
      path: '/segments/:uuid',
      name: 'SegmentDetailView',
      component: SegmentDetailView,
    },

    {
      path: '/ansible',
      name: 'AnsibleView',
      component: AnsibleView,
      meta: { title: 'Ansible' }
    },

    {
      path: '/tasks',
      name: 'TaskListView',
      component: TaskListView,
      meta: { title: 'Tasks' }
    },
  ]
})

router.afterEach((to, from) => {
  if(to.meta.title){
    document.title = to.meta.title + ' | ' + DEFAULT_TITLE
  }else{
    document.title = DEFAULT_TITLE;
  }
});

export default router