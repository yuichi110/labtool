<template>
  <div>


    <h1>Index page</h1>
    <h2>{{ message }}</h2>

    <img v-bind:src="require('@/assets/logo.png')">
  </div>
</template>

<script>
import HeaderModule from '@/components/HeaderModule'

export default {
  name: 'TaskListView',
  components: {

  },

  data () {
    return {
      message: 'Welcome to Your Vue.js App'
    }
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
