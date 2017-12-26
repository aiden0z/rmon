<template>
    <section class="chart">
        <!-- 面包屑 -->
        <el-breadcrumb separator="/">
           <el-breadcrumb-item :to="{name: 'servers' }">首页</el-breadcrumb-item>
           <el-breadcrumb-item>{{ server.name }}</el-breadcrumb-item>
           <el-breadcrumb-item>监控</el-breadcrumb-item>
        </el-breadcrumb>
        <!-- 面包屑 -->

        <!-- 服务器信息 -->
         <table class="server-info">
          <tbody>

            <tr>
              <th colspan="8" class="title-row">服务器信息</th>
            </tr>

            <tr>
              <th>Vesion</th>
              <th colspan="2">OS</th>
              <th>Process_ID</th>
              <th colspan="2">UP_Time</th>
              <th>Connection</th>
              <th>Blocked</th>
            </tr>

            <tr>
                <td>{{ metrics.redis_version }}</td>
                <td colspan="2">{{ metrics.os}} </td>
                <td>{{ metrics.process_id }}</td>
                <!-- 计算属性 -->
                <td colspan="2">{{ upTime }} </td>
                <td>{{ metrics.connected_clients }}</td>
                <td>{{ metrics.blocked_clients }}</td>
            </tr>

            <tr>
              <th colspan="8" class="title-row">状态</th>
            </tr>

            <tr>
              <th>Connect Received</th>
              <th>Cmd Processed</th>
              <th>Ops Per Sec</th>
              <th>Rejected Connect</th>
              <th>Expired Keys</th>
              <th>Evicted keys</th>
              <th>Hits</th>
              <th>Misses</th>
            </tr>

            <tr>
              <td>{{ metrics.total_connections_received }}</td>
              <td>{{ metrics.total_commands_processed }}</td>
              <td>{{ metrics.instantaneous_ops_per_sec }}</td>
              <td>{{ metrics.rejected_connections }}</td>
              <td>{{ metrics.expired_keys }}</td>
              <td>{{ metrics.evicted_keys }}</td>
              <td>{{ metrics.keyspace_hits}}</td>
              <td>{{ metrics.keyspace_misses }}</td>
            </tr>

            <tr>
              <th colspan="8" class="title-row">数据库</th>
            </tr>
            <tr>
              <th colspan="2">DB</th>
              <th colspan="2">Keys</th>
              <th colspan="2">Expires</th>
              <th colspan="2">Avg TTL</th>
            </tr>

            <!-- 计算属性 -->
            <tr v-for="db in dbInstances">
              <td colspan="2">{{ db.name }}</td>
              <td colspan="2">{{ db.keys }}</td>
              <td colspan="2">{{ db.expires }}</td>
              <td colspan="2">{{ db.avg_ttl }}</td>
            </tr>
            
          </tbody>
        </table>

        <!-- 图表 -->
        <el-row>
            <el-col :span="24">
                <div id="chartOPS" style="width:100%; height:400px;"></div>
            </el-col>
            <el-col :span="24">
                <div id="chartMemory" style="width:100%; height:400px;"></div>
            </el-col>
            <el-col :span="24">
                <div id="chartCPU" style="width:100%; height:400px;"></div>
            </el-col>
        </el-row>
        <!-- 图表 -->

    </section>
</template>

<script>
    import echarts from 'echarts'
    import moment from 'moment'

    export default {
        data() {
            return {
                resources: {
                    serverMetric: this.$resource('/servers{/serverId}/metrics'),
                    serverDetail: this.$resource('/servers{/serverId}'),
                    serverCommand: this.$resource('/servers{/serverId}/command')
                },

                // 图表中最大数据长度
                dataLength: 200,
                // 数据刷新间隔
                interval: 1000,
                timer: null,

                // OPS 图
                chartOPS: null,
                chartOPSOption: null,

                // 内存使用率图标
                chartMemory: null,
                chartMemoryOption: null,

                // CPU使用率图表
                chartCPU: null,
                chartCPUOption: null,
            
                // Redis 服务器
                server: {},
                // 数据参考 https://redis.io/commands/INFO
                metrics: {}
            }
        },

        methods: {
            // 生成 echarts 配置对象
            generateEchartOption(text, legend, yAxisName, yFormat) {
                // 参考 http://echarts.baidu.com/option.html
                let option = {

                    // 颜色配置 from highcharts
                    // color: ['#7cb5ec', '#434348', '#90ed7d', '#f7a35c', '#8085e9', '#f15c80', '#e4d354', '#2b908f', '#f45b5b', '#91e8e1'],

                    // 标题
                    title: {
                        left: 'center',
                        text: text
                    },
                    // 提示框
                    tootip: {
                        trigger: 'axis'
                    },
                    // 工具栏配置
                    toolbox: {
                        feature: {
                            saveAsImage: {}
                        }
                    },
                    // 图例
                    legend: {
                        data: legend,
                        x: 'left'
                    },
                    // 网格配置
                    grid: {
                        top: 60,
                        bottom: 40,
                        left: 10,
                        right: 10
                    },
                    // 横坐标
                    xAxis: {
                        type: 'category',
                        // 生成横坐标轴数据
                        data: (function() {
                            let data = []
                            let now = moment()

                            // 横坐标数据为相隔接近 1 秒的时间节点
                            for (let i = 0; i < this.dataLength; i++) {
                                data.unshift(now.format('HH:mm:ss'))
                                now = moment(now - this.interval)
                            }
                            return data;
                        }.bind(this))()
                    },
                    // 纵坐标
                    yAxis: {
                        type: 'value',
                        scale: true,
                        name: yAxisName,
                        axisLabel: {
                            formatter: '{value} ' + yFormat
                        }
                    },

                    // 数据
                    series: []
                }

                // 根据图例生成数据
                for (let i = 0; i < legend.length; i++) {
                    option.series.push({
                        name: legend[i],
                        type: 'line',
                        smooth: true,
                        // 初始化时，所有数据都为 0 
                        data: (function() {
                            let data = []
                            for (let j = 0; j < this.dataLength; j++) {
                                data.unshift(0)
                            }
                            return data
                        }.bind(this))()
                    })
                }

                return option
            },

            // 更新监控数据
            async updateMetrics() {

                let resp
                try {
                    resp = await this.resources.serverMetric.get({serverId: this.$route.params.serverId})
                } catch (resp) {

                    this.$message({
                        type: 'error',
                        message: `获取服务器 ${this.server.name} 失败，请刷新页面重试`
                    })
                    this.stopUpdateMetrics()
                    return
                }

                this.metrics = await resp.json()

                // 更新数据
                let now = moment().format('HH:mm:SS')

                let option = this.chartOPSOption
                let m = this.metrics
                // 更新 OPS 数据
                option.series[0].data.shift()
                option.series[0].data.push(m.instantaneous_ops_per_sec)
                option.xAxis.data.shift()
                option.xAxis.data.push(now)

                // 更新内存使用数据
                option = this.chartMemoryOption
                option.series[0].data.shift()
                option.series[0].data.push((m.used_memory / 1024).toFixed(2))
                option.series[1].data.shift()
                option.series[1].data.push((m.used_memory_rss / 1024).toFixed(2))
                option.xAxis.data.shift()
                option.xAxis.data.push(now)

                // 更新 CPU 使用率数据
                option = this.chartCPUOption
                option.series[0].data.shift();
                option.series[0].data.push(m.used_cpu_sys);
                option.series[1].data.shift();
                option.series[1].data.push(m.used_cpu_user);
                option.series[2].data.shift();
                option.series[2].data.push(m.used_cpu_user_children);
                option.series[3].data.shift();
                option.series[3].data.push(m.used_cpu_sys_children);
                option.xAxis.data.shift();
                option.xAxis.data.push(now);

                this.chartOPS.setOption(this.chartOPSOption)
                this.chartMemory.setOption(this.chartMemoryOption)
                this.chartCPU.setOption(this.chartCPUOption)

                this.timer = setTimeout(this.updateMetrics, this.interval)
            },

            // 停止更新监控数据
            stopUpdateMetrics() {
                if (this.timer) {
                    clearTimeout(this.timer)
                }
                this.timer = null;
            }
        },

        computed: {

            // 格式化在线时间
            upTime() {
                let t = moment.duration(this.metrics.uptime_in_seconds, 'seconds')
                return `${t.days()} days ${t.hours()}:${t.minutes()}:${t.seconds()}`
            },

            // 解析出数据库实例及其信息
            dbInstances() {
                let instances = []

                for (let key in this.metrics) {
                    if (key.substring(0, 2) == 'db') {
                        instances.push({
                            name: key,
                            keys: this.metrics[key].keys,
                            expires: this.metrics[key].expires,
                            avg_ttl: this.metrics[key].avg_ttl
                        })
                    }
                }
                return instances
            }
        },

        mounted: function() {

            // 先停止更新数据
            this.stopUpdateMetrics()

            // 初始化 echarts 实例
            this.chartOPS = echarts.init(this.$el.querySelector('#chartOPS'))
            this.chartOPSOption = this.generateEchartOption('每秒执行命令数量', ['OPS'], '命令数量', '')
            this.chartOPS.setOption(this.chartOPSOption)

            this.chartMemory = echarts.init(this.$el.querySelector('#chartMemory'))
            this.chartMemoryOption = this.generateEchartOption('内存使用量', ['used_memory', 'used_memory_rss'], '使用量', 'Kb')
            this.chartMemory.setOption(this.chartMemoryOption)

            this.chartCPU = echarts.init(this.$el.querySelector('#chartCPU'))
            this.chartCPUOption = this.generateEchartOption(
                'CPU 使用率', ['cpu_user', 'cpu_sys', 'cpu_user_child', 'cpu_sys_child'], '使用率', '')
            this.chartCPU.setOption(this.chartCPUOption)

            // 开始更新数据
            this.updateMetrics()
        },
    
        async created() {

            let resp

            try {
                // 获取服务器详情
                resp = await this.resources.serverDetail.get({serverId: this.$route.params.serverId})
            } catch (resp) {
                // 如果获取失败则进行提示，并返回列表页面
                this.$message({
                    type: 'error',
                    message: '获取服务器信息失败'
                })

                this.$router.push({name: 'servers'})
                return
            }

            this.server = await resp.json()

        },

        // 在组件销毁前先停止更新数据
        beforeDestroy() {
            this.stopUpdateMetrics()
        }

    }
</script>

<style scoped>
    .chart {
        width: 100%;
        float: left;
    }

    .el-col {
        padding: 30px 20px;
    }

    .server-info {
        width: 100%;
        border: 1px solid black;
        margin-top: 20px;
        text-align: center;
        border-collapse: collapse;
    }

    table, th, td {
    border: 1px solid black;
    }

    .title-row {
        height: 50px;
    }
</style>
