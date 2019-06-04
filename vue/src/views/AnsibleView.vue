<template>
<div>
  <b-container>
    <h1>Run Ansible Playbook</h1>

    <b-form-group
      label="Hosts: "
      label-cols="2"
      label-for="input-horizontal"
    >
      <b-form-input 
        v-model="hosts_text" 
        placeholder="Comma separated hosts. Example: '10.0.0.1, 10.0.0.2'"
        @input="() => { hosts_changed() }"
      ></b-form-input>
    </b-form-group>

    <b-form-group
      label="Remote User: "
      label-cols="2"
      label-for="input-horizontal"
    >
      <b-form-input v-model="user" placeholder="Remote host user name"></b-form-input>
    </b-form-group>

    <b-form-group
      label="Password: "
      label-cols="2"
      label-for="input-horizontal"
    >
      <b-form-input v-model="password" placeholder="Remote host user password"></b-form-input>
    </b-form-group>

    <b-form-group
      label="Playbook: "
      label-cols="2"
      label-for="input-horizontal"
    >
      <b-form-select 
        v-model="selected_playbook" 
        :options="$store.state.playbooks"
        @input="() => { playbook_changed() }"
      ></b-form-select>
    </b-form-group>

    <b-button block variant="primary" 
      @click="() => { run_clicked() }"
      :disabled="runDisabled"
    >Run Playbook</b-button>


    <b-row>
      <b-col>
        <h2>Inventory</h2>
        <pre style="text-align: left; border-style: groove">{{ get_inventory_body() }}</pre>

        <h2>Playbook Content</h2>
        <pre style="text-align: left; border-style: groove">{{ get_playbook_body() }}</pre>
      </b-col>
      <b-col>
        <h2>Progress and Result</h2>
        <pre style="text-align: left; border-style: groove">{{ playbook_task_status }}</pre>
      </b-col>
    </b-row>
  </b-container>

</div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AnsibleView',
  components: {

  },

  data () {
    return {
      hosts_text: '',
      hosts: [],
      user: '',
      password: '',

      selected_playbook: null,
      playbook_name: '',
      playbook_body: '',

      playbook_task_uuid: '',
      playbook_task_status: '\n',
    }
  },

  computed: {
    runDisabled: function(){
      if(this.hosts.length == 0){
        return true
      }
      if(this.user == ''){
        return true
      }
      if(this.password == ''){
        return true
      }
      if(this.selected_playbook == null){
        return true
      }

      return false
    },
  },

  methods: {
    run_clicked: function(){

      axios.post('/api/operations/run_playbook/' + this.selected_playbook, {
        hosts: this.hosts,
        user: this.user,
        password: this.password
      })
      .then((response) => {
        console.log(response)
        this.playbook_task_uuid = response.data.uuid
        this.$store.dispatch('task_success')
      })
      .catch((error) => {
        console.log(error)
        this.$store.dispatch('task_fail')
      })
    },

    hosts_changed: function(){
      let words = this.hosts_text.split(',')
      let ar = []
      for(let word of words){
        ar.push(word.trim())
      }
      this.hosts = ar
    },

    playbook_changed: function(){
      console.log(this.selected_playbook)

      for(let playbook of this.$store.state.playbooks){
        if(playbook['value'] == this.selected_playbook){
          this.playbook_name = playbook['text']
          this.playbook_body = playbook['body']
          console.log(playbook)
          break
        }
      }
    },

    get_inventory_body: function(){
      let text = ''
      for(let host of this.hosts){
        text += host + '\n'
      }

      if(text == ''){
        return '\n'
      }
      return text
    },

    get_playbook_body: function(){
      let text = '# Auto generated code start\n'
      text += '---\n'
      text += '- name: ' + this.playbook_name + '\n'
      text += '  hosts: all\n'
      text += '  romote_user: ' + this.user + '\n'
      text += '  tasks:\n'
      text += '# Auto generated code end.\n\n'

      for(let line of this.playbook_body.split('\n'))
        text += '  ' + line + '\n'
      
      return text
    },

    get_task_progress: function(){
      if(this.playbook_task_uuid == ''){
        return
      }

      axios.get('/api/tasks/' + this.playbook_task_uuid)
      .then((response) => {
        this.playbook_task_status = response.data.status
      })
      .catch((error) => {
        console.log(error)
      })
    }
  },

  created(){
    //this.getClusters()
    //this.timer = setInterval(this.getClusters, 10 * 1000)
  },

  mounted(){
    setInterval(this.get_task_progress, 5 * 1000)
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
