<template>
    <section>
        <!-- 导航栏 -->
        <Menu></Menu>

        <!--工具条-->
        <el-col :span="24" class="toolbar">
            <el-form :inline="true">
                <el-form-item>
                    <el-input placeholder="TODO"></el-input>
                </el-form-item>
                <el-form-item>
                    <el-button @click="handleSearch">查询</el-button>
                </el-form-item>
                <el-form-item>
                    <el-button @click="handleAdd">添加用户</el-button>
                </el-form-item>
                <el-form-item>
                </el-form-item>
            </el-form>
        </el-col>
        <!-- 工具条 -->

        <!-- 用户列表 -->
        <el-table :data="users" highlight-current-row border v-loading="listLoading">
            <el-table-column prop="id" label="ID" width="100">
            </el-table-column>
            <el-table-column prop="name" label="用户名" width="100">
            </el-table-column>
            <el-table-column prop="email" label="邮件地址" width="150">
            </el-table-column>
            <el-table-column prop="is_admin" label="管理员" width="100":formatter="(row, column) => row.is_admin ? '是': '否'">
            </el-table-column>
            <el-table-column prop="wx_id" label="微信ID">
            </el-table-column>
            <el-table-column prop="login_at" label="登录时间">
               <template scope="data">{{ data.row.login_at | moment("YYYY-MM-DD HH:mm:ss") }}</template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间">
               <template scope="data">{{ data.row.updated_at | moment("YYYY-MM-DD HH:mm:ss") }}</template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间">
               <template scope="data">{{ data.row.created_at | moment("YYYY-MM-DD HH:mm:ss") }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150">
                <template scope="scope">
                    <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button type="text" size="small" @click="handleDelete(scope.row)">删除</el-button>
                </template>
            </el-table-column>
        </el-table>
        <!-- 用户列表 -->

        <!-- 表单 -->
        <el-dialog :title="editForm.title" v-model="editForm.visible" :close-on-click-modal="false">
            <el-form :model="editForm.data" label-width="80px" :rules="editForm.rules" ref="editForm">
                <el-form-item label="昵称" prop="name">
                    <el-input v-model="editForm.data.name" auto-complete="on"></el-input>
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                    <el-input v-model="editForm.data.email" auto-complete="on" ></el-input> 

                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="editForm.data.password" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="是否是管理员" prop="is_admin">
                    <el-switch v-model="editForm.data.is_admin"></el-switch>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click.native="editForm.visible = false">取 消</el-button>
                <el-button type="primary" @click.native="submit">提交</el-button>
            </div>
        </el-dialog>
        <!-- 表单 -->

    </section>
</template>

<script>
    export default {
        data() {
            return {
                resources: {
                    users: this.$resource('/users/'),
                    userDetail: this.$resource('/users{/userId}'),
                },
                users: [],
                editForm: {
                    visible: false,
                    title: '编辑',
                    data: {
                        id: 0,
                        name: '',
                        email: '',
                        password: '',
                        is_admin: false
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
                        email: [{
                            required: true,
                            message: '请输入邮箱',
                            trigger: 'blur'
                        }, {
                            type: 'email',
                            message: '请输入正确的邮箱',
                            trigger: 'blur'
                        }]
                    }
                },
                listLoading: false
            }
        },
        methods: {
            // 获取用户列表
            async fetchUsers() {
                    // 设置加载状态
                this.listLoading = true
                let resp, data

                try {
                    resp = await this.resources.users.get()
                    data = await resp.json()
                }  catch (error) {
                    this.$message({
                        message: '加载用户失败，请稍后重试',
                        type: 'error'
                    })
                    this.listLoading = false
                    return
                }

                this.listLoading = false
                this.users = data
            },

            // 搜索功能
            handleSearch() {
                this.$message({message: '搜索功能暂未实现', type: 'warning'})
            },

            // 显示新增界面
            handleAdd() {
                if (this.editForm.data.id != 0) {
                    if (!!this.$refs.editForm) {
                        this.$refs.editForm.resetFields()
                    }
                    this.editForm.data = {
                        name: '',
                        email: '',
                        password: '',
                        is_admin: false
                    }
                }
                this.editForm.visible = true;
                this.editForm.title = '添加';
            },

            // 显示编辑界面
            handleEdit(user) {
                // 重置表单状态
                this.editForm.visible = true;
                this.editForm.title = '更新'
                if (!!this.$refs.editForm) {
                    this.$refs.editForm.resetFields()
                }
                Object.assign(this.editForm.data, user)
            },

            // 提交用户表单
            async submit() {

                let valid
                this.$refs.editForm.validate((error) => {
                    valid = error
                })

                if (!valid) {
                    return
                }

                // 显示确认框
                try {
                    await this.$confirm('确认提交吗？', '提示')
                } catch (error) {
                    return
                }

                this.editForm.visible = false

                try {
                    let resp, action
                    // 添加用户
                    if (this.editForm.data.id == 0) {
                        action = '添加'
                        resp = await this.resources.users.save(this.editForm.data)
                    } else {
                        // 更新用户
                        action = '更新'
                        resp = await this.resources.userDetail.update(
                            {userId: this.editForm.data.id}, this.editForm.data)
                    }
                    this.$message({
                        message:  `用户 ${this.editForm.data.name} ${action}成功`,
                        type: 'success'
                    })
                    this.fetchUsers()
                } catch(resp) {

                    let message

                    try {
                        let data = await resp.json()
                        message = data.message
                    } catch(error) {
                        message = '访问失败'
                    }

                    this.$message({
                        message: message,
                        type: 'error'
                    })
                }
            },

            // 删除操作
            async handleDelete(user) {

                try {
                    await this.$confirm('确认删除吗？', '提示')
                } catch (error) {
                    return
                }

                try {
                    await this.resources.userDetail.delete({userId: user.id})
                } catch (resp) {
                    let data, message
                    try {
                        data = await resp.json()
                        message = data.message
                    } catch(error) {
                        message =  `用户 ${user.name} 删除失败`
                    }
                    this.$message({
                        type: 'error',
                        message: message
                    })
                    return
                }

                this.$message({
                    message: `用户 ${user.name} 删除成功`,
                    type: 'success'
                })

                this.fetchUsers()
            }
        },

        // 组件创建完成后就开始加载数据
        created() {
            this.fetchUsers()
        }
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

</style>
