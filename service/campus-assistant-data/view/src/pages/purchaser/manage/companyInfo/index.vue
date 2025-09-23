<template>
  <div class="page-content-s-i">
    <div class="title_content">
      <div class="info">
        <LeftOutlined @click="getRouterBack" style="margin-right: 12px;"/>
        企业详情
      </div>
    </div>

    <div class="auth_content">
      <div class="userInfo">
        <div class="userItem">
          <div class="info_items">
            <div class="item">
              <span>企业名称:</span>
              <span>{{ formDataBasic.companyName }}</span>
            </div>
            <div class="item">
              <span>法人:</span>
              <span>{{ formDataBasic.legalPerson }}</span>
            </div>
          </div>
        </div>
        <div class="audit">
          <!-- "1":未认证 -->
          <!-- "2":审核中 -->
          <!-- "3":已认证 -->
          <!-- "4":未通过 -->
          <!-- <a-button class="icon" v-if="formDataBasic.supplierStatus == '1'" 
            @click="submitAudit('2')">提交审核</a-button>
          <a-button class="icon" v-if="formDataBasic.supplierStatus == '2'" 
            @click="submitAudit('1')">撤销审核</a-button>
          <a-button class="icon" v-if="formDataBasic.supplierStatus == '4'" 
            @click="submitAudit('2')">重新审核</a-button> -->
        </div>
      </div>
      <div class="auth_status">
        <div class="status_item" v-if="formDataBasic.supplierStatus == '1'" >
          <img src="@/assets/svgIcon/unAuthenticated.svg">
          <span style="color: var(--unnamed, #86909C);">未认证</span>
        </div>
        <div class="status_item" v-if="formDataBasic.supplierStatus == '2'" >
          <img src="@/assets/svgIcon/verifying.svg" alt="" srcset="">
          <span style="color: #FF7D00;">审核中</span>
        </div>
        <div class="status_item" v-if="formDataBasic.supplierStatus == '3'" >
          <img src="@/assets/svgIcon/authenticated.svg">
          <span>已认证</span>
        </div>
        <div class="status_item" v-if="formDataBasic.supplierStatus == '4'" >
          <img src="@/assets/svgIcon/unPassed.svg">
          <span style="color: var(--5, #F53F3F);">未通过</span>
        </div>
      </div>
    </div>

    <div class="content_items">
      <div class="anchor_head">
        <div class="head">
          <a-anchor direction="horizontal" :affix="false" :getContainer="getContainer" @click="handleNavClick" :items="[
            {
              key: 'part-1',
              href: '#info_id1',
              title: '基本信息',
            },
            {
              key: 'part-2',
              href: '#info_id2',
              title: '经营范围',
            },
            {
              key: 'part-3',
              href: '#info_id3',
              title: '资质文件',
            },
            {
              key: 'part-4',
              href: '#info_id4',
              title: '专利技术',
            },
            {
              key: 'part-5',
              href: '#info_id5',
              title: '社会诚信',
            },
            {
              key: 'part-6',
              href: '#info_id6',
              title: '供应清单',
            },
            {
              key: 'part-7',
              href: '#info_id7',
              title: '履约评价',
            },
          ]">
          </a-anchor>
        </div>
      </div>

      <div id="anchor_content" class="anchor_content">
        <div>
          <div id="info_id1" class="anchor_item">
            <span>基本信息</span>
          </div>
          <div class="item_content1">
            <a-form :model="formDataBasic" ref="formRefBasic" labelWrap disabled
              :label-col="{ span: 8 }">
              <a-row wrap>
                <a-col :span="12">
                  <a-form-item label="企业名称" name="companyName">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.companyName">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="登记状态" name="registrationStatus">

                    <!-- 存续、在业、吊销、注销、迁入、迁出、停业、清算 -->
                    <a-select :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.registrationStatus">
                      <a-select-option value="0">续存</a-select-option>
                      <a-select-option value="1">在业</a-select-option>
                      <a-select-option value="2">吊销</a-select-option>
                      <a-select-option value="3">注销</a-select-option>
                      <a-select-option value="4">迁入</a-select-option>
                      <a-select-option value="5">迁出</a-select-option>
                      <a-select-option value="6">停业</a-select-option>
                      <a-select-option value="7">清算</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="统一社会信用代码/纳税人识别号" name="creditCode" :label-col="{ span: 8 }">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.creditCode">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="成立日期" name="establishDate">
                    <a-date-picker style="width: 100%;" :format="dateFormat" :valueFormat="dateFormat"
                      :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.establishDate">
                    </a-date-picker>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="法定代表人" name="legalPerson">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.legalPerson">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="注册资本" name="registeredCapital">
                    <a-input-number style="width: 100%;" :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.registeredCapital">
                    </a-input-number>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="实缴资本" name="paidCapital">
                    <a-input-number style="width: 100%;" :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.paidCapital">
                    </a-input-number>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="企业编码" name="companyCode">
                      <a-input
                          :placeholder="$t('placeholder.pleaseEnter')"
                          v-model:value="formDataBasic.companyCode">
                      </a-input>
                  </a-form-item>                
                </a-col>

                <a-col :span="12">
                  <a-form-item label="纳税人资质" name="taxpayerQualification">
                    <!-- 一般纳税人和小规模纳税人 -->
                    <a-select :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.taxpayerQualification">
                      <a-select-option value="0">一般纳税人</a-select-option>
                      <a-select-option value="1">小规模纳税人</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="工商注册号" name="registerNumber">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.registerNumber">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="人员规模" name="staffSize">
                    <a-select :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.staffSize">
                      <!-- 大型企业：从业人员≥1000人，且营业收入8000万元； -->
                      <!-- 中型企业：从业人员≥400人，且营业收入2000万元-8000万元；； -->
                      <!-- 小型企业：从业人员≥30人，且营业收入500万元-2000万元； -->
                      <!-- 微型企业：从业人员<30人，或营业收入<500万元。 -->
                      <a-select-option value="0">0~29人</a-select-option>
                      <a-select-option value="1">30~299人</a-select-option>
                      <a-select-option value="2">300~999人</a-select-option>
                      <a-select-option value="3">1000人以上</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="参保人数" name="insuredPersons">
                    <a-input-number style="width: 100%;" :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.insuredPersons">
                    </a-input-number>
                  </a-form-item>
                </a-col>

                <a-col :span="24">
                  <a-form-item label="注册地址" name="address" :label-col="{ span: 4 }">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.address">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="24">
                  <a-form-item label="通信地址" name="mailAddress" :label-col="{ span: 4 }">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.mailAddress">
                    </a-input>
                  </a-form-item>
                </a-col>
              </a-row>
            </a-form>
          </div>
        </div>

        <div>
          <div id="info_id2" class="anchor_item">
            <span>经营范围</span>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource2" :columns="columns2" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id3" class="anchor_item">
            <span>资质文件</span>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource3" :columns="columns3" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id4" class="anchor_item">
            <span>专利技术</span>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource4" :columns="columns4" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id5" class="anchor_item">
            <span>社会诚信</span>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource5" :columns="columns5" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id6" class="anchor_item">
            <span>供应清单</span>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource6" :columns="columns6" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id7" class="anchor_item"><span>履约评价</span></div>
          <div class="item_content2">
            <a-table :dataSource="dataSource7" :columns="columns7" :pagination="false" size="small" bordered>
              <template v-slot:num="slotProps">
                {{ slotProps.index + 1 }}
              </template>
            </a-table>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from "vue"
import { companyApi } from "@/api/company";
import { LeftOutlined } from '@ant-design/icons-vue';
import { useRouter, useRoute } from 'vue-router';
const $route = useRoute();
const $router = useRouter();
const dateFormat = 'YYYY-MM-DD';

// 锚点跟随
const getContainer = () => {
  return document.getElementById("anchor_content");
};
const handleNavClick = (e: MouseEvent) => {
  // @ts-ignore
  e.preventDefault();
};


// 基础信息表单
// 数据格式
interface IFormDataBasic {
  id:string;
  companyName:string;// (value = "公司名称")
  registrationStatus:string;// (value = "登记状态")
  creditCode:string;// (value = "统一信用识别码")
  establishDate:string;// (value = "成立日期")
  legalPerson:string;// (value = "法定代表人")
  registeredCapital:number|null;// (value = "注册资本")
  paidCapital:number|null;// (value = "实缴资本")
  companyCode:string;// (value = "企业编码")
  taxpayerQualification:string;// (value = "纳税人资质")
  taxpayerCode:string;// (value = "纳税人识别号")
  registerNumber:string;// (value = "工商注册号")
  staffSize:string;// (value = "人员规模")
  insuredPersons:number|null;// (value = "参保人数")
  address:string;// (value = "注册地址")
  mailAddress:string;// (value = "通信地址")
  purchaser:boolean;// (value = "是否是采购商 0否 1是")
  supplier:boolean;// (value = "是否是供应商 0否 1是")
  supplierStatus:string;// (value = "供应商注册状态")

// (value = "经营范围")
//  List<SupplyBusinessScope> businessScopes:any[];
// (value = "资质文件")
//  List<SupplyQualificationDocuments> qualificationDocuments;
// (value = "专利技术")
//  List<SupplyPatentTechnology> patentTechnologies;
// (value = "社会诚信")
//  List<SupplySocialIntegrity> socialIntegrates;
// (value = "供应清单")
//  List<SupplyList> supplyList;
// (value = "履约评价")
//  List<PerformanceEvaluation> performanceEvaluation;
}

const formDataBasic = reactive<IFormDataBasic>({
  id:'',
  companyName:'',           // (value = "公司名称")
  registrationStatus:'',    // (value = "登记状态")
  creditCode:'',            // (value = "统一信用识别码")
  establishDate:'',         // (value = "成立日期")
  legalPerson:'',           // (value = "法定代表人")
  registeredCapital:null,   // (value = "注册资本")
  paidCapital:null,         // (value = "实缴资本")
  companyCode:'',           // (value = "企业编码")
  taxpayerQualification:'', // (value = "纳税人资质")
  taxpayerCode:'',          // (value = "纳税人识别号")
  registerNumber:'',        // (value = "工商注册号")
  staffSize:'',             // (value = "人员规模")
  insuredPersons:null,      // (value = "参保人数")
  address:'',               // (value = "注册地址")
  mailAddress:'',           // (value = "通讯地址")
  purchaser:false,          // (value = "是否是采购商 0否 1是")
  supplier:true,            // (value = "是否是供应商 0否 1是")
  supplierStatus:'',        // (value = "供应商注册状态")

});

const getCompanyId = () => {
  let companyId = $route.params.id as string;
  return companyId;
}
const getRouterBack = () => {
  $router.back();
}

// 经营范围
const dataSource2 = ref<any[]>([])
const columns2 = [
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
    align: 'center',
  },
];

// 资质文件
const dataSource3 = ref<any[]>([])
const columns3 = [
  {
    title: '资质类型',
    dataIndex: 'qualificationsType',
    key: 'qualificationsType',
    align: 'center',
  },
  {
    title: '证书编号',
    dataIndex: 'certificateNo',
    key: 'certificateNo',
    align: 'center',
  },
  {
    title: '资质名称',
    dataIndex: 'qualificationsName',
    key: 'qualificationsName',
    align: 'center',
  },
  {
    title: '发证日期',
    dataIndex: 'issuanceDate',
    key: 'issuanceDate',
    align: 'center',
  },
  {
    title: '有效期',
    dataIndex: 'periodValidity',
    key: 'periodValidity',
    align: 'center',
  },
  {
    title: '发证机关',
    dataIndex: 'licenceIssuingAuthority',
    key: 'licenceIssuingAuthority',
    align: 'center',
  },
];

// 专利技术
const dataSource4 = ref<any[]>([])
const columns4 = [
  {
    title: '发明名称',
    dataIndex: 'inventName',
    key: 'inventName',
    align: 'center',
  },
  {
    title: '专利类型',
    dataIndex: 'patentType',
    key: 'patentType',
    align: 'center',
  },
  {
    title: '法律状态',
    dataIndex: 'lawStatus',
    key: 'lawStatus',
    align: 'center',
  },
  {
    title: '申请号',
    dataIndex: 'applyNo',
    key: 'applyNo',
    align: 'center',
  },
  {
    title: '申请日期',
    dataIndex: 'applyDate',
    key: 'applyDate',
    align: 'center',
  },
  {
    title: '公开(公告)号',
    dataIndex: 'openNo',
    key: 'openNo',
    align: 'center',
  },
  {
    title: '公开(公告)日期',
    dataIndex: 'openDate',
    key: 'openDate',
    align: 'center',
  },
  {
    title: '发明人',
    dataIndex: 'inventor',
    key: 'inventor',
    align: 'center',
  },
];

// 社会诚信
const dataSource5 = ref<any[]>([])
const columns5 = [
  {
    title: '信用类型',
    dataIndex: 'creditType',
    key: 'creditType',
    align: 'center',
  },
  {
    title: '评价年度',
    dataIndex: 'evaluationYear',
    key: 'evaluationYear',
    align: 'center',
  },
  {
    title: '信用等级',
    dataIndex: 'creditGrade',
    key: 'creditGrade',
    align: 'center',
  },
  {
    title: '评价单位',
    dataIndex: 'evaluationUnit',
    key: 'evaluationUnit',
    align: 'center',
  },
  {
    title: '发布日期',
    dataIndex: 'releaseDate',
    key: 'releaseDate',
    align: 'center',
  },
  {
    title: '证明材料',
    dataIndex: 'fileName',
    key: 'fileName',
    align: 'center',
  },
];

// 供应清单
const dataSource6 = ref<any[]>([])
const columns6 = [
  {
    title: '可供类目',
    dataIndex: 'supplyType',
    key: 'supplyType',
    align: 'center',
  },
  {
    title: '可供物料',
    dataIndex: 'supplyMaterial',
    key: 'supplyMaterial',
    align: 'center',
  },
];

// 履约评价
const dataSource7 = ref<any[]>([])
const columns7 = [
  {
    title: '合同编号',
    dataIndex: 'contractNo',
    key: 'contractNo',
    align: 'center',
  },
  {
    title: '项目名称',
    dataIndex: 'projectName',
    key: 'projectName',
    align: 'center',
  },
  {
    title: '含税总金额(元)',
    dataIndex: 'totalAmount',
    key: 'totalAmount',
    align: 'center',
  },
  {
    title: '履约情况',
    dataIndex: 'performanceEvaluationStatus',
    key: 'performanceEvaluationStatus',
    align: 'center',
  },
  {
    title: '质量评价',
    dataIndex: 'qualityEvaluation',
    key: 'qualityEvaluation',
    align: 'center',
  },
];

const initSupplierInfo = () => {
  // 经营范围
  dataSource2.value.length = 0;
  // 资质文件
  dataSource3.value.length = 0;
  // 专利技术
  dataSource4.value.length = 0;
  // 社会诚信
  dataSource5.value.length = 0;
  // 供应清单
  dataSource6.value.length = 0;
  // 履约评价
  dataSource7.value.length = 0;
  companyApi.getSupplierCompanyInfo(getCompanyId()).then((res:any) => {
    if (res.success) {      
      formDataBasic.id = res.obj.id;          
      formDataBasic.companyName = res.obj.companyName;           // (value = "公司名称")
      formDataBasic.registrationStatus = res.obj.registrationStatus;    // (value = "登记状态")
      formDataBasic.creditCode = res.obj.creditCode;            // (value = "统一信用识别码")
      formDataBasic.establishDate = res.obj.establishDate;         // (value = "成立日期")
      formDataBasic.legalPerson = res.obj.legalPerson;           // (value = "法定代表人")
      formDataBasic.registeredCapital = res.obj.registeredCapital;   // (value = "注册资本")
      formDataBasic.paidCapital = res.obj.paidCapital;         // (value = "实缴资本")
      formDataBasic.companyCode = res.obj.companyCode;           // (value = "企业编码")
      formDataBasic.taxpayerQualification = res.obj.taxpayerQualification; // (value = "纳税人资质")
      formDataBasic.taxpayerCode = res.obj.taxpayerCode;          // (value = "纳税人识别号")
      formDataBasic.registerNumber = res.obj.registerNumber;        // (value = "工商注册号")
      formDataBasic.staffSize = res.obj.staffSize;             // (value = "人员规模")
      formDataBasic.insuredPersons = res.obj.insuredPersons;      // (value = "参保人数")
      formDataBasic.address = res.obj.address;               // (value = "注册地址")
      formDataBasic.mailAddress = res.obj.mailAddress;           // (value = "通讯地址")
      formDataBasic.purchaser = res.obj.purchaser;      
      formDataBasic.supplier = res.obj.supplier;               
      formDataBasic.supplierStatus = res.obj.supplierStatus;      

      dataSource2.value = res.obj.businessScopes;
      dataSource3.value = res.obj.qualificationDocuments;
      dataSource4.value = res.obj.patentTechnologies;
      dataSource5.value = res.obj.socialIntegrates;
      dataSource6.value = res.obj.supplyList;
      dataSource7.value = res.obj.performanceEvaluation;
    }
  })
}

onMounted(() => {
  initSupplierInfo();
});
</script>

<style lang="less" scoped>
@import 'index.less';
</style>
