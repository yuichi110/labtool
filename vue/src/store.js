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

    task_success: false,
    task_fail: false,
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

    set_task_success(state, bool){
      state.task_success = bool
    },

    set_task_fail(state, bool){
      state.task_fail = bool
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

    task_success({ dispatch, commit, state }){
      commit('set_task_success', true)
      
      let fun = function(){
        commit('set_task_success', false)
      }
      setTimeout(fun, 1 * 1000)
    },

    task_fail({ dispatch, commit, state }){
      commit('set_task_fail', true)
      
      let fun = function(){
        commit('set_task_fail', false)
      }
      setTimeout(fun, 1 * 1000)
    }
  }
})
