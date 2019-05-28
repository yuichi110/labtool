<template>
  <div>
    <!--
    <HeaderModule/>

    <h1>Cluster {{ name }}</h1>

    <FooterModule/>
  -->
  </div>
</template>

<script>


export default {
  name: 'ClusterDetailView',
  components: {

  },

  data () {
    return {
      name: '',
    }
  },

  methods: {
    getCluster: function(){
      let words = this.$route.path.split('/')
      let cluster_uuid = words[words.length-1]
      let url = urls.CLUSTER_UUID.format(cluster_uuid)
      console.log(url)

      return axios.get(url)
      .then((response) => {
        let cluster = response.data
        this.name = cluster['name']
      })
      .catch((error) => {
        console.log('Error. Failed to get response from "' + urls.CLUSTER + '"')
      })
    },
  },

  created(){
    this.getCluster()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
