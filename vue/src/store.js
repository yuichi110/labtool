import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    clusters: [],
    assets: [],
    segments: [],
  },

  mutations: {
    set_clusters(state, data){
      state.clusters = data
    },

    set_assets(state, data){
      state.assets = data
    },

    set_segments(state, data){
      state.segments = data
    }
  },

  actions: {
    cluster_get({ dispatch, commit, state }){
      return axios.get('/api/clusters/')
      .then((response) => {
        commit('set_clusters', response.data)
      })
      .catch((error) => {
        console.log('Error: ' + error)
      })
    },

    assets_get({ dispatch, commit, state }){
      return axios.get('/api/assets/')
      .then((response) => {
        commit('set_assets', response.data)
      })
      .catch((error) => {
        console.log('Error: ' + error)
      })
    },

    segments_get({ dispatch, commit, state }){
      return axios.get('/api/segments/')
      .then((response) => {
        commit('set_segments', response.data)
      })
      .catch((error) => {
        console.log('Error: ' + error)
      })
    },
  }
})
