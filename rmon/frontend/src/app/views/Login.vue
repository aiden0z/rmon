<template>
    <el-row>
        <el-col :span="12" :offset="6">
            <!-- 登录表单 -->
            <el-form :model="editForm.data" label-width="80px" :rules="editForm.rules" ref="editForm">
                <el-form-item label="名称" prop="name">
                    <el-input v-model="editForm.data.name" auto-complete="on" placeholder="邮箱也能登录"></el-input>
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input type="password" v-model="editForm.data.password" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click.native="submit">登录</el-button>
                </el-form-item>
            </el-form>
            <!-- 登录表单 -->
        </el-col>
    </el-row>
</template>

<script>
    export default {
        data() {
            return {
                resources: {
                    login: this.$resource('/login'),
                },
                users: [],
                editForm: {
                    data: {
                        name: '',
                        password: ''
                    },
                    rules: {
                        name: [{
                            required: true,
                            message: '请输入昵称',
                            trigger: 'blur'
                        }, {
                            min: 2,
                            max: 64,
                            message: '长度在 2 到 64 个字符',
                            trigger: 'blur'
                        }],
                        password: [{
                            required: true,
                            message: '请输入邮箱',
                            trigger: 'blur'
                        }]
                    }
                }
            }
        },
        methods: {

            // 提交登录表单
            async submit() {

                let valid
                this.$refs.editForm.validate((error) => {
                    valid = error
                })

                if (!valid) {
                    return
                }

                try {
                    let resp, data
                    resp = await this.resources.login.save(this.editForm.data)

                    // save user token and redirect to servers managment page
                    data = await resp.json()

                    // 将 token 保存在 sessionStorage 中
                    sessionStorage.setItem('RMON_TOKEN', data.token)

                    this.$router.push({name: 'servers'})

                } catch(resp) {

                    let message

                    try {
                        let data = await resp.json()
                        message = data.message
                    } catch(error) {
                        message = '登录失败'
                    }

                    this.$message({
                        message: message,
                        type: 'error'
                    })
                }
            },
        },
    }
</script>
<style scoped>

.toolbar .el-form-item {
    margin-bottom: 10px;
}

.toolbar {
    background: #fff;
    padding: 10px 10px 0 0;
}

.server-link {
    text-decoration: none;
}

</style>
