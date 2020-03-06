// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import ElementUI from 'element-ui' //新添加
import 'element-ui/lib/theme-chalk/index.css' //新添加,避免后取打包样式不同,要放在import App 之前
import NormailizeCss from 'normalize.css'
import 'vue-awesome/icons'
import Icon from 'vue-awesome/components/Icon'

import App from './App'
import router from './router'
import axios from 'axios'
import QS from 'qs'

Vue.use(ElementUI);
Vue.component('icon', Icon);

Vue.config.productionTip = false;
Vue.prototype.$axios = axios;
Vue.prototype.qs = QS;

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
});
