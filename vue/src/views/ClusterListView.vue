<template>
<div>
  <b-container>
    <h1>Clusters</h1>


    <table class="table table-borderless" style="margin-top: auto; margin-bottom: auto;">
      <thead>
        <tr>
          <th scope="col">Cluster</th>
          <th scope="col">Segment</th>
          <th scope="col">Prism IP</th>
          <th scope="col">IPMI MAC</th>
          <th scope="col">Host IP</th>
          <th scope="col">Cluster Login</th>
          <th scope="col">Version</th>
          <th scope="col">Hypervisor</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr 
          v-for="cluster in $store.state.clusters"
          :key="cluster.uuid"
        >
          <td>{{ cluster.name }}</td>
          <td>{{ cluster.segment_name }}</td>
          <td>{{ cluster.external_ip }}</td>
          <td>
            <span style="color: green" v-if="physical_check_result(cluster.physical_check) == 0"><i class="fas fa-check-circle"></i></span>
            <span style="color: orange" v-else-if="physical_check_result(cluster.physical_check) == 1"><i class="fas fa-exclamation-circle"></i></span>
            <span style="color: red" v-else><i class="fas fa-times-circle"></i></span>
          </td>
          <td>
            <span style="color: green" v-if="host_check_result(cluster.host_check) == 0"><i class="fas fa-check-circle"></i></span>
            <span style="color: orange" v-else-if="host_check_result(cluster.host_check) == 1"><i class="fas fa-exclamation-circle"></i></span>
            <span style="color: red" v-else><i class="fas fa-times-circle"></i></span>
          </td>
          <td>
            <span style="color: green" v-if="cluster.prism_check"><i class="fas fa-check-circle"></i></span>
            <span style="color: red" v-else><i class="fas fa-times-circle"></i></span>
          </td>
          <td>{{ cluster.version }}</td>
          <td>{{ cluster.hypervisor }}</td>
          <td>
            <a style="color: blue; cursor: pointer;" @click="() => { start_clicked(cluster.uuid) }">Start</a>
            <a style="color: red; cursor: pointer; margin-left: 20px" @click="() => { stop_clicked(cluster.uuid) }">Stop</a>
            <a style="color: red; cursor: pointer; margin-left: 20px" @click="() => { foundation_clicked(cluster.uuid) }">Foundation</a>
          </td>          
        </tr>
      </tbody>
    </table>

  </b-container>

  <b-modal id="cluster-stop-modal" title="Cluster Stop" >
    <b-container>
      Cluster Stop
    </b-container>
  </b-modal>

  <b-modal id="cluster-foundation-modal" title="Cluster Foundation" hide-footer>
    <b-container>
      <b-form-group
        label="AOS Version"
        label-cols="4"
        label-for="input-horizontal"
      >
        <b-form-select v-model="selected_aos_version" :options="aos_versions"></b-form-select>
      </b-form-group>

      <b-form-group
        label="Hypervisor"
        label-cols="4"
        label-for="input-horizontal"
      >
        <b-form-select v-model="selected_hypervisor" :options="hypervisors"></b-form-select>
      </b-form-group>

      <div slot="modal-footer" class="w-100">
        <b-button block variant="danger" 
          :disabled="foundationDisabled"
          @click="() => { start_foundation() }"
        >Start Foundation</b-button>
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
      selected_cluster: null,

      selected_aos_version: null,
      aos_versions: [],

      selected_hypervisor: null,
      hypervisors: [],
    }
  },

  computed: {
    foundationDisabled: function(){
      if(this.selected_aos_version == null){
        return true
      }
      if(this.selected_hypervisor == null){
        return true
      }
      return false
    },
  },

  methods: {
    physical_check_result: function(checks){
      let all_ok = true
      let all_ng = true
      for(let key in checks){
        let value = checks[key]
        if(value){
          all_ng = false
        }else{
          all_ok = false
        }
      }

      if(all_ng){
        return 2
      }
      if(all_ok){
        return 0
      }
      return 1
    },

    host_check_result: function(checks){
      let all_ok = true
      let all_ng = true
      for(let key in checks){
        let value = checks[key]
        if(value){
          all_ng = false
        }else{
          all_ok = false
        }
      }

      if(all_ng){
        return 2
      }
      if(all_ok){
        return 0
      }
      return 1
    },

    stop_clicked: function(uuid){
      this.selected_cluster = uuid

      this.$bvModal.show('cluster-stop-modal')
    },

    foundation_clicked: function(uuid){
      this.selected_cluster = uuid

      this.selected_aos_version = null
      for(let cluster of this.$store.state.clusters){
        if(cluster.uuid != uuid){
          continue
        }
        let aos_versions = []
        for(let key in cluster.foundation_vms.nos_packages){
          let value = cluster.foundation_vms.nos_packages[key]
          aos_versions.push({
            value:value,
            text:key
          })
        }
        this.aos_versions = aos_versions
        break
      }

      this.selected_hypervisor = null
      this.hypervisors = [{value:'ahv', text:'AHV'}]

      this.$bvModal.show('cluster-foundation-modal')
    },

    start_foundation: function(){
      console.log(this.selected_cluster)
      console.log(this.selected_aos_version)
      console.log(this.selected_hypervisor)

      axios.post('/api/operations/foundation', {
        cluster_uuid: this.selected_cluster,
        aos_image: this.selected_aos_version,
        hypervisor_type: 'ahv',
        hypervisor_image: ''
      })
      .then((response) => {
        console.log(response)
      })
      .catch((error) => {
        console.log(error)
      })
    }
  },

  created(){
    //this.getClusters()
    //this.timer = setInterval(this.getClusters, 10 * 1000)
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
