import { http } from "../request"

export interface IReviewExperts{
    companyId: string;//所属企业id
    companyName?: string;//所属单位
    grade: number|null;//等级（排序字段）
    id?: string;//主键id
    idNumber: string;//身份证号
    major: string;//所属专业
    name: string;//真实姓名
    phone: string;//手机号码
    professionalQualifications: string;//职称等级
}

export interface IPages{
    current:number;
    size:number;
    companyId?: string;//所属企业id
    major?: string;//所属专业
    name?: string;//真实姓名
    professionalQualifications?: string;//职称等级
}

// 采购商-专家库
// Review Experts Controller
export const reviewExpertsApi ={
    // 采购商-专家库分页
    getReviewExpertsPage:(data:IPages)=>http.request({
        url:`purchase/reviewExperts`,
        method:'get',
        params:data
    }),
    // 采购商-专家库新增
    postReviewExperts:(data:IReviewExperts)=>http.request({
        url:`purchase/reviewExperts`,
        method:'post',
        data:data,
    }),
    // 采购商-专家库修改
    putReviewExperts:(data:IReviewExperts)=>http.request({
        url:`purchase/reviewExperts/${data.id}`,
        method:'put',
        data:data
    }),
    // 采购商-专家库删除
    delReviewExpertsById:(id:string)=>http.request({
        url:`purchase/reviewExperts/${id}`,
        method:'delete',
        params:{id}
    }),
    // 采购商-专家库列表
    getReviewExpertsList:()=>http.request({
        url:`purchase/reviewExperts/list`,
        method:'get',
    }),
}