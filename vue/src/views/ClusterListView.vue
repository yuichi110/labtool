<template>
<div>
  <b-container>
    <h1>(Assets + Segments) -> Clusters</h1>

    <div 
      v-for="cluster in $store.state.clusters"
      :key="cluster.uuid"
      style="padding-bottom: 50px; text-align: left"
    >
      <h2>{{ cluster.name }}</h2>
      <p>UUID: {{ cluster.uuid }}</p>
      <p>Asset Name: {{ cluster.asset_name }}</p>
      <p>Segment Name: {{ cluster.segment_name }}</p>
      
      <p>Prism User: {{ cluster.prism_user }}</p>
      <p>Prism Password: {{ cluster.prism_password }}</p>
      <p>Prism External IP: {{ cluster.external_ip }}</p>
      <p>Netmask: {{ cluster.netmask }}</p>
      <p>Gateway: {{ cluster.gateway }}</p>
      <p>Name Server: {{ cluster.name_server }}</p>
      <p>NTP Server: {{ cluster.ntp_server }}</p>

      <h4> - Basics</h4>
      <p>Language: {{ cluster.basics.language }}</p>
      <p>NFS Whitelist: {{ cluster.basics.nfs_whitelists }}</p>

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
            v-for="container in cluster.containers"
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
            v-for="(network, name) in cluster.networks"
            :key="name"
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
            v-for="node in cluster.nodes"
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
  </b-modal>

</div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'ClusterListView',
  components: {

  },

  data () {
    return {

    }
  },

  computed: {


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
