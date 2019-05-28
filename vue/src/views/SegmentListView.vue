<template>
<div>
  <b-container>

    <div 
      v-for="segment in $store.state.segments"
      :key="segment.uuid"
      style="padding-bottom: 50px; text-align: left"
    >
      <h2>{{ segment.name }}</h2>

      <table 
        class="table" 
        style="margin-top: auto; margin-bottom: auto;"
      >
        <thead>
          <tr>
            <th scope="col">Image Name</th>
            <th scope="col">Container</th>
            <th scope="col">URL</th>
          </tr>
        </thead>

        <tbody>
          <tr 
            v-for="(value, key) in segment.images"
            :key="key"
          >
            <td>{{ key }}</td>
            <td>{{ value.container }}</td>  
            <td>{{ value.url }}</td>     
          </tr>
        </tbody>
      </table>
    </div>

  </b-container>

</div>
</template>

<script>


export default {
  name: 'IndexView',
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
