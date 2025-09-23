<template>
  <div class="page-content-s-i">
    <div class="title_content">
      <div class="info">信息维护</div>
    </div>

    <div class="head_info" v-if="true">
      <span>有5项内容修改需要提交审核</span>
    </div>
    <div class="head_info_null" v-else>
      <span></span>
    </div>

    <div class="auth_content">
      <div class="userInfo">
        <div class="userItem">
          <div class="info_items">
            <div class="item">
              <span>用户姓名:</span>
              <span>{{ userInfo.name }}</span>
            </div>
            <div class="item">
              <span>手机号:</span>
              <span>{{ userInfo.phone }}</span>
            </div>
          </div>
          <div class="reset" @click="resetAccount">
            <span>重置账号</span>
          </div>
        </div>
        <div class="audit">
          <!-- "1":未认证 -->
          <!-- "2":审核中 -->
          <!-- "3":已认证 -->
          <!-- "4":未通过 -->
          <a-button class="icon" v-if="formDataBasic.supplierStatus == '1'" @click="submitAudit()">提交审核</a-button>
          <!-- <a-button class="icon" v-if="formDataBasic.supplierStatus == '2'" @click="submitAudit()">撤销审核</a-button> -->
          <!-- <a-button class="icon" v-if="formDataBasic.supplierStatus == '4'"
            @click="submitAudit('2')">重新审核</a-button> -->
        </div>
      </div>
      <div class="auth_status">
        <div class="status_item" v-if="formDataBasic.supplierStatus == '1'">
          <img src="../../../assets/svgIcon/unAuthenticated.svg">
          <span style="color: var(--unnamed, #86909C);">未认证</span>
        </div>
        <div class="status_item" v-if="formDataBasic.supplierStatus == '2'">
          <img src="../../../assets/svgIcon/verifying.svg">
          <span style="color: #FF7D00;">审核中</span>
        </div>
        <div class="status_item" v-if="formDataBasic.supplierStatus == '3'">
          <img src="../../../assets/svgIcon/authenticated.svg">
          <span>已认证</span>
        </div>
        <div class="status_item" v-if="formDataBasic.supplierStatus == '4'">
          <img src="../../../assets/svgIcon/unPassed.svg">
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
        <!-- <div class="head_info" v-if="true">
          <span>有5项内容修改需要提交审核</span>
        </div>
        <div class="head_info_null" v-else>
          <span></span>
        </div> -->
      </div>

      <div id="anchor_content" class="anchor_content">
        <div>
          <div id="info_id1" class="anchor_item">
            <span>基本信息</span>
            <a-button type="primary" size="small"
              v-if="formDataBasic.supplierStatus !== '2' && formDataBasic.supplierStatus !== '3'"
              @click="saveBasicInfo">保存</a-button>
          </div>
          <div class="item_content1">
            <a-form :model="formDataBasic" ref="formRefBasic" labelWrap
              :disabled="formDataBasic.supplierStatus == '2' || formDataBasic.supplierStatus == '3'"
              :rules="formRulesBasic" :label-col="{ span: 8 }">
              <a-row wrap>
                <a-col :span="12">
                  <a-form-item label="企业名称" name="companyName">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.companyName">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="登记状态" name="registrationStatus">
                    <!-- <a-input :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.registrationStatus">
                    </a-input> -->

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
                  <a-row justify="space-between">
                    <a-col offset="4">
                      <a-form-item label="注册资本" name="registeredCapital">
                        <a-input style="width: 260px;" :placeholder="$t('placeholder.pleaseEnter')"
                          v-model:value="formDataBasic.registeredCapital">
                        </a-input>
                      </a-form-item>
                    </a-col>
                    <a-col>
                      <a-form-item label="" name="registeredCurrency">
                        <a-select v-model:value="formDataBasic.registeredCurrency" placeholder="请选择"
                          style="width: 100px;">
                          <a-select-option v-for="item in currencyList" :key="item" :label="item"
                            :value="item"></a-select-option>
                        </a-select>
                      </a-form-item>
                    </a-col>
                  </a-row>
                </a-col>

                <a-col :span="12">
                  <a-row justify="space-between">
                    <a-col offset="4">
                      <a-form-item label="实缴资本" name="paidCapital">
                        <a-input style="width: 260px;" :placeholder="$t('placeholder.pleaseEnter')"
                          v-model:value="formDataBasic.paidCapital">
                        </a-input>
                      </a-form-item>
                    </a-col>
                    <a-col>
                      <a-form-item label="" name="paidCurrency">
                        <a-select v-model:value="formDataBasic.paidCurrency" placeholder="请选择" style="width: 100px;">
                          <a-select-option v-for="item in currencyList" :key="item" :label="item"
                            :value="item"></a-select-option></a-select>
                      </a-form-item>
                    </a-col>
                  </a-row>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="企业编码" name="companyCode">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.companyCode">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="纳税人资质" name="taxpayerQualification">
                    <!-- <a-input :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.taxpayerQualification">
                    </a-input> -->

                    <!-- 一般纳税人和小规模纳税人 -->
                    <a-select :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.taxpayerQualification">
                      <a-select-option value="0">一般纳税人</a-select-option>
                      <a-select-option value="1">小规模纳税人</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>

                <!-- <a-col :span="12">
                  <a-form-item label="纳税人识别号" name="taxpayerCode">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.taxpayerCode">
                    </a-input>
                  </a-form-item>
                </a-col> -->

                <a-col :span="12">
                  <a-form-item label="工商注册号" name="registerNumber">
                    <a-input :placeholder="$t('placeholder.pleaseEnter')" v-model:value="formDataBasic.registerNumber">
                    </a-input>
                  </a-form-item>
                </a-col>

                <a-col :span="12">
                  <a-form-item label="人员规模" name="staffSize">
                    <!-- <a-input-number style="width: 100%;" :placeholder="$t('placeholder.pleaseEnter')"
                      v-model:value="formDataBasic.staffSize">
                    </a-input-number> -->

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
            <a-button type="primary" ghost size="small"
              v-if="formDataBasic.supplierStatus !== '2' && formDataBasic.supplierStatus !== '3'"
              @click="addEditColumns2Open('add')">新增</a-button>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource2" :columns="columns2" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.dataIndex === 'operate'">
                  <div class="operate-style">
                    <!-- 编辑 -->
                    <a-button type="link" :disabled="formDataBasic.supplierStatus == '3'"
                      @click="addEditColumns2Open('edit', record)">
                      {{ $t('placeholder.change') }}
                    </a-button>
                    <!-- 删除 -->
                    <!-- <a-button type="link" danger @click="delColumns2ById(record.id)"> -->
                    <a-button type="link" danger :disabled="formDataBasic.supplierStatus == '3'"
                      @click="openConfirm(2, record.id)">
                      {{ $t('placeholder.delete') }}
                    </a-button>
                  </div>
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id3" class="anchor_item">
            <span>资质文件</span>
            <a-button type="primary" ghost size="small"
              v-if="formDataBasic.supplierStatus !== '2' && formDataBasic.supplierStatus !== '3'"
              @click="addEditColumns3Open('add')">新增</a-button>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource3" :columns="columns3" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.dataIndex === 'operate'">
                  <div class="operate-style">
                    <!-- 编辑 -->
                    <a-button type="link" :disabled="formDataBasic.supplierStatus == '3'"
                      @click="addEditColumns3Open('edit', record)">
                      {{ $t('placeholder.change') }}
                    </a-button>
                    <!-- 删除 -->
                    <!-- <a-button type="link" danger @click="delColumns3ById(record.id)"> -->
                    <a-button type="link" danger :disabled="formDataBasic.supplierStatus == '3'"
                      @click="openConfirm(3, record.id)">
                      {{ $t('placeholder.delete') }}
                    </a-button>
                  </div>
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id4" class="anchor_item">
            <span>专利技术</span>
            <a-button type="primary" ghost size="small"
              v-if="formDataBasic.supplierStatus !== '2' && formDataBasic.supplierStatus !== '3'"
              @click="addEditColumns4Open('add')">新增</a-button>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource4" :columns="columns4" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.dataIndex === 'operate'">
                  <div class="operate-style">
                    <!-- 编辑 -->
                    <a-button type="link" :disabled="formDataBasic.supplierStatus == '3'"
                      @click="addEditColumns4Open('edit', record)">
                      {{ $t('placeholder.change') }}
                    </a-button>
                    <!-- 删除 -->
                    <!-- <a-button type="link" danger @click="delColumns4ById(record.id)"> -->
                    <a-button type="link" danger :disabled="formDataBasic.supplierStatus == '3'"
                      @click="openConfirm(4, record.id)">
                      {{ $t('placeholder.delete') }}
                    </a-button>
                  </div>
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id5" class="anchor_item">
            <span>社会诚信</span>
            <a-button type="primary" ghost size="small"
              v-if="formDataBasic.supplierStatus !== '2' && formDataBasic.supplierStatus !== '3'"
              @click="addEditColumns5Open('add')">新增</a-button>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource5" :columns="columns5" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.dataIndex === 'operate'">
                  <div class="operate-style">
                    <!-- 编辑 -->
                    <a-button type="link" :disabled="formDataBasic.supplierStatus == '3'"
                      @click="addEditColumns5Open('edit', record)">
                      {{ $t('placeholder.change') }}
                    </a-button>
                    <!-- 删除 -->
                    <!-- <a-button type="link" danger @click="delColumns5ById(record.id)"> -->
                    <a-button type="link" danger :disabled="formDataBasic.supplierStatus == '3'"
                      @click="openConfirm(5, record.id)">
                      {{ $t('placeholder.delete') }}
                    </a-button>
                  </div>
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id6" class="anchor_item">
            <span>供应清单</span>
            <a-button type="primary" ghost size="small"
              v-if="formDataBasic.supplierStatus !== '2' && formDataBasic.supplierStatus !== '3'"
              @click="addEditColumns6Open('add')">新增</a-button>
          </div>
          <div class="item_content2">
            <a-table :dataSource="dataSource6" :columns="columns6" :pagination="false" size="small" bordered>
              <template #bodyCell="{ column, text, record, index }">
                <template v-if="column.dataIndex === 'num'">
                  {{ index + 1 }}
                </template>
                <template v-if="column.dataIndex === 'operate'">
                  <div class="operate-style">
                    <!-- 编辑 -->
                    <a-button type="link" :disabled="formDataBasic.supplierStatus == '3'"
                      @click="addEditColumns6Open('edit', record)">
                      {{ $t('placeholder.change') }}
                    </a-button>
                    <!-- 删除 -->
                    <!-- <a-button type="link" danger @click="delColumns6ById(record.id)"> -->
                    <a-button type="link" danger :disabled="formDataBasic.supplierStatus == '3'"
                      @click="openConfirm(6, record.id)">
                      {{ $t('placeholder.delete') }}
                    </a-button>
                  </div>
                </template>
              </template>
            </a-table>
          </div>
        </div>

        <div>
          <div id="info_id7" class="anchor_item"><span>履约评价</span></div>
          <div class="item_content2">
            <a-table :dataSource="dataSource7" :columns="columns7" :pagination="false" size="small" bordered>
            </a-table>
          </div>
        </div>
      </div>

    </div>

    <!-- 经营范围 -->
    <addEditABusiness v-if="columns2Data" :visible="columns2DialogVisible" :type="columns2DialogType"
      :form-data="columns2Data" @handle-cancel="columns2DialogVisible = false;" @handle-ok="addEditColumns2Execute">
    </addEditABusiness>
    <!-- 资质文件 -->
    <addEditBQualify v-if="columns3Data" :visible="columns3DialogVisible" :type="columns3DialogType"
      :form-data="columns3Data" @handle-cancel="columns3DialogVisible = false;" @handle-ok="addEditColumns3Execute">
    </addEditBQualify>
    <!-- 专利技术 -->
    <addEditCPatent v-if="columns4Data" :visible="columns4DialogVisible" :type="columns4DialogType"
      :form-data="columns4Data" @handle-cancel="columns4DialogVisible = false;" @handle-ok="addEditColumns4Execute">
    </addEditCPatent>
    <!-- 社会诚信 -->
    <addEditDSocial v-if="columns5Data" :visible="columns5DialogVisible" :type="columns5DialogType"
      :form-data="columns5Data" @handle-cancel="columns5DialogVisible = false;" @handle-ok="addEditColumns5Execute"
      ref="addEditDSocialRef">
    </addEditDSocial>
    <!-- 供应清单 -->
    <addEditEList v-if="columns6Data" :visible="columns6DialogVisible" :type="columns6DialogType"
      :form-data="columns6Data" @handle-cancel="columns6DialogVisible = false;" @handle-ok="addEditColumns6Execute">
    </addEditEList>
    <!-- 删除弹框 -->
    <DelModal ref="delRef" @delData="delData"></DelModal>
    <a-modal v-model:open="chooseCompanyVisible" title="选择入驻企业" @ok="handleFilterCompanyOk" @cancel="handleFilterCompanyCancel">
      <a-form :model="purchaserForm" ref="purchaserRef">
        <a-form-item label="入驻企业" name="purchaserId" :rules="[{ required: true, message: i18n.global.t('placeholder.pleaseEnter') }]">
          <a-select v-model:value="purchaserForm.purchaserId" show-search placeholder="请选择" style="width: 100%"
            :options="companyList" :filter-option="filterOption"
            :field-names="{ label: 'companyName', value: 'id' }"></a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import i18n from "@/i18n";
import { onMounted, reactive, ref, h } from "vue"
import { companyApi } from "@/api/company";
import { storeToRefs } from 'pinia'
import { useDataStore } from '@/store/userStatus';
// 经营范围
import { supplyBusinessScopeApi } from "@/api/SupplyBusinessScope";
import addEditABusiness from "./dialog/addEditABusiness.vue";
// 资质文件
import { supplyQualificationDocumentsApi } from "@/api/SupplyQualificationDocuments";
import addEditBQualify from "./dialog/addEditBQualify.vue";
// 专利技术
import { supplyPatentTechnologyApi } from "@/api/SupplyPatentTechnology";
import addEditCPatent from "./dialog/addEditCPatent.vue";
// 社会诚信
import { supplySocialIntegrityApi } from "@/api/SupplySocialIntegrity";
import addEditDSocial from "./dialog/addEditDSocial.vue";
// 供应清单
import { supplyListApi } from "@/api/SupplyList";
import addEditEList from "./dialog/addEditEList.vue";
// 删除弹窗
import DelModal from '@/components/DelModal/delDialogWithNoInfo.vue';
import { message } from "ant-design-vue";
import datjs from 'dayjs'
import { Modal } from 'ant-design-vue';
import { ExclamationCircleOutlined } from '@ant-design/icons-vue';
import { userApi } from "@/api/user";
const store = useDataStore();
const { userInfo, isLogin } = storeToRefs(store);
const dateFormat = 'YYYY-MM-DD';

// 锚点跟随
const getContainer = () => {
  return document.getElementById("anchor_content");
};
const handleNavClick = (e: MouseEvent) => {
  // @ts-ignore
  e.preventDefault();
};
const companyList = ref<any>([])
const currencyList = ref<any>([])
const chooseCompanyVisible = ref<boolean>(false)
const purchaserForm = reactive({
  purchaserId: undefined
})
const initFilterCompanyList = () => {
  companyApi.getCompanyList().then(res => {
    const { obj, success }: { obj: any, success: boolean } = res
    if (success) {
      let local = localStorage.getItem('userInfo') as any
      let storage = JSON.parse(local)
      companyList.value = obj.filter((item: any) => item.id !== storage.companyId)
    }
  })
  companyApi.getCurrencyList().then(res => {
    const { success, obj } = res
    if (success) {
      currencyList.value = obj
    }
  })
}

const filterOption = (input: string, option: any) => {
  return option.companyName.indexOf(input) >= 0;
};
const purchaserRef = ref()
const handleFilterCompanyOk = () => {
  purchaserRef.value.validate().then(() => {
    companyApi.putCompanyAuditSubmit(purchaserForm.purchaserId).then(res => {
      message.success("提交成功");
      // 成功后刷新供应商信息
      initSupplierInfo();
      userApi({}).getUserInfo().then((res: any) => {
        if (res.success) {
          localStorage.setItem("userInfo", JSON.stringify(res.obj));
          userInfo.value = res.obj;
        }
      })
    }).finally(()=> {
      handleFilterCompanyCancel()
    })
  })
}
const handleFilterCompanyCancel = () => {
  purchaserForm.purchaserId = undefined
  chooseCompanyVisible.value = false
  purchaserRef.value.resetFields()
}
// 提交审核
// <!-- "1":未认证 -->
// <!-- "2":审核中 -->
// <!-- "3":已认证 -->
// <!-- "4":未通过 -->
const submitAudit = () => {
  chooseCompanyVisible.value = true
  // if (supplierStatus == '2') {
  //   // 提交审核状态
  //   companyApi.putCompanyAuditStatus(supplierStatus).then((res: any) => {
  //     if (res.success) {
  //       message.success("提交成功");
  //       // 成功后刷新供应商信息
  //       initSupplierInfo();

  // putCompanyAuditSubmit
  //       userApi({}).getUserInfo().then((res: any) => {
  //         if (res.success) {
  //           localStorage.setItem("userInfo", JSON.stringify(res.obj));
  //           userInfo.value = res.obj;
  //         }
  //       })

  //     }
  //   })
  // } else {
  //   companyApi.putCompanyAuditStatus(supplierStatus).then((res: any) => {
  //     if (res.success) {
  //       message.success("提交成功");
  //       initSupplierInfo();
  //     }
  //   })
  // }
}

// 重置密码
const resetAccount = () => {
  console.log('resetAccount');
  // Modal.confirm({
  //   title: '重置账号?',
  //   icon: h(ExclamationCircleOutlined),
  //   content: h('div', { style: 'color:red;' }, 'Some descriptions'),
  //   onOk() {
  //     console.log('OK');
  //   },
  //   onCancel() {
  //     console.log('Cancel');
  //   },
  //   class: 'test',
  // });
};

//删除
const delFileId = ref<string>('');
const delFileType = ref<number>(0);
const delRef = ref<any>();
const delData = () => {
  switch (delFileType.value) {
    case 2: delColumns2ById(delFileId.value);
      break;
    case 3: delColumns3ById(delFileId.value);
      break;
    case 4: delColumns4ById(delFileId.value);
      break;
    case 5: delColumns5ById(delFileId.value);
      break;
    case 6: delColumns6ById(delFileId.value);
      break;
    default:
      break;
  }
  delRef.value.close()
}
const openConfirm = (type: number, id: any) => {
  delFileId.value = id;
  delFileType.value = type;
  delRef.value.open();
}

// 基础信息表单
// 数据格式
interface IFormDataBasic {
  id: string;
  companyName: string;// (value = "公司名称")
  registrationStatus: string;// (value = "登记状态")
  creditCode: string;// (value = "统一信用识别码")
  establishDate: string;// (value = "成立日期")
  legalPerson: string;// (value = "法定代表人")
  registeredCapital: string;// (value = "注册资本")
  registeredCurrency: string;// (value = "注册币种")
  paidCapital: string;// (value = "实缴资本")
  paidCurrency: string;// (value = "实缴币种")
  companyCode: string;// (value = "企业编码")
  taxpayerQualification: string;// (value = "纳税人资质")
  taxpayerCode: string;// (value = "纳税人识别号")
  registerNumber: string;// (value = "工商注册号")
  staffSize: string;// (value = "人员规模")
  insuredPersons: number | null;// (value = "参保人数")
  address: string;// (value = "注册地址")
  mailAddress: string;// (value = "通信地址")
  purchaser: boolean;// (value = "是否是采购商 0否 1是")
  supplier: boolean;// (value = "是否是供应商 0否 1是")
  supplierStatus: string;// (value = "供应商注册状态")

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
  id: '',
  companyName: '',           // (value = "公司名称")
  registrationStatus: '',    // (value = "登记状态")
  creditCode: '',            // (value = "统一信用识别码")
  establishDate: '',         // (value = "成立日期")
  legalPerson: '',           // (value = "法定代表人")
  registeredCapital: '',   // (value = "注册资本")
  registeredCurrency: '人民币',    // (value = "注册币种")
  paidCapital: '',         // (value = "实缴资本")
  paidCurrency: '人民币',          // (value = "实缴币种")
  companyCode: '',           // (value = "企业编码")
  taxpayerQualification: '', // (value = "纳税人资质")
  taxpayerCode: '',          // (value = "纳税人识别号")
  registerNumber: '',        // (value = "工商注册号")
  staffSize: '',             // (value = "人员规模")
  insuredPersons: null,      // (value = "参保人数")
  address: '',               // (value = "注册地址")
  mailAddress: '',           // (value = "通讯地址")
  purchaser: false,          // (value = "是否是采购商 0否 1是")
  supplier: true,            // (value = "是否是供应商 0否 1是")
  supplierStatus: '',        // (value = "供应商注册状态")

});
const formRefBasic = ref();
const formRulesBasic = {
  companyName: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  registrationStatus: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  creditCode: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  establishDate: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  legalPerson: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  registeredCapital: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  paidCapital: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  registeredCurrency: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  paidCurrency: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  companyCode: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  taxpayerQualification: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  taxpayerCode: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  registerNumber: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  staffSize: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  insuredPersons: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  address: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
  mailAddress: [{ required: true, message: i18n.global.t('placeholder.pleaseEnter'), trigger: "blur" }],
};
const saveBasicInfo = async () => {
  await formRefBasic.value
    .validate()
    .then(() => {
      companyApi.editCompany(formDataBasic).then((res: any) => {
        if (res.success) {
          message.success('保存成功');
        }
      })
    })
    .catch((err: any) => {
      console.log(err);
    });
};

const getCompanyId = () => {
  let userData = JSON.parse(localStorage.getItem("userInfo") as string);
  let companyId = '';
  if (userData != null) companyId = userData.companyId;
  return companyId;
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
  {
    title: '操作',
    dataIndex: 'operate',
    key: 'operate',
    align: 'center',
    width: 120,
  },
];
// 新增、编辑经营范围
const columns2DialogVisible = ref<boolean>(false);
const columns2DialogType = ref<string>('edit');
const columns2Data = ref<any>();
// 新增、编辑经营范围 打开弹窗以及赋初值
const addEditColumns2Open = (type: string, data?: any) => {
  columns2DialogType.value = type;
  if (type == 'edit') {
    columns2Data.value = JSON.parse(JSON.stringify(data))
  } else {
    columns2Data.value = {
      companyId: getCompanyId(),
      name: '',
    }
  }
  columns2DialogVisible.value = true;
}// 编辑企业信息弹窗确认数据返回
const addEditColumns2Execute = (type: string, data: any) => {
  if (type == 'edit') {
    supplyBusinessScopeApi.editSupplyBusinessScope(data).then((res: any) => {
      if (res.success) {
        columns2DialogVisible.value = false;
        getColumns2();
      }
    });
  } else {
    supplyBusinessScopeApi.postSupplyBusinessScope(data).then((res: any) => {
      if (res.success) {
        columns2DialogVisible.value = false;
        getColumns2();
      }
    });
  }
}
const delColumns2ById = (id: string) => {
  supplyBusinessScopeApi.delSupplyBusinessScope(id).then((res: any) => {
    if (res.success) {
      getColumns2();
    }
  });
}
const getColumns2 = () => {
  supplyBusinessScopeApi.getSupplyBusinessScope().then((res: any) => {
    if (res.success) {
      dataSource2.value = res.obj
    }
  });
}

// 资质文件
// 资质类型
// 证书编号
// 资质名称
// 发证日期
// 有效期
// 发证机关
// 操作
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
  {
    title: '操作',
    dataIndex: 'operate',
    key: 'operate',
    align: 'center',
    width: 120,
  },
];
// 新增、编辑 资质文件
const columns3DialogVisible = ref<boolean>(false);
const columns3DialogType = ref<string>('edit');
const columns3Data = ref<any>();
// 新增、编辑 资质文件 打开弹窗以及赋初值
const addEditColumns3Open = (type: string, data?: any) => {
  columns3DialogType.value = type;
  if (type == 'edit') {
    columns3Data.value = JSON.parse(JSON.stringify(data))
  } else {
    columns3Data.value = {
      companyId: getCompanyId(),
      qualificationsType: '',// 资质类型
      certificateNo: '',// 证书编号
      qualificationsName: '',// 资质名称
      issuanceDate: '',// 发证日期
      periodValidity: '',// 有效期
      licenceIssuingAuthority: '',// 发证机关
    }
  }
  columns3DialogVisible.value = true;
}
// 编辑 资质文件 弹窗确认数据返回
const addEditColumns3Execute = (type: string, data: any) => {
  if (type == 'edit') {
    supplyQualificationDocumentsApi.editSupplyQualificationDocuments(data).then((res: any) => {
      if (res.success) {
        columns3DialogVisible.value = false;
        getColumns3();
      }
    });
  } else {
    supplyQualificationDocumentsApi.postSupplyQualificationDocuments(data).then((res: any) => {
      if (res.success) {
        columns3DialogVisible.value = false;
        getColumns3();
      }
    });
  }
}
// 删除 资质文件 弹窗确认数据返回
const delColumns3ById = (id: string) => {
  supplyQualificationDocumentsApi.delSupplyQualificationDocuments(id).then((res: any) => {
    if (res.success) {
      getColumns3();
    }
  });
}
const getColumns3 = () => {
  supplyQualificationDocumentsApi.getSupplyQualificationDocuments().then((res: any) => {
    if (res.success) {
      dataSource3.value = res.obj
    }
  });
}

// 专利技术 
// 发明名称
// 专利类型
// 法律状态
// 申请号
// 申请日期
// 公开(公告)号
// 公开(公告)日期 
// 发明人
// 操作
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
  {
    title: '操作',
    dataIndex: 'operate',
    key: 'operate',
    align: 'center',
    width: 120,
  },
];
// 新增、编辑 专利技术
const columns4DialogVisible = ref<boolean>(false);
const columns4DialogType = ref<string>('edit');
const columns4Data = ref<any>();
// 新增、编辑 专利技术 打开弹窗以及赋初值
const addEditColumns4Open = (type: string, data?: any) => {
  columns4DialogType.value = type;
  if (type == 'edit') {
    columns4Data.value = JSON.parse(JSON.stringify(data))
  } else {
    columns4Data.value = {
      companyId: getCompanyId(),
      inventName: '',// 发明名称
      patentType: '',// 专利类型
      lawStatus: '',// 法律状态
      applyNo: '',// 申请号
      applyDate: '',// 申请日期
      openNo: '',// 公开(公告)号
      openDate: '',// 公开(公告)日期
      inventor: '',// 发明人
    }
  }
  columns4DialogVisible.value = true;
}
// 编辑 专利技术 弹窗确认数据返回
const addEditColumns4Execute = (type: string, data: any) => {
  if (type == 'edit') {
    supplyPatentTechnologyApi.editSupplyPatentTechnology(data).then((res: any) => {
      if (res.success) {
        columns4DialogVisible.value = false;
        getColumns4();
      }
    });
  } else {
    supplyPatentTechnologyApi.postSupplyPatentTechnology(data).then((res: any) => {
      if (res.success) {
        columns4DialogVisible.value = false;
        getColumns4();
      }
    });
  }
}
// 删除 专利技术 弹窗确认数据返回
const delColumns4ById = (id: string) => {
  supplyPatentTechnologyApi.delSupplyPatentTechnology(id).then((res: any) => {
    if (res.success) {
      getColumns4();
    }
  });
}
const getColumns4 = () => {
  supplyPatentTechnologyApi.getSupplyPatentTechnology().then((res: any) => {
    if (res.success) {
      dataSource4.value = res.obj
    }
  });
}

// 社会诚信
// 信用类型
// 评价年度
// 信用等级
// 评价单位
// 发布日期
// 证明材料
// 操作
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
  {
    title: '操作',
    dataIndex: 'operate',
    key: 'operate',
    align: 'center',
    width: 120,
  },
];
// 新增、编辑 社会诚信
const columns5DialogVisible = ref<boolean>(false);
const columns5DialogType = ref<string>('edit');
const columns5Data = ref<any>();
const addEditDSocialRef = ref<any>(null)
// 新增、编辑 社会诚信 打开弹窗以及赋初值
const addEditColumns5Open = (type: string, data?: any) => {
  columns5DialogType.value = type;
  if (type == 'edit') {
    console.log('datjs', data);

    columns5Data.value = JSON.parse(JSON.stringify(data))
  } else {
    columns5Data.value = {
      companyId: getCompanyId(),
      creditType: '',// 信用类型
      evaluationYear: '',// 评价年度
      creditGrade: '',// 信用等级
      evaluationUnit: '',// 评价单位
      releaseDate: '',// 发布日期
      // fileName: '',// 证明材料
      // fileExtension: '',// 证明材料后缀
    }
  }
  columns5DialogVisible.value = true;
}
// 编辑 社会诚信 弹窗确认数据返回
const addEditColumns5Execute = (type: string, data: any) => {
  if (type == 'edit') {
    // supplySocialIntegrityApi.editSupplySocialIntegrity(data).then((res:any) => {
    //   if (res.success) {
    //     columns5DialogVisible.value = false;        
    //   }
    // });    
    const httpData: any = {
      data: {
        companyId: data.companyId + '',
        creditGrade: data.creditGrade,
        creditType: data.creditType,
        evaluationUnit: data.evaluationUnit,
        evaluationYear: data.evaluationYear,
        releaseDate: data.releaseDate
      },
      id: data.id
    }
    supplySocialIntegrityApi.editSupplySocialIntegrity(httpData).then((res: any) => {
      if (res.success) {
        if (res.success) {
          if (!data.file) {
            columns5DialogVisible.value = false;
            message.success('修改成功')
            addEditDSocialRef.value.resetFields()
            getColumns5()
            return
          }
          const formData = new FormData()
          formData.append('file', data.file)
          const fileData: any = {
            id: data.id,
            data: formData
          }
          supplySocialIntegrityApi.setFile(fileData).then((res2: any) => {
            if (res.success) {
              columns5DialogVisible.value = false;
              message.success('修改成功')
              addEditDSocialRef.value.resetFields()
              getColumns5()
            } else {
              message.error('文件上传失败')
            }
          })
        }
      }
    });
  } else {
    const httpData: any = {
      companyId: data.companyId,
      creditGrade: data.creditGrade,
      creditType: data.creditType,
      evaluationUnit: data.evaluationUnit,
      evaluationYear: data.evaluationYear,
      releaseDate: data.releaseDate
    }
    supplySocialIntegrityApi.postSupplySocialIntegrity(httpData).then((res: any) => {
      if (res.success) {
        if (res.success) {
          if (!data.file) {
            columns5DialogVisible.value = false;
            message.success('修改')
            addEditDSocialRef.value.resetFields()
            return
          }
          const goodFaithId = res.obj
          const formData = new FormData()
          formData.append('file', data.file)
          const fileData: any = {
            id: goodFaithId,
            data: formData
          }
          supplySocialIntegrityApi.setFile(fileData).then((res2: any) => {
            if (res.success) {
              columns5DialogVisible.value = false;
              message.success('新增成功')
              addEditDSocialRef.value.resetFields()
              getColumns5()
            } else {
              message.error('文件上传失败')
            }
          })
        }
      }
    });
  }
}
// 删除 社会诚信 弹窗确认数据返回
const delColumns5ById = (id: string) => {
  supplySocialIntegrityApi.delSupplySocialIntegrity(id).then((res: any) => {
    if (res.success) {
      getColumns5()
    }
  });
}
const getColumns5 = () => {
  supplySocialIntegrityApi.getSupplySocialIntegrityList().then((res: any) => {
    if (res.success) {
      dataSource5.value = res.obj
    }
  });
}

// 供应清单
// 可供类目
// 可供物料
// 操作
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
  {
    title: '操作',
    dataIndex: 'operate',
    key: 'operate',
    align: 'center',
    width: 120,
  },
];
// 新增、编辑 供应清单
const columns6DialogVisible = ref<boolean>(false);
const columns6DialogType = ref<string>('edit');
const columns6Data = ref<any>();
// 新增、编辑 供应清单 打开弹窗以及赋初值
const addEditColumns6Open = (type: string, data?: any) => {
  columns6DialogType.value = type;
  if (type == 'edit') {
    columns6Data.value = JSON.parse(JSON.stringify(data))
  } else {
    columns6Data.value = {
      companyId: getCompanyId(),
      supplyType: '',// 可供类目
      supplyMaterial: '',// 可供物料
    }
  }
  columns6DialogVisible.value = true;
}
// 编辑 供应清单 弹窗确认数据返回
const addEditColumns6Execute = (type: string, data: any) => {
  if (type == 'edit') {
    supplyListApi.editSupplyList(data).then((res: any) => {
      if (res.success) {
        columns6DialogVisible.value = false;
        getColumns6();
      }
    });
  } else {
    supplyListApi.postSupplyList(data).then((res: any) => {
      if (res.success) {
        columns6DialogVisible.value = false;
        getColumns6();
      }
    });
  }
}
// 删除 供应清单 弹窗确认数据返回
const delColumns6ById = (id: string) => {
  supplyListApi.delSupplyList(id).then((res: any) => {
    if (res.success) {
      getColumns6();
    }
  });
}
const getColumns6 = () => {
  supplyListApi.getSupplyList().then((res: any) => {
    if (res.success) {
      dataSource6.value = res.obj
    }
  });
}

// 履约评价
// 合同编号
// 项目名称
// 含税总金额(元)
// 履约情况
// 质量评价
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
  companyApi.getSupplierCompanyInfo(getCompanyId()).then((res: any) => {
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
const getUserInfo = () => {
  let userData = JSON.parse(localStorage.getItem("userInfo") as string);
  if (userData != null) {
    userInfo.value = userData;
    isLogin.value = true;
  } else {
    isLogin.value = false;
  }
}

// 检测是否提交审核，默认自动通过认证
const passAuth = () => {
  if (userInfo.value.supplierStatus == '2') {
    // submitAudit('3');
    userApi({}).getUserInfo().then((res: any) => {
      if (res.success) {
        localStorage.setItem("userInfo", JSON.stringify(res.obj));
        userInfo.value = res.obj;
      }
    })
  }
}

onMounted(() => {
  getUserInfo();
  initSupplierInfo();
  initFilterCompanyList()
});
</script>

<style lang="less" scoped>
@import 'index.less';
</style>
