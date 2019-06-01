import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    clusters: [],
    assets: [],
    segments: [],
    tasks: [],

    task_spinning: false,
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
    },

    set_tasks(state, data){
      state.tasks = data
    },

    set_task_spinning(state, bool){
      state.task_spinning = bool
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

    tasks_get({ dispatch, commit, state }){
      return axios.get('/api/tasks/')
      .then((response) => {
        commit('set_tasks', response.data)
      })
      .catch((error) => {
        console.log('Error: ' + error)
      })
    },

    task_start({ dispatch, commit, state }){
      commit('set_task_spinning', true)
      
      let fun = function(){
        commit('set_task_spinning', false)
      }
      setTimeout(fun, 2 * 1000)
    }
  }
})
