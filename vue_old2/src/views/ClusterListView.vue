<template>
  <div>
    <HeaderModule/>
    <h1>Clusters</h1>

  <el-table
    :data="clusters"
    style="width: 100%">
    <el-table-column
      label="Cluster"
      width="100">
      <template slot-scope="scope">
        <el-popover trigger="hover" placement="top">
          <p>Name: {{ scope.row.name }}</p>
          <p>UUID: {{ scope.row.uuid }}</p>
          <div slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ scope.row.name }}</el-tag>
          </div>
        </el-popover>
      </template>
    </el-table-column>
    <el-table-column
      label="Asset"
      width="100">
      <template slot-scope="scope">
        <el-popover trigger="hover" placement="top">
          <p>Name: {{ scope.row.asset_name }}</p>
          <p>UUID: {{ scope.row.asset_uuid }}</p>
          <div slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ scope.row.asset_name }}</el-tag>
          </div>
        </el-popover>
      </template>
    </el-table-column>
    <el-table-column
      label="Segment"
      width="100">
      <template slot-scope="scope">
        <el-popover trigger="hover" placement="top">
          <p>Name: {{ scope.row.segment_name }}</p>
          <p>UUID: {{ scope.row.segment_uuid }}</p>
          <div slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ scope.row.segment_name }}</el-tag>
          </div>
        </el-popover>
      </template>
    </el-table-column>

    <el-table-column
      label="Foundation">
      <template slot-scope="scope">
        <el-select v-model="scope.row.value_aos" placeholder="AOS">
          <el-option
            v-for="(value, key) in scope.row.foundation_vms.nos_packages"
            :key="value"
            :label="key"
            :value="value">
          </el-option>
        </el-select>
        <el-select v-model="scope.row.value_hypervisor" placeholder="Hypervisor">
          <el-option
            v-for="(value, key) in hypervisor"
            :key="value"
            :label="key"
            :value="value">
          </el-option>
        </el-select>
        <el-button
          size="mini"
          type="primary"
          @click="handleFoundation(scope.row.uuid, scope.row.value_aos, scope.row.value_hypervisor)">Foundation</el-button>
      </template>
    </el-table-column>

    <el-table-column
      label="Operations">
      <template slot-scope="scope">
        <el-button
          size="mini"
          @click="handleDetail(scope.row.uuid)">Detail</el-button>
        <el-button
          size="mini"
          @click="handleEdit(scope.row.uuid)">Edit</el-button>
        <el-button
          size="mini"
          type="danger"
          @click="handleDelete(scope.row.uuid)">Delete</el-button>
      </template>
    </el-table-column>
  </el-table>

    <FooterModule/>
  </div>
</template>

<script>
import axios from 'axios'
import urls from '@/urls'
import '@/utils'

import HeaderModule from '@/components/HeaderModule'
import FooterModule from '@/components/FooterModule'

export default {
  name: 'ClusterListView',
  components: {
    HeaderModule,
    FooterModule,
  },

  data () {
    return {
      clusters: [],
      hypervisor: {
        'AHV (AOS Bundled)':'ahv',
        'ESXi 6.5':'esxi:esxi.iso'
      }
    }
  },

  methods: {
    getClusters: function(){
      return axios.get(urls.CLUSTER)
      .then((response) => {
        let clusters = response.data
        for(let cluster of clusters){
          cluster['value_aos'] = ''
          cluster['value_hypervisor'] = ''
        }
        this.clusters = clusters
      })
      .catch((error) => {
        console.log('Error. Failed to get response from "' + urls.CLUSTER + '"')
      })
    },

    handleDetail(cluster_uuid) {
      console.log(cluster_uuid);
    },
    handleEdit(cluster_uuid) {
      console.log(cluster_uuid);
    },
    handleFoundation(cluster_uuid, value_aos, value_hypervisor) {
      console.log(value_aos)
      console.log(value_hypervisor)
      if(value_aos == ''){
        return
      }
      if(value_hypervisor == ''){
        return
      }

      let hypervisor_type = 'ahv'
      let hypervisor_image = ''
      if(value_hypervisor != 'ahv'){
        words = value_hypervisor.split(':')
        hypervisor_type = $.trim(words[0])
        hypervisor_image = $.trim(words[1])
      }

      axios.post('/api/operations/foundation', {
        cluster_uuid: cluster_uuid,
        aos_image: value_aos,
        hypervisor_type: hypervisor_type,
        hypervisor_image: hypervisor_image
      })
      .then((response) => {
        console.log(response)
      })
      .catch((error) => {
        console.log(error)
      })
    },
    handleDelete(cluster_uuid) {
      console.log(cluster_uuid);
    }
  },

  created(){
    this.getClusters()
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
