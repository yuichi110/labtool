<template>
<div>
  <b-container>
    <h2>Playbooks</h2>
    
    <div 
      v-for="playbook in $store.state.playbooks"
      :key="playbook.uuid"
      style="padding-bottom: 50px; text-align: left"
    >
      <h2>{{ playbook.name }}</h2>
      <p>UUID: {{ playbook.uuid }}</p>
      <pre style="text-align: left; border-style: groove">{{ playbook.body }}</pre>
    </div>

  </b-container>

</div>
</template>

<script>


export default {
  name: 'AssetListView',
  components: {

  },

  data () {
    return {
      assets: []
    }
  },

  methods: {

  },

  created(){

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
