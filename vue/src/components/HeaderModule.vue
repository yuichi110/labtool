<template>
<b-container>
  <nav class="navbar navbar-expand-lg navbar-light" style="margin-top: auto; margin-bottom: auto; height:">
    <b-navbar-brand :to="{name:'IndexView'}">Founder</b-navbar-brand>

    <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

    <b-collapse id="nav-collapse" is-nav>
      <b-navbar-nav>
        <b-nav-item :to="{name:'IndexView'}">Home</b-nav-item>
        <b-nav-item :to="{name:'AnsibleView'}">Run-Ansible</b-nav-item>
        <b-nav-item :to="{name:'PlaybookListView'}">Playbooks</b-nav-item>

        <b-nav-item :to="{name:'ClusterListView'}">Clusters</b-nav-item>
        <b-nav-item :to="{name:'AssetListView'}">Assets</b-nav-item>
        <b-nav-item :to="{name:'SegmentListView'}">Segments</b-nav-item>

        <b-nav-item :to="{name:'TaskListView'}">
          Tasks
          <b-spinner 
          v-if="$store.state.task_success"
          small variant="primary" label="Spinning"></b-spinner>
          <b-spinner 
          v-if="$store.state.task_fail"
          small variant="danger" label="Spinning"></b-spinner>
        </b-nav-item>
      </b-navbar-nav>

    </b-collapse>
  </nav>
</b-container>
</template>

<script>

export default {
  name: 'HeaderModule',
  data(){
    return {
    }
  },

  methods: {

  },

  created(){

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
