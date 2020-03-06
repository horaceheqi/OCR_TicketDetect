<template>
  <el-menu default-active="1" @open="handleOpen" @close="handleClose" background-color="#545c64" text-color="#fff"
           active-text-color="#ffd04b">
    <el-menu-item index="1">
      <i class="el-icon-menu"></i>
      <span slot="title">通用识别</span>
    </el-menu-item>
  </el-menu>
</template>

<script>
  export default {
    name: "myMenu",
    methods: {
      // 侧面菜单栏控制
      handleOpen(key, keyPath) {
        console.log(key, keyPath);
      },
      handleClose(key, keyPath) {
        console.log(key, keyPath);
      },
    }
  }
</script>

<style scoped>

</style>
