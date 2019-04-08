<template>
  <div>
    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" @select="handleSelect">

      <el-menu-item index="1">
        <router-link :to="{name:'IndexView'}">JPOC Mgmt</router-link>
      </el-menu-item>

      <el-submenu index="2">
        <template slot="title">
          <router-link :to="{name:'ClusterListView'}">Clusters</router-link>
        </template>
        <el-menu-item v-for="(cluster, key, index) in clusters" :key="index" index="2-1">
          <router-link :to="{name:'ClusterDetailView', params:{id: cluster.id }}">{{ cluster.name }}</router-link>
        </el-menu-item>
      </el-submenu>

      <el-submenu index="3">
        <template slot="title">
          <router-link :to="{name:'AssetListView'}">Assets</router-link>
        </template>
        <el-menu-item v-for="(asset, key, index) in assets" :key="index" index="3-1">
          <router-link :to="{name:'AssetDetailView', params:{id: asset.id }}">{{ asset.name }}</router-link>
        </el-menu-item>
      </el-submenu>
      
      <el-submenu index="4">
        <template slot="title">
          <router-link :to="{name:'SegmentListView'}">Segments</router-link>
        </template>
        <el-menu-item v-for="(segment, key, index) in segments" :key="index" index="4-1">
          <router-link :to="{name:'SegmentDetailView', params:{id: segment.id }}">{{ segment.name }}</router-link>
        </el-menu-item>
      </el-submenu>

      <el-submenu index="5">
        <template slot="title">
          <router-link :to="{name:'TaskListView'}">Tasks</router-link>
        </template>
        <el-menu-item v-for="(segment, key, index) in tasks" :key="index" index="4-1">
          <router-link :to="{name:'TaskDetailView', params:{id: task.id }}">{{ task.name }}</router-link>
        </el-menu-item>
      </el-submenu>

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
      assets: [],
      segments: [],
      tasks: [],
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

    getAssets: function(){
      return axios.get(urls.ASSET)
      .then((response) => {
        //console.log('Header')
        //console.log(response.data)
        this.assets = response.data
      })
      .catch((error) => {
        console.log('Error. Failed to get response from "' + urls.CLUSTER + '"')
      })
    },

    getSegments: function(){
      return axios.get(urls.SEGMENT)
      .then((response) => {
        //console.log('Header')
        //console.log(response.data)
        this.segments = response.data
      })
      .catch((error) => {
        console.log('Error. Failed to get response from "' + urls.CLUSTER + '"')
      })
    },

    getTasks: function(){
      return axios.get(urls.TASK)
      .then((response) => {
        //console.log('Header')
        //console.log(response.data)
        this.tasks = response.data
      })
      .catch((error) => {
        console.log('Error. Failed to get response from "' + urls.CLUSTER + '"')
      })
    }
  },

  created(){
    this.getClusters()
    this.getAssets()
    this.getSegments()
    this.getTasks()
    this.timer = setInterval(this.getClusters, 10 * 1000)
    this.timer = setInterval(this.getAssets, 10 * 1000)
    this.timer = setInterval(this.getSegments, 10 * 1000)
    this.timer = setInterval(this.getTasks, 10 * 1000)
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
