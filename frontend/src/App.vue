<template>
  <router-view />
</template>

<script>
import { defineComponent } from 'vue'
// import Vue from 'vue'
// import App from './App.vue'

import VuePaginate from 'vue-paginate'
// Vue.use(VuePaginate);

// Vue.config.productionTip = false

import process from 'process/browser';

export default defineComponent({
  name: 'App'
})
</script>
