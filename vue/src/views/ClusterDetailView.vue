<template>
  <div>
    <HeaderModule/>

    <p>{{ clusterName }}</p>
    <p>{{ clusterUser }}</p>

    <FooterModule/>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@/urls'
import '@/utils'

import HeaderModule from '@/components/HeaderModule'
import FooterModule from '@/components/FooterModule'

export default {
  name: 'ClusterDetailView',

  components: {
    HeaderModule,
    FooterModule,
  },

  data(){
    return {
      clusterName : '',
      clusterUser : '',
    }
  },

  methods: {
    getTheCluster: function(){
      //console.log(this.$router.currentRoute.path)
      let path = '/api' + this.$router.currentRoute.path
      return axios.get(path)
      .then((response) => {
        let data = response.data
        this.clusterName = data.name
      })
    },
  },

  created(){
    console.log('Created:' + this.$router.currentRoute.path)
    this.getTheCluster()
  },

  updated(){
    console.log('Updated:' + this.$router.currentRoute.path)
    this.getTheCluster()
  },
}
</script>

<style scoped>
  
</style>
