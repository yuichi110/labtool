<template>
  <div id="app">
    <HeaderModule/>
    <router-view/>
  </div>
</template>

<script>
import HeaderModule from '@/components/HeaderModule.vue'

export default {
  name: 'app',

  components: {
    HeaderModule,
  },

  data(){
    return {
    }
  },

  methods: {
    updateStatus: function(){
      this.$store.dispatch('cluster_get')
      this.$store.dispatch('assets_get')
      this.$store.dispatch('segments_get')
    },

    updateTasks: function(){
      this.$store.dispatch('tasks_get')
    }
  },

  created(){
    this.updateStatus()
    setInterval(this.updateStatus, 60 * 1000)

    this.updateTasks()
    setInterval(this.updateTasks, 10 * 1000)
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
