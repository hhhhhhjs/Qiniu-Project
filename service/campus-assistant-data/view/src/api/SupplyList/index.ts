import { http } from "../request"

export interface ISupplyList{
    id?:string;
    companyId: string;
    supplyType: string;// 可供类目
    supplyMaterial: string;// 可供物料
};

// 供应商-供应清单
// Supply List Controller
export const supplyListApi = {   
    // 供应商-社会诚信列表
    getSupplyList:()=>http.request({
        url:`supply/supplyList`,
        method:'get',
    }),
    
    // 供应商-供应清单新增
    postSupplyList:(data:ISupplyList)=>http.request({
        url:`supply/supplyList`,
        method:'post',
        data:data,
    }),
    
    // 供应商-供应清单修改
    editSupplyList:(data:ISupplyList)=>http.request({
        url:`supply/supplyList/${data.id}`,
        method:'put',
        data:data,
    }),
    
    // 供应商-供应清单删除
    delSupplyList:(id:string)=>http.request({
        url:`supply/supplyList/${id}`,
        method:'delete',
    }),
};