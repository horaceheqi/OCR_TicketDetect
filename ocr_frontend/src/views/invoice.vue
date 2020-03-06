<template>
  <el-container>
    <el-header>
      <el-row class="img-box">
        <el-upload
          class="inline-block"
          action="http://127.0.0.1:5000/upload"
          :http-request="El_upload"
          :show-file-list="false"
          list-type="picture" accept="image/*">
          <el-button type="primary">选择图片</el-button>
        </el-upload>
        <el-button type="primary" @click="handleRunDetect">检测识别</el-button>
        <!--<input name="file" type="file" accept="image/*" @change="uploads"/>-->
      </el-row>
    </el-header>
    <el-main style="width: auto; height: auto">
      <el-container>
        <!--<el-image :src="url" style="width:65%; height:60%;">加载图片</el-image>-->
        <div class="box">
          <el-image class="box-img" v-if="imageUrl" fit="scale-down" :src="imageUrl"
                    :onerror="handleDefaultPath"></el-image>
        </div>
        <div class="box-mes">
          <el-collapse v-model="activeNames" @change="handleChangeText">
            <el-collapse-item title="识别结果" name="1">
              <div >
                <ul class="result-item">
                  <li class="result-item">
                    <span class="result-num result-title">序号</span>
                    <span class="result-text result-title">内容</span>
                  </li>
                  <li class="result-item" v-for="(item, i) in result">
                    <span class="result-num">{{i}}</span>
                    <span class="result-text">{{item}}</span>
                  </li>
                </ul>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-container>
    </el-main>
    <el-footer></el-footer>
  </el-container>
</template>

<script>
  export default {
    name: "invoice",
    data() {
      return {
        handleDefaultPath: "this.src='../static/template.png'",
        imageUrl: '../static/template.png',
        imageName: '',
        activeNames: ['1'],
        result: ''
      }
    },
    methods: {
      // 文件上传
      El_upload(content) {
        let form = new FormData();
        form.append('file', content.file);
        this.$axios.post(content.action, form).then(res => {
          if (res.data.status != 200) {
            this.$message.error('图片文件上传失败');
          } else {
            this.imageName = res.data.data.file_name;
            this.imageUrl = "../static/image_upload/" + this.imageName;
            this.result = '';
            this.$message.success('图片文件上传成功');
          }
        }).catch(error => {
          console.log(error)
          if (error.response) {
            this.$message.error('文件上传失败,' + error.response.data);
          } else if (error.request) {
            this.$message.error('文件上传失败，服务器端无响应')
          } else {
            this.$message.error('文件上传失败，请求封装失败')
          }
        });
      },
      // 下拉框的控制
      handleChangeText(val) {
        console.log(val);
      },
      handleRunDetect() {
        this.$axios.post('http://127.0.0.1:5000/detect', {image_name: this.imageName}).then(res => {
          this.$message.success('检测识别成功');
          console.log(res);
          this.result = res.data.data;
          this.imageUrl = "../static/image_result/" + res.data.file_name;
        }).catch(res => {
          this.$message.error('检测识别失败');
          console.log(res)
        })
      },
      // 另一种上传文件方法,暂时没用
      uploads(e) {
        let file = e.target.files[0];
        let param = new FormData();  // 创建form对象
        param.append('file', file, file.name);  // 通过append向form对象添加数据
        console.log(param.get('file')); // FormData私有类对象，访问不到，可以通过get判断值是否传进去
        let config = {
          headers: {'Content-Type': 'multipart/form-data'}
        };
        // 添加请求头
        this.$axios.post('http://127.0.0.1:5000/upload', param, config).then(response => {
          if (response.data.code === 0) {
            self.ImgUrl = response.data.data
          }
          console.log(response.data)
        })
      }
    }
  }
</script>

<style scoped>
  .inline-block {
    display: inline-block;
  }

  .result-num {
    display: inline-block;
    text-align: left;
    vertical-align: top;
    width: 42px;
  }

  .result-text {
    width: 238px;
  }

  .result-title {
    color: #666;
  }

  .result-item{
    list-style: none;
    padding: 0;
    margin: 0;
    position: relative;
    margin-bottom: 5px;
  }

  .box {
    position: absolute;
    overflow: hidden;
    float: left;
    width: 755px;
    height: 480px;
    vertical-align: middle;
    text-align: center;
    border: 1px solid #000;
    background-color: #000;
  }

  .box-img {
    position: relative;
    width: 100%;
    height: 100%;
  }

  .box-mes {
    position: relative;
    margin-left: 760px;
    height: 480px;
    width: 504px;
    background-color: #fafafa;
    word-wrap: break-word;
    word-break: break-all;
  }
</style>
