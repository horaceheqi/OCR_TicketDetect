<template>
  <el-header>
    <h4 style="margin: 0px 0px 0px 1rem; display: inline;">OCR</h4>
    <el-dropdown style="float: right">
      <i class="el-icon-setting" style="margin-right: 15px"></i>
      <el-dropdown-menu slot="dropdown">
        <el-dropdown-item>用户管理</el-dropdown-item>
        <el-dropdown-item>用户注销</el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>
    <span style="cursor: pointer; display: inline; float: right; margin-right: 1rem">admin</span>
  </el-header>
</template>

<script>
    export default {
        name: "myHeader"
    }
</script>

<style scoped>

</style>
