<template>
  <div>
    <HeaderModule/>

    <h1>Assets</h1>

  <el-table
    :data="assets"
    style="width: 100%">
    <el-table-column
      label="Name"
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
      label="ID"
      width="100">
      <template slot-scope="scope">
        <el-popover trigger="hover" placement="top">
          <p>Name: {{ scope.row.name }}</p>
          <p>UUID: {{ scope.row.uuid }}</p>
          <div slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ scope.row.POCID }}</el-tag>
          </div>
        </el-popover>
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
  name: 'AssetListView',
  components: {
    HeaderModule,
    FooterModule,
  },

  data () {
    return {
      assets: []
    }
  },

  methods: {
    getAssets: function(){
      return axios.get(urls.ASSET)
      .then((response) => {
        console.log(response.data)
        this.assets = response.data
      })
      .catch((error) => {
        console.log('Error. Failed to get response from "' + urls.CLUSTER + '"')
      })
    },

    handleEdit(cluster_uuid) {
      console.log(cluster_uuid);
    },
    handleDelete(cluster_uuid) {
      console.log(cluster_uuid);
    }
  },

  created(){
    this.getAssets()
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
