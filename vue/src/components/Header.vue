<template>
  <div>
    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">
      <el-menu-item index="1">Cluster Builder</el-menu-item>

      <el-submenu index="2">
        <template slot="title">Clusters</template>
        <el-menu-item v-for="(cluster, key, index) in clusters" :key="index">
          <router-link :to="{name:'Cluster', params:{id: cluster.id }}">{{ cluster.name }}</router-link>
        </el-menu-item>
      </el-submenu>

      <el-menu-item index="3" disabled>Info</el-menu-item>
      <el-menu-item index="4"><a href="https://www.ele.me" target="_blank">Orders</a></el-menu-item>
    </el-menu>

    <p>Header</p>
    <p>{{ clusters }}</p>
    <div><el-date-picker v-model="datetime" type="datetime" placeholder="日時を選択してください"></el-date-picker></div>
    <p>{{ datetime }}</p>
  </div>
</template>

<script>
import axios from 'axios'
const URL_CLUSTERS = '/api/'

export default {
  name: 'Header',
  data(){
    return {
      activeIndex: '1',
      activeIndex2: '1',
      clusters: [],
      datetime: '',

      clusters2: [
        {name:'Cluster1'},
        {name:'Cluster2'},
      ],
    }
    
  },
  methods: {
    handleSelect: function(key, keyPath) {
      console.log(key, keyPath);
    },

    getClusters: function(){
      console.log('Get Clusters')
      return axios.get(URL_CLUSTERS)
      .then((response) => {
        this.clusters = response.data
      })
    },
  },

  created(){
    this.getClusters()
  }
}
</script>

<style scoped>
  
</style>
