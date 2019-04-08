<template>
  <p>{{ clusterName }}</p>
  <p>{{ clusterUser }}</p>
</template>

<script>
import axios from 'axios'
import urls from '../urls'
import '../utils'

export default {
  data(){
    return {
      clusterName : '',
      clusterUser : '',
    }
  },

  methods: {
    getClusters: function(){
      console.log(this.$router.currentRoute)

      return axios.get(urls.CLUSTER)
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
