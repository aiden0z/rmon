<template>
  <div id="app">
    <wv-group>
      <wv-input ref="username" label="用户" v-model="data.name" required></wv-input>
      <wv-input ref="password" label="密码" type="password" v-model="data.password" required></wv-input>
      <wv-button type="primary" @click="submit">绑定</wv-button>
    </wv-group>
  </div>
</template>

<script>

export default {
  data() {
    return {
      resources: {
        bindUser: this.$resource(),
      },
      data: {
        name: '',
        password: ''
      }
    }
  },

  methods: {
    async submit() {
      // 检查表单
      this.$refs.username.validate()
      this.$refs.password.validate()
      if (!this.$refs.username.valid || !this.$refs.password.valid) {
        return
      }

      let resp
      try {
        resp = await this.resources.bindUser.save(this.data)
      } catch (resp) {
        let message
        try {
          let result = await resp.json()
          message = '错误，' + result.message
        } catch (error) {
          console.log(error)
          message = '发生错误，请稍后重试'
        }
        this.$dialog({
          message:  message
        })
        return
      }

      this.$dialog({
        message: '绑定成功，请点击左上角返回公众号继续操作'
      })
    },
  }

}
</script>

<style scoped>
</style>
