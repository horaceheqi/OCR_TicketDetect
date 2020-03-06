<template>
  <div id="app" style="height: 100%;">
    <el-container id="dashboard" style="height: 100%;">
      <el-header style="height: 60px; background-color: #598c88; color: #fff; padding: 0; line-height: 60px;">
        <MyHeader/>
      </el-header>
      <el-container>
        <el-aside style="width: initial; background-color: #545c64;">
          <MyMenu/>
        </el-aside>
        <el-main>
          <router-view/>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
  import MyHeader from "./components/myHeader";
  import MyMenu from "./components/myMenu";

  export default {
    components: {MyHeader, MyMenu},
    name: 'App',
  }
</script>
<style>
  html {
    height: 100%;
  }

  body {
    height: 100%;
  }

  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    cursor: pointer;
    display: inline;
    margin-right: 1rem;
  }
</style>
