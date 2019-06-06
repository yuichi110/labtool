<template>
<div>
  <b-container>
    <h2>Assets</h2>
    
    <div 
      v-for="asset in $store.state.assets"
      :key="asset.uuid"
      style="padding-bottom: 50px; text-align: left"
    >
      <h2>{{ asset.name }}</h2>
      <p>UUID: {{ asset.uuid }}</p>
      <p>Prism User: {{ asset.prism_user }}</p>
      <p>Prism Password: {{ asset.prism_password }}</p>
      <p>Prism External IP: {{ asset.external_ip }}</p>
      <p>Netmask: {{ asset.netmask }}</p>
      <p>Gateway: {{ asset.gateway }}</p>
      <p>Name Server: {{ asset.name_server }}</p>
      <p>NTP Server: {{ asset.ntp_server }}</p>

      <h4> - Nodes</h4>
      <table 
        class="table table-borderless" 
        style="margin-top: auto; margin-bottom: auto;"
      >
        <thead>
          <tr>
            <th scope="col">Host</th>
            <th scope="col">Position</th>
            <th scope="col">IPMI MAC</th>
            <th scope="col">IPMI IP</th>
            <th scope="col">Host IP</th>
            <th scope="col">CVM IP</th>
          </tr>
        </thead>

        <tbody>
          <tr 
            v-for="node in asset.nodes"
            :key="node.ipmi_mac"
          >
            <td>{{ node.host_name }}</td>
            <td>{{ node.position }}</td>  
            <td>{{ node.ipmi_mac }}</td>
            <td>{{ node.ipmi_ip }}</td>
            <td>{{ node.host_ip }}</td>  
            <td>{{ node.cvm_ip }}</td>       
          </tr>
        </tbody>
      </table>
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
