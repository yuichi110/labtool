var app = new Vue({
  el: '#app',
  data: {
    price: 19800
  },

  filters: {
    localeNum: function(val) {
      return val.toLocaleString()
    }
  }
})

