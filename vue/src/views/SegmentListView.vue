<template>
<div>
  <b-container>
    <b-raw>

    <h2>Segments</h2>
    
    <div 
      v-for="segment in $store.state.segments"
      :key="segment.uuid"
      style="padding-bottom: 50px; text-align: left"
    >
      <h2>{{ segment.name }}</h2>
      <p>UUID: {{ segment.uuid }}</p>

      <h4> - Foundation VM</h4>
      <p>IP: {{ segment.foundation_vms.ip_addresses }}</p>
      <p>User: {{ segment.foundation_vms.user }}</p>
      <p>Password: {{ segment.foundation_vms.password }}</p>

      <h4> - Basics</h4>
      <p>Language: {{ segment.basics.language }}</p>
      <p>NFS Whitelist: {{ segment.basics.nfs_whitelists }}</p>

      <h4> - Containers</h4>
      <table 
        class="table table-borderless" 
        style="margin-top: auto; margin-bottom: auto;"
      >
        <thead>
          <tr>
            <th scope="col">Container Name</th>
            <th scope="col">Compression</th>
          </tr>
        </thead>

        <tbody>
          <tr 
            v-for="container in segment.containers"
            :key="container"
          >
            <td>{{ container }}</td>    
            <td></td>
          </tr>
        </tbody>
      </table>

      <h4> - Networks</h4>
      <table 
        class="table table-borderless" 
        style="margin-top: auto; margin-bottom: auto;"
      >
        <thead>
          <tr>
            <th scope="col">Name</th>
            <th scope="col">VLAN</th>
            <th scope="col">AHV IPAM</th>
            <th scope="col">Network</th>
            <th scope="col">Prefix</th>
            <th scope="col">Gateway</th>
            <th scope="col">DNS</th>
            <th scope="col">Pool</th>
          </tr>
        </thead>

        <tbody>
          <tr 
            v-for="(network, name) in segment.networks"
            :key="network"
          >
            <td>{{ name }}
            <td>{{ network.vlan }}</td>
            <td>{{ network.use_dhcp }}</td>
            <td>{{ network.network }}</td>    
            <td>{{ network.prefix }}</td>
            <td>{{ network.gateway }}</td>    
            <td>{{ network.dns }}</td>
            <td>{{ network.pools }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="'alias' in segment">
        <h4> - OverRide Asset Params</h4>
        <p>OverRide Prism IP: {{ segment.alias.external_ip }}</p>
        <p>OverRide Prism User: {{ segment.alias.prism_user }}</p>
        <p>OverRide Prism IP: {{ segment.alias.prism_password }}</p>
        <p>OverRide Netmask: {{ segment.alias.netmask }}</p>
        <p>OverRide Gateway: {{ segment.alias.gateway }}</p>
        <p>OverRide Name Server: {{ segment.alias.name_server }}</p>
        <p>OverRide NTP Server: {{ segment.alias.ntp_server }}</p>

        <h4> - OverRide Nodes</h4>
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
              v-for="node in segment.alias.nodes"
              :key="node.ipmi_ip"
            >
              <td>{{ node.host_name }}</td>
              <td>{{ node.position }}</td>  
              <td>Asset's MAC</td>
              <td>{{ node.ipmi_ip }}</td>
              <td>{{ node.host_ip }}</td>  
              <td>{{ node.cvm_ip }}</td>       
            </tr>
          </tbody>
        </table>

      </div>

      <h4> - Images</h4>
      <table 
        class="table table-borderless" 
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

  </b-raw>
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
