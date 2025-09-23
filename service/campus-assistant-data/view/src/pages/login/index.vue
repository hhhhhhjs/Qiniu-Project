<template>
    <div class="login-page container">
        <a-config-provider :locale="locale === 'en' ? enUS : zhCN">
        <section class="page-right">
            <div class="company">
                <div class="c_top">
                    <div class="signup_lang">
                        <div class="signup" @click="registerDialogVisible = true;">{{$t('login.signup')}}</div>
                        <div class="and"></div>
                        <!-- <div class="lang" @click="langType = !langType"> -->
                        <div class="lang" @click="changeLang">
                            <span>{{ language }}</span>
                            <img src="../../assets/images/en_zh_lang.svg">
                        </div>
                    </div>
                </div>
                <div class="c_middle">
                    <div class="company_logo"></div>
                    <div class="company_title">
                        <img src="../../assets/images/company_subtitle.svg">
                    </div>
                    <div class="company_subtitle">Future of science and technology</div>
                </div>
                <div class="c_bottom">
                    <span>
                        {{$t('login.ICPnumber')}}：198373971·4012395782398570235482340sdkfaskflasjlasufj
                    </span>
                </div>
            </div>
            <div class="login-box">
                <div class="title">{{$t('login.company')}}</div>
                <a-divider class="divider-line"></a-divider>
                <div class="login_type">
                    <div class="login_btn" :class="loginType ? 'login_btn_active':''" @click="loginType = true">{{$t('login.loginByAccount')}}</div>
                    <div class="login_btn" :class="loginType ? '':'login_btn_active'" @click="loginType = false">{{$t('login.loginByPhone')}}</div>
                </div>
                <a-form ref="formRef" :rules="rules" :model="userInfomation" v-if="loginType">
                    <a-form-item name="phone">
                        <a-input class="input"
                            :placeholder="$t('login.chkPhone')"
                            ref="phoneInput"
                            size="large"
                            @keyup.enter.native="handleKeyEnter('phone')"
                            v-model:value="userInfomation.phone">
                            <template #prefix>
                                <user-outlined />
                            </template>
                        </a-input>
                    </a-form-item>
                    <a-form-item  name="password">
                        <a-input-password class="input"
                            :placeholder="$t('login.chkPwd')"
                            ref="passwordInput"
                            size="large"
                            @keyup.enter.native="handleKeyEnter('password')"
                            v-model:value="userInfomation.password">
                            <template #prefix>
                                <lock-outlined />
                            </template>
                        </a-input-password>
                    </a-form-item>
                    <a-form-item name="code" >    
                        <a-input class="input" style="width: calc(100% - 104px);"
                            :placeholder="$t('login.chkCode')" 
                            ref="codeInput"
                            size="large"                            
                            v-model:value="userInfomation.code"
                            @keyup.enter.native="handleKeyEnter('code')"
                        />
                        <img :src="vericode" id="img" alt="验证码" @click="getCode"/>
                    </a-form-item>
                </a-form>
                <a-form ref="formRefSms" :rules="rules" :model="userLoginSms" v-else>
                    <a-form-item name="phone">
                        <a-input class="input"
                            :placeholder="$t('login.chkPhone')"
                            ref="phoneInput"
                            size="large"
                            @keyup.enter.native="handleKeyEnterSms('phone')"
                            v-model:value="userLoginSms.phone">
                            <template #prefix>
                                <user-outlined />
                            </template>
                        </a-input>
                    </a-form-item>
                    <a-form-item name="code" >    
                        <a-input class="input" style="width: calc(100% - 104px);"
                            :placeholder="$t('login.chkCode')" 
                            ref="codeInput"
                            size="large"                            
                            v-model:value="userLoginSms.code"
                            @keyup.enter.native="handleKeyEnterSms('code')"
                        />
                        <a-button type="primary" style="height: 44px;width: 100px;background-color: #2566BB;" @click="getSmsCode" v-if="!isClickSend">发送验证码</a-button>
                        <a-button type="primary" style="height: 44px;width: 100px;" disabled v-else>{{ codeNum }}秒后重试</a-button>
                    </a-form-item>
                </a-form>
                <div class="password_area">
                    <div class="remember">
                        <!-- <a-radio><span>{{$t('login.rememberPwd')}}</span></a-radio>                         -->
                    </div>
                    <div class="forget">{{$t('login.forgetPwd')}}</div>
                </div>
                <a-button type="primary" class="login-button" @click="onSubmit">{{$t('login.login')}}</a-button>
                <a-divider>{{$t('login.contactUs')}}</a-divider>
                <div class="company_info">
                    <div class="items">
                        <span>{{$t('login.hotLine')}}</span>
                        <span>{{ orgInfo.hotLine }}</span>
                    </div>
                    <div class="items">
                        <span>{{$t('login.email')}}</span>
                        <span>{{ orgInfo.email }}</span>
                    </div>
                    <div class="items">
                        <span>{{$t('login.report')}}</span>
                        <span>{{ orgInfo.report }}</span>
                    </div>
                    <div class="items">
                        <span>{{$t('login.address')}}</span>
                        <span>{{ orgInfo.address }}</span>
                    </div>
                </div>
                <div class="help">
                    <question-circle-outlined />
                    <span>{{$t('login.helpCenter')}}</span>
                </div>
            </div>
        </section>
        <RegisterDialog :visible="registerDialogVisible"
            @handle-ok="registerAccount" @handle-cancel="registerDialogVisible = false"></RegisterDialog>

        </a-config-provider>
    </div>
</template>
  
<script setup lang="ts">
import {
  QuestionCircleOutlined,
  UserOutlined,
  LockOutlined
} from '@ant-design/icons-vue';
import { onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { userApi } from '../../api/user';
import { contactUsApi } from '../../api/contactUs';
import RegisterDialog from "@/components/register/registerDialog.vue";
import i18n from '../../i18n';
import enUS from 'ant-design-vue/es/locale/en_US';
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import { storeToRefs } from 'pinia';
import { useDataStore } from '../../store/userStatus';
const store = useDataStore();
const { userInfo, isLogin }  = storeToRefs(store);

const registerDialogVisible = ref<boolean>(false)
const registerAccount = (data:any) => {
    userApi(data).postUserRegister().then((res:any) => {
        if (res.success) {
            registerDialogVisible.value = false;
            localStorage.setItem("token", res.obj);
            localStorage.setItem('time', Date.now() + '')
            
            userApi({}).getUserInfo().then((res:any) => {
                if (res.success) {
                    localStorage.setItem("userInfo", JSON.stringify(res.obj));
                    userInfo.value = res.obj;
                    isLogin.value = true;
                    $router.push({ name: "mainPage" });
                }else{
                    getCode();
                }
            });
        }        
    })
}

dayjs.locale('en');
const locale = ref(enUS.locale);
const langType = ref<boolean>(false)
// 切换英文 切换中文
const language = ref<string>(
    localStorage.getItem('lang') == 'en' ? 'EN' : 'ZH' || 'ZH'
)
const changeLang = () => {
    langType.value = !langType.value;
    if (langType.value) {
        language.value = 'EN';
        locale.value = enUS.locale;
        dayjs.locale('en');
        localStorage.setItem('lang', 'en')
        i18n.global.locale = 'en'
        // location.reload();
    } else {
        language.value = 'ZH';
        locale.value = zhCN.locale
        localStorage.setItem('lang', 'zh')
        i18n.global.locale = 'zh';
        dayjs.locale('zh');
    }    
}

const loginType = ref<boolean>(true)
const formRef = ref();
const formRefSms = ref();
const phoneInput = ref();
const passwordInput = ref();
const codeInput = ref();
interface IUserForm {
    phone: string; //用户名
    password?: string | number; //验证码
    code: string | number; //密码
}
const userInfomation = reactive<IUserForm>({
    // phone: "15824111676",
    // password: "admin",
    phone: "",
    password: "",
    code: "",
});
const userLoginSms = reactive<IUserForm>({
    // phone: "15824111676",
    phone: "",
    code: "",
});
const companyInfo = ref<any>([
    {label:'热线',value:'0571-88888888'},
    {label:'邮箱',value:'jdjtzczx@163.com'},
    {label:'举报',value:'jdjtJbzx@163.com'},
    {label:'地址',value:'浙江省杭州市滨江区庙后王路125号'},
]);

interface IOrgInfo {
    address: string;
    email: string;
    hotLine: string;
    report: string;
};
const orgInfo = reactive<IOrgInfo>({
    address:'',
    email:'',
    hotLine:'',
    report:'',
});

const vericode = ref();

const getCode = () => {
    userApi({}).getPictureCode().then((res:any) => {        
        vericode.value = window.URL.createObjectURL(new Blob([res], { type: 'image/png' }))
    })
    // vericode.value = `http://www.tangguangdi.com/zjimee-pbm/organization/user/pictureCode?${new Date().getTime()}`;
};


// 定时器id
const clearId = ref<any>();
// 是否发送了验证码 防止连点
const isClickSend = ref<boolean>(false);
// 倒计时时间
const codeNum = ref<number>(60);
// 发送验证码
const getSmsCode = async () => {
    if (userLoginSms.phone == "") {
        phoneInput.value.focus();
        return;
    } 
    if (isClickSend.value || codeNum.value != 60) return;
    isClickSend.value = true;
    const res = await userApi({phone:userLoginSms.phone}).getSmsCode().then()
    clearId.value = setInterval(() => {
        codeNum.value--;
        if (codeNum.value == 0) {
            clearInterval(clearId.value);
            codeNum.value = 60;
            isClickSend.value = false;
        }
    }, 1000);
    // console.log("sendCode", res);
};
const getCompanyInfo = () => {
    contactUsApi({}).getCompanyInfo().then((res:any) => {
        orgInfo.address = res.obj.address
        orgInfo.email = res.obj.email
        orgInfo.hotLine = res.obj.hotLine
        orgInfo.report = res.obj.report
    })
};

const handleKeyEnter = (input: string): void => {
  switch (input) {
    case "phone":
      passwordInput.value.focus();
      break;
    case "password":
      codeInput.value.focus();
      break;
    case "code":
      onSubmit;
      break;
    default:
      phoneInput.value.focus();
      break;
  }
};
const handleKeyEnterSms = (input: string): void => {
  switch (input) {
    case "phone":
      codeInput.value.focus();
      break;
    case "code":
      onSubmit;
      break;
    default:
      phoneInput.value.focus();
      break;
  }
};

const onSubmit = async () => {
    if (loginType.value) {
        await formRef.value
          .validate()
          .then(() => {
              let data = {
                  phone:userInfomation.phone,
                  password:userInfomation.password,
                  code:userInfomation.code,
              }
              userApi(data).login().then((res:any) => {
                  if (res.success) {
                      localStorage.setItem("token", res.obj);
                      localStorage.setItem('time', Date.now() + '')
                      
                      userApi({}).getUserInfo().then((res:any) => {
                          if (res.success) {
                              localStorage.setItem("userInfo", JSON.stringify(res.obj));
                              userInfo.value = res.obj;
                              $router.push({ name: "mainPage" });
                          }
                      });
                  }else{
                      getCode()
                  }
              })
      
          })
          .catch((err:any) => {
            console.log(err);
          });
    } else {
        await formRefSms.value
          .validate()
          .then(() => {
              let data = {
                  phone:userLoginSms.phone,
                  code:userLoginSms.code,
              }
              userApi(data).loginBySmsCode().then((res:any) => {
                  if (res.success) {
                      localStorage.setItem("token", res.obj);
                      localStorage.setItem('time', Date.now() + '')
                      
                      userApi({}).getUserInfo().then((res:any) => {
                          if (res.success) {
                              localStorage.setItem("userInfo", JSON.stringify(res.obj));
                              userInfo.value = res.obj;
                              $router.push({ name: "mainPage" });
                          }
                      });
                  }
              })
      
          })
          .catch((err:any) => {
            console.log(err);
          });
    }
};

const $router = useRouter();
const rules = {
    phone: [{ required: true, message: i18n.global.t('login.chkPhone'), trigger: "blur" }],
    password: [{ required: true, message: i18n.global.t('login.chkPwd'), trigger: "blur" }],
    code: [{ required: true, message: i18n.global.t('login.chkCode'), trigger: "blur" }],
};

onMounted(() => {
    // 更新图片验证码
    getCode()
    // 清理定时器
    clearInterval(clearId.value)
    // 获取集团单位信息
    getCompanyInfo()    
})

</script>
  
<style scoped lang="less">
.login-page {
    width: 100%;
    height: 100vh;
    min-width: 1600px;
    min-height: 900px;
    overflow: auto;
    display: flex;
    background-color: rgba(0, 133, 255, 0.08);
    background-image: url('../../assets/images/pbm_bg.png');
    background-size: 100% 100%;
}

.logo {
    margin: 30px;
}

.page-right {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background-color: transparent;
    
    .company{
        width: 100%;
        height: 100%;
        position: relative;
        .c_top{
            width: 100%;
            height: 8.875rem /* 142/16 */;
            display: flex;
            justify-content: flex-end;
            padding: 1.5rem /* 24/16 */ 4rem /* 64/16 */;
            .signup_lang{
                width: 15.625rem /* 170/16 */;
                height: 1.25rem /* 20/16 */;
                display: inline-flex;
                align-items: center;
                gap: 1.0625rem /* 17/16 */;
                .signup{
                    display: flex;
                    width: 6.25rem /* 100/16 */;
                    height: 1.25rem /* 20/16 */;
                    justify-content: center;
                    align-items: center;
                    border-radius: .25rem /* 4/16 */;
                    border: .03125rem /* 0.5/16 */ solid #FFF;
                    background: rgba(255, 255, 255, 0.50);

                    color: #2055A6;
                    font-family: PingFang SC;
                    font-size: .875rem /* 14/16 */;
                    font-style: normal;
                    font-weight: 500;
                    line-height: normal;
                }
                .and{
                    height: .5rem /* 8/16 */;
                    width: .0625rem /* 1/16 */;
                    border: .0625rem /* 1/16 */ solid #C9CDD4;
                    stroke: var(--unnamed, );
                }
                .lang{
                    display: flex;
                    padding: 0px 8px;
                    align-items: center;
                    gap: 4px;
                    border-radius: 4px;
                    border: 0.5px solid #FFF;
                    background: rgba(255, 255, 255, 0.50);

                    span{
                        color: var(--unnamed, #4E5969);
                        text-align: center;
                        font-family: PingFang SC;
                        font-size: .875rem /* 14/16 */;
                        font-style: normal;
                        font-weight: 400;
                        line-height: normal;
                    }
                }
                .signup:hover{
                    cursor: pointer;
                }
                .lang:hover{
                    cursor: pointer;
                }
            }
        }
        .c_middle{
            width: 100%;
            height: 19.375rem /* 310/16 */;
            background: rgba(122, 191, 255, 0.20);
            backdrop-filter: blur(4px);
            padding: 2.5625rem /* 41/16 */ 4.4375rem /* 71/16 */;
            .company_logo{
                width: 100%;
                height: 3.125rem /* 50/16 */;
                background-image: url('../../assets/images/pbm_logo.png');
                background-size: contain;
                background-repeat: no-repeat;
            }
            .company_title{
                width: 100%;
                margin-top: 2rem /* 32/16 */;
                margin-bottom: 1.5rem /* 24/16 */;
                // background-image: url('../../assets/images/company_subtitle.svg');
            }
            .company_subtitle{
                width: 100%;
                color: var(--unnamed, #FFF);
                text-shadow: 0px .25rem /* 4/16 */ .25rem /* 4/16 */ 0px rgba(0, 0, 0, 0.25);
                font-family: PingFang SC;
                font-size: 1.25rem /* 20/16 */;
                font-style: normal;
                font-weight: 600;
                line-height: normal;
                letter-spacing: .59375rem /* 9.5/16 */;
            }
        }
        .c_bottom{
            width: 100%;
            position: absolute;
            display: flex;
            justify-content: flex-end;
            bottom: 0;
            padding-bottom: .5rem /* 8/16 */;
            
            span{
                width: 34.375%;
                margin-right: 3.8125rem /* 61/16 */;

                color: var(--unnamed, #86909C);
                text-align: center;
                font-family: PingFang SC;
                font-size: .75rem /* 12/16 */;
                font-style: normal;
                font-weight: 400;
                line-height: 1.25rem /* 20/16 */;
            }
        }
    }
}

.login-box {
    width: 35%;
    height: 85%;
    // width: 41.25rem /* 660/16 */;
    // height: 56.875rem /* 910/16 */;

    position: absolute;
    padding: 4% /* 80/16 */ 5% /* 102/16 */ 1.5% /* 30/16 */ 5% /* 102/16 */;
    top: 9%;
    right: 3.8125rem /* 61/16 */;
    border-radius: .5rem /* 8/16 */;

    background: rgba(255, 255, 255, 0.82);
    box-shadow: 0px 10px 12px 0px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(23px);
    
    .title {
        width: 100%;
        color: #2055A6;
        text-align: center;
        // font-family: MF FangHei (Noncommercial);
        font-size: 2.5rem /* 37/16 */;
        font-style: normal;
        font-weight: bolder;
        line-height: 3rem /* 48/16 */;
        letter-spacing: .25rem /* 4/16 */;
    }
    
    .divider-line {
        margin-top: 1.5625rem /* 25/16 */;
        background: #F1F2F4;
    }
    .login_type{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .5rem /* 8/16 */;
        width: 100%;
        padding: .25rem /* 4/16 */;
        height: 2.75rem /* 44/16 */;
        justify-content: center;
        align-items: center;

        border-radius: 8px;
        border: 1px solid var(--unnamed, #F7F8F9);
        background: var(--unnamed, #F1F2F4);
        margin-top: 2rem /* 32/16 */;
        margin-bottom: 2.5rem /* 40/16 */;
        .login_btn{
            display: flex;
            padding: .5rem /* 8/16 */;
            justify-content: center;
            align-items: center;
            border-radius: .5rem /* 8/16 */;

            color: var(--unnamed, #4E5969);
            text-align: center;
            font-family: PingFang SC;
            font-size: .875rem /* 14/16 */;
            font-style: normal;
            font-weight: 400;
            // line-height: normal;
        }
        .login_btn:hover{
            cursor: pointer;
        }
        .login_btn_active{
            background: #FFF;
        }
    }

    .password_area{
        width: 100%;
        display: flex;
        justify-content: space-between;

        .remember{
            width: 50%;
            span{
                color: var(--unnamed, #4E5969);
                font-family: PingFang SC;
                font-size: 14px;
                font-style: normal;
                font-weight: 400;
                line-height: 22px; 
            }
        }
        .forget{
            cursor: pointer;
            width: 40%;
            display: flex;
            justify-content: flex-end;
            color: var(--unnamed, #4E5969);
            font-family: PingFang SC;
            font-size: 14px;
            font-style: normal;
            font-weight: 400;
            line-height: 22px;            
        }
    }

    .company_info{
        width: 100%;
        display: flex;
        flex-direction: column;
        gap: .5rem /* 8/16 */;
        .items{
            width: 100%;
            height: 1.25rem /* 20/16 */;
            display: flex;
            justify-content: space-between;
            align-items: center;
            align-self: stretch;

            span{
                color: var(--unnamed, #4E5969);
                text-align: center;
                font-family: PingFang SC;
                font-size: .875rem /* 14/16 */;
                font-style: normal;
                font-weight: 400;
                line-height: 1.25rem /* 20/16 */;
            }
        }
    }
    .help{
        width: 100%;
        height: .875rem /* 14/16 */;
        display: flex;
        justify-content: center;
        align-items: center;
        position: absolute;
        bottom: 1.875rem /* 30/16 */;
        left: 0;
        gap: .5rem /* 8/16 */;

        span{
            color: var(--unnamed, #86909C);
            font-family: PingFang SC;
            font-size: .875rem /* 14/16 */;
            font-style: normal;
            font-weight: 400;
            line-height: normal;
        }
    }

}

:deep( .ant-form-item-label > label ){
    height: 48px;
}
:deep( .ant-form-item-control-input-content ){
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.input {
    border: 1px solid #c6ccd2;
    border-radius: 8px;
    height: 48px;
}


.login-button {
    width: 100%;
    display: flex;
    height: 2.75rem /* 44/16 */;
    justify-content: center;
    align-items: center;
    flex-shrink: 0;
    // background: var(--theme-color);
    margin-bottom: 4.375rem /* 70/16 */;
    margin-top: 3.5rem /* 56/16 */;
    border-radius: .25rem /* 4/16 */;
    background: #2566BB;

    color: #FFF;
    font-family: PingFang SC;
    font-size: 1.5rem /* 24/16 */;
    font-style: normal;
    font-weight: 400;
    letter-spacing: 1.925px;
}

.forget-password {
    float: right;
    font-size: 16px;
    color: #8d99a5;
    letter-spacing: 1.925px;
}



</style>
  ../../api/user