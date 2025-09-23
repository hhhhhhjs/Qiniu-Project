<!-- 预邀厂商 -->
<template>
    <div class="basicInfo" id="executeTheProcess">
        <div class="basic-item">
            <UtilsTitle :title="'执行进程'">
                <div>
                    <a-button class="add-style">废标</a-button>
                </div>
            </UtilsTitle>
            <div class="process-body">
                <div class="process-body-header">
                    <div class="header-left">
                        <div class="left-text">
                            <div class="text-edit">
                                <img src="@/assets/images//edit-icon.png" style="margin-right: 12px;">
                                <span>变更日志</span>
                            </div>

                            <div class="text-msg">
                                <div class="msg-list">
                                    <div class="mar-right-40">
                                        2023/07/26 06:55
                                    </div>
                                    <div class="mar-right-40">
                                        变更人：张三
                                    </div>
                                    <div class="mar-right-40">
                                        操作：发生了咖啡机阿斯利康发哈久啊失蜡法看哈书
                                    </div>
                                </div>
                                <div class="msg-more">
                                    查看更多
                                </div>
                            </div>

                        </div>
                    </div>
                    <div class="header-right" @click="openAnswering">
                        <div class="del-style width20">
                            <div class="alarm">
                                {{ warnNum }}
                            </div>
                        </div>
                        <div class="alarm-text">
                            <span>答疑</span>
                        </div>
                    </div>
                </div>

                <div class="process-body-main">
                    <a-steps :current="current" direction="vertical">
                        <a-step :icon='h(SVG)'>
                            <template #title>
                                <div class="tender-header">
                                    <div class="tender-status">
                                        响应
                                    </div>

                                    <div class="tender-time">
                                        {{ respondToQuotes }}
                                    </div>
                                </div>
                            </template>
                            <template #description>
                                <div class="tender-body">
                                    <div class="body-title">
                                        <div>响应情况</div>
                                        <div>
                                            <a-button @click="uploadAll">下载文件</a-button>
                                        </div>
                                    </div>
                                    <div>
                                        <a-table :dataSource="tenderData" :columns="tenderColumns" :pagination="false"
                                            :size="'large'" :loading="loading">
                                            <template #bodyCell="{ column, text, record, index }">
                                                <template v-if="column.dataIndex.includes('status')">
                                                    <div
                                                        :style="{ color: record[column.key] == 1 ? '#00B42A' : '#F53F3F' }">
                                                        {{ record[column.key] == 1 ? '已上传' : '未上传' }}
                                                    </div>
                                                </template>
                                            </template>
                                        </a-table>
                                    </div>

                                    <div class="body-title2">
                                        <div>响应报价</div>
                                    </div>
                                    <vxe-table border show-footer ref="tableRef" align="center" :merge-cells="mergeCells"
                                        :data="tableDataFirst" :loading="tableLoding">
                                        <vxe-column field="company" title="供应商名称"></vxe-column>
                                        <vxe-colgroup :title="`${item.title}(${item.num})`" v-for="item in tableColumns">
                                            <vxe-column :field="item.taxRate" title="税率(%)"></vxe-column>
                                            <vxe-column :field="item.unitPrice" title="单价(元)"></vxe-column>
                                            <vxe-column title="总价(元)">
                                                <template #default="{ row, rowIndex }">
                                                    {{
                                                        row[item.unitPrice] * item.num
                                                    }}
                                                </template>
                                            </vxe-column>
                                        </vxe-colgroup>
                                        <vxe-column field="allPrice" title="合计">
                                        </vxe-column>
                                    </vxe-table>
                                </div>


                            </template>


                        </a-step>

                        <a-step :icon='h(SVG)' v-if="current == 1 || current == 2">
                            <template #title>
                                <div class="evaluationOfBids-header" style="cursor: auto;">
                                    <div class="evaluationOfBids-status">
                                        评审
                                    </div>

                                    <div class="evaluationOfBids-time" v-if="props?.baseData?.endDate">
                                        {{ props.baseData.endDate }}
                                    </div>
                                </div>
                            </template>
                            <template #description>
                                <div class="evaluationOfBids-body" style="cursor: auto;">
                                    <div class="body-title">
                                        评审人员
                                    </div>
                                    <!-- 邀请专家 -->
                                    <Specialized :propsid="props.propsid" :current="0"></Specialized>
                                    <div class="body-title">
                                        评审报告
                                    </div>
                                    <ReviewReport :propsid="props.propsid" :current="0"></ReviewReport>

                                    <a-select ref="select" v-model:value="tableRound"
                                        style="width: 120px;margin-bottom: 8px;margin-top: 8px;" @change="handleChange">
                                        <a-select-option :value="item.value" v-for="item in roundSelect">{{ item.label
                                        }}</a-select-option>
                                    </a-select>
                                    <vxe-table border show-footer ref="tableRef" align="center" :merge-cells="mergeCells"
                                        :data="tableData" :loading="tableLoding">
                                        <vxe-column field="company" title="供应商名称"></vxe-column>
                                        <vxe-colgroup :title="`${item.title}(${item.num})`" v-for="item in tableColumns">
                                            <vxe-column :field="item.taxRate" title="税率(%)"></vxe-column>
                                            <vxe-column :field="item.unitPrice" title="单价(元)"></vxe-column>
                                            <vxe-column title="总价(元)">
                                                <template #default="{ row, rowIndex }">
                                                    {{
                                                        row[item.unitPrice] * item.num
                                                    }}
                                                </template>
                                            </vxe-column>
                                        </vxe-colgroup>
                                        <vxe-column field="allPrice" title="合计">
                                        </vxe-column>
                                    </vxe-table>
                                </div>



                            </template>
                        </a-step>


                        <a-step :icon='h(SVG)' v-if="current == 2">
                            <template #title>
                                <div class="evaluationOfBids-header" style="cursor: auto;">
                                    <div class="evaluationOfBids-status">
                                        公示
                                    </div>

                                    <div class="evaluationOfBids-time">
                                        <!-- 2023/07/26 06:55 -->
                                    </div>
                                </div>
                            </template>
                            <template #description>
                                <vxe-table border show-overflow :data="publicityData" :column-config="{ resizable: true }"
                                    :edit-config="{ trigger: 'click', mode: 'cell' }" align="center"
                                    :radio-config="{ highlight: true }" style="cursor: auto;">
                                    <vxe-column type="radio" width="60">
                                        <template #header>
                                            <vxe-button type="text">成交</vxe-button>
                                        </template>
                                    </vxe-column>
                                    <vxe-column title="供应商名称" field="companyName"></vxe-column>

                                    <vxe-column :edit-render="{ autofocus: '.vxe-input--inner' }" title="综合得分" field="score"
                                        width="200">
                                        <template #edit="{ row }">
                                            <vxe-input v-model="row.score" type="text" @blur="dataBlur(row)" @keydown="(event: any) => {
                                                if (event.$event.keyCode == 13) {
                                                    dataBlur(row)
                                                }
                                            }"></vxe-input>
                                        </template>
                                    </vxe-column>

                                </vxe-table>
                                <div class="remark-style">注：点击选中表示为成交供应商</div>
                            </template>
                        </a-step>
                    </a-steps>
                </div>
            </div>
        </div>
    </div>


    <!-- 答疑内容弹框 -->
    <a-modal v-model:open="answerDialog" :title="'答疑内容'" @ok="() => {
        answerDialog = false
    }" :destroyOnClose="true" width="80%">
        <div class="answer-boss">
            <div style="padding: 16px 32px;">
                <div v-for="item in dataSource" style="margin-bottom: 8px;">
                    <div class='issue-style'>
                        <div class="issue-unit text-omit">
                            提问单位：{{ item.companyName }}
                        </div>
                        <div class="issue-text text-omit">
                            <img src="@/assets/images/Arrow-grh.svg" alt="" class="arrow-17">
                            <img src="@/assets/images/clock.svg" alt="" class="clock-margin">
                            <span class="issue-time">&nbsp; 提问时间 &nbsp;&nbsp;&nbsp;
                                {{ item.createTime }}</span>
                            <span>
                                问题：{{ item.question }}
                            </span>
                        </div>
                        <div class="issue-status" v-if="item.reply">
                            <span>已答疑</span>
                            <RightOutlined class="icon-style" v-if="item.iconFlag" @click="item.iconFlag = false" />
                            <DownOutlined class="icon-style" v-else @click="item.iconFlag = true" />
                        </div>
                        <div class="issue-status2" v-else="item.reply">
                            未答疑
                        </div>
                        <div class="operate">
                            <img src="@/assets/images/Arrow-grh.svg" alt="" class="arrow-17">
                            <div class="detail-style" @click="openEdit(item)">答疑</div>
                            <div class="del-style" @click="openConfirm(item)">删除</div>
                        </div>
                    </div>
                    <div class="reply-style" v-if="item.iconFlag">
                        {{ item.reply }}
                    </div>

                </div>
                <div class="right-table-pages">
                    <div>
                        <!-- 共xx条数据 -->
                        {{ $t('placeholder.allOf') }} {{ pageVO2.total }} {{ $t('placeholder.strip') }}{{
                            $t('placeholder.data') }}
                    </div>
                    <a-pagination v-model:current="pageVO2.currentPage" v-model:pageSize="pageVO2.pageSize"
                        show-size-changer :total="pageVO2.total" @change="sizeChangeNeeds">
                    </a-pagination>
                </div>
            </div>
        </div>
    </a-modal>

    <!-- 编辑弹框 -->
    <a-modal v-model:open="editDialog" :title="'答疑内容'" @ok="formOk" :destroyOnClose="true">
        <a-form :model="formState" ref="formRef" :rules="formRules">
            <a-form-item :label="'答疑内容'" name="reply">
                <a-textarea v-model:value="formState.reply" />
            </a-form-item>
        </a-form>
    </a-modal>
    <!-- 删除弹框 -->
    <DelModal ref="delRef" :delElementTitle="'问题'" :delElementValue="delElementValue" @delData="delData"></DelModal>
</template>

<script lang="ts" setup>
import UtilsTitle from '@/components/UtilsTitle/index.vue';
import {
    RightOutlined, DownOutlined
} from '@ant-design/icons-vue';
import { ref, reactive, onMounted } from 'vue'
import { executePurchaseFileApi } from '@/api/ExecuteQuestionReply'
import { executeApi } from '@/api/Execute'
import type { questionReply } from '@/api/ExecuteQuestionReply'
import { message } from 'ant-design-vue';
import { responseFileApi } from '@/api/ResponseFile'
import JSZip from 'JSZip'
import { saveAs } from 'file-saver'
import { quotationApi } from '@/api/quotation'
import { excutePartake } from '@/api/ExecutePartake'
import Specialized from './components/specialized.vue'
import ReviewReport from './components/reviewReport.vue'
import dayjs from 'dayjs';
import { h } from 'vue';
import SVG from './components/img.vue'
const items = [
    {
        title: 'Login',
        status: 'finish',
        icon: h(SVG),
    },
    {
        title: 'Verification',
        status: 'finish',
        icon: h(SVG),
    },
    {
        title: 'Pay',
        status: 'process',
        icon: h(SVG),
    },
]
interface props {
    propsid: string,
    USERINFO: any,
    baseData: any
}
const loading = ref<boolean>(true)
const props = defineProps<props>()
const current = ref<number>(0)
const tenderData = ref<any>([

])
let tenderColumns: any = ref([

])
function getBase64(file: any) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}
const previewImage = ref<any>()
const fileList = ref<any>([])
const beforeUpload = async (file: any) => {
    previewImage.value = await getBase64(file)
    console.log('imgs', previewImage.value, file);
}
const handlePreview = (fileObj: any) => {
    const _url = fileObj[0].url || null
    const img = new window.Image();
    img.src = _url || previewImage.value;
    const newWin: any = window.open('');
    newWin.document.write(img.outerHTML);
    newWin.document.close();
}


const activeKey = ref<number | string>('')
const setActiveKey = (number: number | string) => {
    activeKey.value = number
}


//打开答疑内容弹框 **************************************************************
const answerDialog = ref<boolean>(false)
const openAnswering = () => {
    const data = {
        current: pageVO2.currentPage,
        size: pageVO2.pageSize,
        executeId: props.propsid
    }
    executePurchaseFileApi.getPurchaseList(data).then((res: any) => {
        if (res.success) {
            dataSource.value = res.obj.records
            pageVO2.total = res.obj.total
            answerDialog.value = true
        }
    })
}
const dataSource = ref<any>(
)
const pageVO2 = reactive({
    currentPage: 1,
    pageSize: 10,
    total: 8
})
const warnNum = ref<number>(0)
const getWarnNum = () => {
    const data = {
        current: 1,
        size: 100000,
        executeId: props.propsid
    }
    executePurchaseFileApi.getPurchaseList(data).then((res: any) => {
        if (res.success) {
            let num = 0
            // console.log('res.obj.records', res.obj.records);
            res.obj.records.forEach((item: any) => {
                if (!item.reply) {
                    num += 1
                }
            })
            warnNum.value = num
        }
    })
}
const getexecuteListList = () => {
    if (!props.propsid) {
        setTimeout(() => {
            getexecuteListList()
        }, 500);
    } else {
        //pageVO2
        const data = {
            current: pageVO2.currentPage,
            size: pageVO2.pageSize,
            executeId: props.propsid
        }
        executePurchaseFileApi.getPurchaseList(data).then((res: any) => {
            if (res.success) {
                dataSource.value = res.obj.records
                pageVO2.total = res.obj.total
            }
        })
    }
}

//编辑弹框
const editDialog = ref<boolean>(false)
const crudId = ref<string>('')
const openEdit = (row: any) => {
    crudId.value = row.id
    editDialog.value = true
}
const formState = ref<any>({
    reply: ""
})
const formRules = {
}
const formOk = () => {
    const data = <questionReply>{
        id: crudId.value,
        reply: formState.value.reply
    }
    executePurchaseFileApi.editExecutePurchaseFile(data).then((res: any) => {
        if (res.success) {
            getexecuteListList()
            message.success('答疑内容成功')
            editDialog.value = false
        }
    })
}
//删除的
const delElementValue = ref<string>('')
const delRef = ref<any>()
const openConfirm = (row: any) => {
    delRef.value.open()
    delElementValue.value = row.question
    crudId.value = row.id
}
const delData = () => {
    executePurchaseFileApi.delExecutePurchaseFile(crudId.value).then((res: any) => {
        if (res.success) {
            delRef.value.close()
            getexecuteListList()
        }
    })
}
const sizeChangeNeeds = () => {
    getexecuteListList()
}
//**************************************** */


//采购执行 供应商响应文件列表*******************************************************
const getSupplyResponseFileList = () => {
    if (!props.propsid) {
        setTimeout(() => {
            getSupplyResponseFileList()
        }, 500);
    } else {
        loading.value = true
        executeApi.getSupplyResponseFileList(props.propsid).then((res: any) => {
            if (res.success) {
                let temp_columns = <any>[]
                temp_columns.push({
                    title: '供应商名称',//供应商名称
                    dataIndex: 'company',
                    key: 'company',
                    width: '200'
                })
                ///创建判断是否上传的id验证数组,新增clomuns上去
                let idList = <any>[]
                props.baseData.responseFileList.forEach((item: any, index: string) => {
                    const temp_column = {
                        title: item.fileName,//
                        dataIndex: 'status' + index,
                        key: 'status' + index,
                        width: '200'
                    }
                    temp_columns.push(temp_column)
                    idList.push(item.id)
                })
                tenderColumns.value = temp_columns
                //获取对应的数据
                let dataList = <any>[]
                for (let temp_key in res.obj) {
                    const value = res.obj[temp_key]
                    const length = idList.length
                    const temp_data = <any>{}
                    temp_data['company'] = temp_key
                    for (let i = 0; i < length; i++) {
                        temp_data['status' + i] = value.includes(idList[i]) ? 1 : 0
                    }
                    dataList.push(temp_data)
                }
                
                tenderData.value = dataList
                loading.value = false
                getWarnNum()
            }
        })
    }
}
//下载全部文件   目前只针对一个响应供应商
const responseFileList = ref<any>([])
const uploadAll = () => {
    loading.value = false
    responseFileList.value = props.baseData.responseFileList
    //数组合并,fileID和标题文件类型等合并
    getResponseFileList()
}
const getResponseFileList = () => {
    responseFileApi.getResponseFileList(props.propsid).then((res: any) => {
        if (res.success) {
            res.obj.forEach((item: any) => {
                const temp_data = responseFileList.value.filter((ele: any) => { return ele.id == item.responseId })
                if (temp_data.length > 0) {
                    temp_data[0]['fileId'] = item.id
                    temp_data[0]['fileExtension'] = item.fileExtension
                }
            })
            //下载
            downLoadAll()
        }
    })
}
const downLoadAll = () => {
    let fileList = <any>[]
    if (responseFileList.value.length > 0) {
        responseFileList.value.forEach((item: any) => {
            fileList.push(downLoadFile(item))
        })
        Promise.all(fileList).then((result: any) => {
            console.log('promise的结果', result,);
            let zip = new JSZip();
            const demo = <any>zip.folder(tenderData.value[0].company)
            result.forEach((item: any) => {
                demo.file(item.ele.fileName + item.ele.fileExtension, item.blob)
            })
            zip.generateAsync({ type: "blob" }).then(function (content) {
                // 下载Zip文件
                saveAs(content, props.baseData.name + ".zip");
            });
        })
    }
}
const downLoadFile = (item: any) => {
    if(!item?.fileId){
        return
    }
    return new Promise((resolve) => {
        responseFileApi.downLoadFile(item.fileId).then((res: any) => {
            resolve({ blob: new Blob([res], { type: 'text/csv;charset=utf-8;' }), ele: item })
        })
    })
}

// 供应商列表数组
const tableRound = ref<string | number>(2)//当前第几轮
const roundSelect = ref<any>()//轮次数组
const tableLoding = ref<boolean>(false)
const getSelect = () => {
    let temP_select_list = <any>[]
    if (props.baseData?.allRound) {
        for (let i = 1; i < props.baseData.allRound; i++) {
            const temp_select = {
                value: i + 1,
                label: `第${i + 1}轮`
            }
            temP_select_list.push(temp_select)
        }
        if (temP_select_list.length < 1) {
            const temp_select = {
                value: 2,
                label: `第${2}轮`
            }
            temP_select_list.push(temp_select)
        }
        // console.log('temP_select_list',temP_select_list);
        roundSelect.value = temP_select_list
    }
}
const handleChange = () => {
    getPurchaseList()
}
const tableData = ref([
])
const tableDataFirst = ref([
])
const mergeCells = ref([
])
//获取供应商列表数组
const getPurchaseList = async () => {
    getSelect()
    tableLoding.value = true
    loading.value = false
    let nowList = <any>[] //当前执行id下的临时数组
    //获取clomuns
    getColumns(props.baseData.listDetails)
    //获取具体数值
    nowList = JSON.parse(JSON.stringify(props.baseData.listDetails))
    const list: any = await getQuotationList(props.propsid)
    list.list.forEach((item: any) => {
        const temp_data = nowList.filter((ele: any) => ele.id == item.detailsId)[0]
        temp_data['taxRate'] = item.taxRate
        temp_data['unitPrice'] = item.unitPrice
        temp_data['idd'] = item.id
    })
    // console.log('nowList', nowList);
    //获取键值对,拼接数组
    getSupplyQutationList(nowList)
    getSupplyQutationListFirst(nowList, 1)
}
//获取具体的物料多少
const getQuotationList = (executeId: string) => {
    return new Promise((resolve) => {
        quotationApi.getQuotationList(executeId).then((res: any) => {
            if (res.success) {
                resolve({
                    list: res.obj
                })
            }
        })

    })
}
//获取供应商和物料的键值对
const getSupplyQutationList = (nowList: any) => {
    if (nowList.length < 1) {
        return
    }
    executeApi.getSupplyQutationList(props.propsid, tableRound.value).then((res: any) => {
        if (res.success) {
            let temp_tableData = <any>[]
            //获取其中的键值对
            const temp_obj = res.obj
            for (let key in temp_obj) {
                const temp_tableData_data = <any>{}
                const THEVALUE = temp_obj[key]
                temp_tableData_data['company'] = key //公司名赋值
                let allPrice = 0
                THEVALUE.forEach((ele: any, num: string) => {
                    temp_tableData_data['taxRate' + num] = ele.taxRate
                    temp_tableData_data['unitPrice' + num] = ele.unitPrice
                    const nnum = nowList.filter((doc: any) => {
                        return ele.detailsId === doc.id
                    })[0]?.num
                    allPrice += nnum * ele.unitPrice

                })
                temp_tableData_data['allPrice'] = allPrice
                temp_tableData.push(temp_tableData_data)
            }
            tableData.value = temp_tableData
            tableLoding.value = false
        }
    })
}


const getSupplyQutationListFirst = (nowList: any, tableRound: number) => {
    if (!props.propsid) {
        setTimeout(() => {
            getSupplyQutationList(nowList)
        }, 500);
    } else {
        executeApi.getSupplyQutationList(props.propsid, tableRound).then((res: any) => {
            if (res.success) {
                let temp_tableData = <any>[]
                //获取其中的键值对
                const temp_obj = res.obj
                for (let key in temp_obj) {
                    const temp_tableData_data = <any>{}
                    const THEVALUE = temp_obj[key]
                    temp_tableData_data['company'] = key //公司名赋值
                    let allPrice = 0
                    THEVALUE.forEach((ele: any, num: string) => {
                        temp_tableData_data['taxRate' + num] = ele.taxRate
                        temp_tableData_data['unitPrice' + num] = ele.unitPrice
                        const nnum = nowList.filter((doc: any) => {
                            return ele.detailsId === doc.id
                        })[0].num
                        allPrice += nnum * ele.unitPrice

                    })
                    temp_tableData_data['allPrice'] = allPrice
                    temp_tableData.push(temp_tableData_data)
                }
                tableDataFirst.value = temp_tableData
                tableLoding.value = false
            }
        })
    }
}
//获取渲染数组的colums
const tableColumns = ref<any>()
const getColumns = (listDetails: any) => {
    let temp_column_list = <any>[]
    listDetails.forEach((item: any, index: string) => {
        let temp_column = <any>{}
        temp_column['title'] = item.materialName
        temp_column['taxRate'] = 'taxRate' + index
        temp_column['unitPrice'] = 'unitPrice' + index
        temp_column['num'] = item.num
        temp_column_list.push(temp_column)
    })
    tableColumns.value = temp_column_list
}
//***************************************************************************** */

//参与商家得分修改*******************
const publicityData = ref<any>([
])
const getPublicityData = () => {
    if (!props.propsid) {
        setTimeout(() => {
            getPublicityData()
        }, 500);
    } else {
        if (props.baseData?.companyList) {
            publicityData.value = props.baseData.companyList
            executeApi.getSupplyScoreList(props.propsid).then((res: any) => {
                if (res.success) {
                    res.obj.forEach((item: any) => {
                        publicityData.value.forEach((ele: any) => {
                            if (ele.companyId === item.companyId) {
                                ele['score'] = item.score
                            }
                        })
                    })
                }
            })
        }

    }
}
const dataBlur = (row: any) => {
    excutePartake.updataScore(row.id, row.score).then((res: any) => {
        if (res.success) {
            getPublicityData()
        }
    })
}
//********************************** */


//响应时间等...
//respondToQuotes响应报价
const respondToQuotes = ref<string>('')
const getRespondToQuotes = () => {
    const today = dayjs();
    const formattedToday = today.format('YYYY-MM-DD HH:MM:ss');
    if (props.baseData?.endDate) {
        respondToQuotes.value = `${dateDiff(props.baseData.endDate, formattedToday)}`
    } else {
        setTimeout(() => {
            getRespondToQuotes()
        }, 500);
    }
}
function dateDiff(date1: string, date2: string) {
    // 将日期字符串转换为Date对象
    const d1: any = new Date(date1);
    const d2: any = new Date(date2);
    // 计算两个日期之间的毫秒差值
    if (d2.getTime() < d1.getTime()) {
        let diffMilliseconds = Math.abs(d2 - d1);
        // 将毫秒差值转换为天数
        // const diffDays = Math.ceil(diffMilliseconds / (1000 * 60 * 60 * 24));
        const days = Math.floor(diffMilliseconds / (24 * 60 * 60 * 1000));
        diffMilliseconds %= 24 * 60 * 60 * 1000;
        const hours = Math.floor(diffMilliseconds / (60 * 60 * 1000));
        diffMilliseconds %= 60 * 60 * 1000;
        const minutes = Math.floor(diffMilliseconds / (60 * 1000));
        diffMilliseconds %= 60 * 1000;
        const seconds = Math.floor(diffMilliseconds / 1000);
        return `还剩余${days}天${hours}小时${minutes}分钟`;
    } else {
        return ''
    }
}



//********* */
const initialize = () => {
    // getexecuteListList() 答疑改为点击后触发

    //供应商响应文件列表
    getSupplyResponseFileList() 
    //供应商列表
    getPurchaseList()
    //公示
    getPublicityData()
    //获取响应时间
    getRespondToQuotes()
    const purchaseStatus = props.baseData?.purchaseStatus
    if(purchaseStatus == 3){
        current.value = 1
    }
    if(purchaseStatus == 4){
        current.value = 2
    }
}

defineExpose({ initialize })



</script>

<style lang="less" scoped>
@import './index.less';

:deep(.ant-upload) {
    background-color: #fff;
    width: 156px !important;
    height: 156px !important;
}
</style>