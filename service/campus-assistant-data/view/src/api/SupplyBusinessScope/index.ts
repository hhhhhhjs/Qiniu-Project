import { http } from "../request"

export interface ISupplyBusinessScope{
    id?:string;
    companyId: string;
    name: string; // 名称
};

// 供应商-经营范围
// Supply Business Scope Controller
export const supplyBusinessScopeApi = {

    // 供应商-经营范围列表
    getSupplyBusinessScope:()=>http.request({
        url:`supply/businessScope`,
        method:'get',
    }),
    // 供应商-经营范围新增
    postSupplyBusinessScope:(data:ISupplyBusinessScope)=>http.request({
        url:`supply/businessScope`,
        method:'post',
        data:data,
    }),

    // 供应商-经营范围修改
    editSupplyBusinessScope:(data:ISupplyBusinessScope)=>http.request({
        url:`supply/businessScope/${data.id}`,
        method:'put',
        data:data
    }),

    // 供应商-经营范围删除
    delSupplyBusinessScope:(id:string)=>http.request({
        url:`supply/businessScope/${id}`,
        method:'delete',
    }),
};