<template>
<div>
  <b-container>

    <h1>Tasks</h1>
    
    <table class="table table-borderless" style="margin-top: auto; margin-bottom: auto;">
      <thead>
        <tr>
          <th scope="col">Task Name</th>
          <th scope="col">Created At</th>
          <th scope="col">Updated At</th>
          <th scope="col">Status</th>
        </tr>
      </thead>

      <tbody>
        <tr 
          v-for="task in $store.state.tasks"
          :key="task.uuid"
        >
          <td>{{ task.name }}</td>
          <td>{{ task.creation_time }}</td>
          <td>{{ task.update_time }}</td>
          <td><pre style="text-align:left">{{ task.status }}</pre></td>
        </tr>
      </tbody>
    </table>

  </b-container>
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
      intervalId: null,
    }
  },

  methods: {
    forceReRender: function(){
      this.$forceUpdate()
    }
  },

  mounted: function(){
    this.intervalId = setInterval(this.forceReRender, 15 * 1000)
  },

  beforeDestroy: function(){
    clearInterval(this.intervalId)
  },
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
