import { http } from "../request"
import type { Dayjs } from 'dayjs';

export interface ISupplyQualificationDocuments{
    id?:string;
    companyId: string;
    qualificationsType: string;// 资质类型
    certificateNo: string;// 证书编号
    qualificationsName: string;// 资质名称
    issuanceDate: Dayjs;// 发证日期
    periodValidity: Dayjs;// 有效期
    licenceIssuingAuthority: string;// 发证机关
};

// 供应商-资质文件
// Supply Qualification Documents Controller
export const supplyQualificationDocumentsApi = {
    // 供应商-资质文件列表
    getSupplyQualificationDocuments:()=>http.request({
        url:`supply/qualificationDocuments`,
        method:'get',
    }),
    // 供应商-资质文件新增
    postSupplyQualificationDocuments:(data:ISupplyQualificationDocuments)=>http.request({
        url:`supply/qualificationDocuments`,
        method:'post',
        data:data,
    }),

    // 供应商-资质文件修改
    editSupplyQualificationDocuments:(data:ISupplyQualificationDocuments)=>http.request({
        url:`supply/qualificationDocuments/${data.id}`,
        method:'put',
        data:data
    }),
    
    // 供应商-资质文件删除
    delSupplyQualificationDocuments:(id:string)=>http.request({
        url:`supply/qualificationDocuments/${id}`,
        method:'delete',
    }),
};