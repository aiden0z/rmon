<template>
    <section>
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
                    <el-button @click="handleAdd">添加</el-button>
                </el-form-item>
            </el-form>
        </el-col>
        <!-- 工具条 -->

        <!-- Redis 服务器列表 -->
        <el-table :data="servers" highlight-current-row border v-loading="listLoading">
            <el-table-column prop="id" label="ID" width="100">
            </el-table-column>
            <el-table-column prop="name" label="名称" width="200">
            </el-table-column>
            <el-table-column prop="host" label="地址" width="100">
            </el-table-column>
            <el-table-column prop="port" label="端口号" width="100">
            </el-table-column>
            <el-table-column prop="password" label="密码" width="100">
            </el-table-column>
            <el-table-column prop="description" label="描述">
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
                    <router-link :to="{name: 'metric', params: {serverId: scope.row.id}}" class="metric-link el-button el-button--small el-button--text">监控</router-link>
                </template>
            </el-table-column>
        </el-table>
        <!-- Redis 服务器列表 -->

        <!-- 表单 -->
        <el-dialog :title="editForm.title" v-model="editForm.visible" :close-on-click-modal="false">
            <el-form :model="editForm.data" label-width="80px" :rules="editForm.rules" ref="editForm">
                <el-form-item label="名称" prop="name">
                    <el-input v-model="editForm.data.name" auto-complete="on"></el-input>
                </el-form-item>
                <el-form-item label="地址" prop="host">
                    <el-input v-model="editForm.data.host" auto-complete="on" ></el-input> 

                </el-form-item>
                <el-form-item label="地址" prop="port">
                    <el-input-number v-model="editForm.data.port" :min="0" :max="65536"></el-input-number>
                </el-form-item>
                <el-form-item label="密码" prop="password">
                    <el-input v-model="editForm.data.password" auto-complete="off"></el-input>
                </el-form-item>
                <el-form-item label="描述">
                    <el-input v-model="editForm.data.description" type="textarea" :rows="3" :maxlength="512"></el-input>
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
                    servers: this.$resource('/servers/'),
                    serverDetail: this.$resource('/servers{/serverId}'),
                },
                servers: [],
                editForm: {
                    visible: false,
                    title: '编辑',
                    data: {
                        id: 0,
                        name: '',
                        host: '',
                        port: 6379,
                        password: '',
                        description: ''
                    },
                    rules: {
                        name: [{
                            required: true,
                            message: '请输入名称',
                            trigger: 'blur'
                        }, {
                            min: 2,
                            max: 64,
                            message: '长度在 2 到 64 个字符',
                            trigger: 'blur'
                        }],
                        host: [{
                            required: true,
                            message: '请输入地址',
                            trigger: 'blur'
                        }],
                        description: [{
                            min: 0,
                            max: 512,
                            message: '长度在 2 到 512 个字符之间',
                        }]
                    }
    
                },
                listLoading: false
            }
        },
        methods: {
            // 获取用户列表
            async fetchServers() {
                    // 设置加载状态
                this.listLoading = true
                let resp, data

                try {
                    resp = await this.resources.servers.get()
                    data = await resp.json()
                }  catch (error) {
                    this.$message({
                        message: '加载服务器失败，请稍后重试',
                        type: 'error'
                    })
                    this.listLoading = false
                    return
                }

                this.listLoading = false
                this.servers = data
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
                        id: 0,
                        name: '',
                        host: '',
                        port: 6379,
                        password: '',
                        description: ''
                    }
                }
                this.editForm.visible = true;
                this.editForm.title = '添加';
            },

            // 显示编辑界面
            handleEdit(server) {
                // 重置表单状态
                this.editForm.visible = true;
                this.editForm.title = '更新'
                if (!!this.$refs.editForm) {
                    this.$refs.editForm.resetFields()
                }
                Object.assign(this.editForm.data, server)
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
                    // 添加服务器
                    if (this.editForm.data.id == 0) {
                        action = '添加'
                        resp = await this.resources.servers.save(this.editForm.data)
                    } else {
                        // 更新服务器
                        action = '更新'
                        resp = await this.resources.serverDetail.update(
                            {serverId: this.editForm.data.id}, this.editForm.data)
                    }
                    this.$message({
                        message:  `服务器 ${this.editForm.data.name} ${action}成功`,
                        type: 'success'
                    })
                    this.fetchServers()
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
            async handleDelete(server) {

                try {
                    await this.$confirm('确认删除吗？', '提示')
                } catch (error) {
                    return
                }

                try {
                    await this.resources.serverDetail.delete({serverId: server.id})
                } catch (resp) {
                    this.$message({
                        message: `服务器 ${server.name} 删除失败`,
                        type: 'error'
                    })
                    return
                }

                this.$message({
                    message: `服务器 ${server.name} 删除成功`,
                    type: 'success'
                })

                this.fetchServers()
            }
        },

        // 组件创建完成后就开始加载数据
        created() {
            this.fetchServers()
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

.metric-link {
    text-decoration: none;
}

</style>
