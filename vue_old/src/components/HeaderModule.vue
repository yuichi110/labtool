<template>
  <div>
    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">

      <el-menu-item index="1">
        <router-link :to="{name:'IndexView'}">Cluster Builder</router-link>
      </el-menu-item>

      <el-submenu index="2">
        <template slot="title">Clusters</template>
        <el-menu-item v-for="(cluster, key, index) in clusters" :key="index" index="2-1">
          <router-link :to="{name:'ClusterDetailView', params:{id: cluster.id }}">{{ cluster.name }}</router-link>
        </el-menu-item>
      </el-submenu>

      <el-menu-item index="3" disabled>
        Info
      </el-menu-item>
      
      <el-menu-item index="4">
        <a href="https://www.ele.me" target="_blank">Orders</a>
      </el-menu-item>

    </el-menu>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@/urls'
import '@/utils'

export default {
  name: 'HeaderModule',
  data(){
    return {
      activeIndex: '1',

      clusters: [],
      timer: '',
    }
  },

  methods: {
    handleSelect: function(key, keyPath) {
      //console.log(key, keyPath);
    },

    getClusters: function(){
      return axios.get(urls.CLUSTER)
      .then((response) => {
        //console.log('Header')
        //console.log(response.data)
        this.clusters = response.data
      })
      .catch((error) => {
        console.log('Error. Failed to get response from "' + urls.CLUSTER + '"')
      })
    },
  },

  created(){
    this.getClusters()
    this.timer = setInterval(this.getClusters, 10 * 1000)
  }
}
</script>

<style scoped>
a:link {
  text-decoration: none;
}

a:visited {
  text-decoration: none;
}
</style>
