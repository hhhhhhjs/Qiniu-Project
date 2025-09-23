/*
 * @Author: zlh
 * @Date: 2022-07-01 15:23:03
 * @LastEditTime: 2022-07-01 15:23:03
 * @LastEditors: zlh
 * @Description: 文件保存
 * @FilePath: \view\src\utils\fileDownload.ts
 */
/**
 * @name:
 * @description:
 * @param {*}
 * @return {*}
 */
import {AxiosResponse} from "axios";

export const fileSave = (res: AxiosResponse<Blob>) => {
  const elink = document.createElement("a");
  const temp = res.headers["content-disposition"].split(";")[1].split("=")[1];
  const fileName = decodeURIComponent(temp);
  elink.download = fileName
  elink.style.display = "none";
  elink.href = URL.createObjectURL(res.data);
  document.body.appendChild(elink);
  elink.click();
  document.body.removeChild(elink);
};
