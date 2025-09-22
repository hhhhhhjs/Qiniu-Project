// upload.js
const qiniu = require("qiniu");
const glob = require("glob");
const path = require("path");
const fs = require("fs");
const crypto = require('crypto');

// 从环境变量读取（在 GitHub Actions 里通过 secrets 注入）
const accessKey = process.env.QINIU_ACCESS_KEY;
const secretKey = process.env.QINIU_SECRET_KEY;
const bucket = process.env.QINIU_BUCKET;
const zone = process.env.QINIU_ZONE || "z0"; // 默认华东，可配置 z0/z1/z2/na0

if (!accessKey || !secretKey || !bucket) {
  console.error("❌ 请检查 QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET 是否配置正确");
  process.exit(1);
}

// 配置七牛云区域
let zoneConfig;
switch (zone) {
  case "z0":
    zoneConfig = qiniu.zone.Zone_z0; // 华东
    break;
  case "z1":
    zoneConfig = qiniu.zone.Zone_z1; // 华北
    break;
  case "z2":
    zoneConfig = qiniu.zone.Zone_z2; // 华南
    break;
  case "na0":
    zoneConfig = qiniu.zone.Zone_na0; // 北美
    break;
  default:
    zoneConfig = qiniu.zone.Zone_z0;
}

const mac = new qiniu.auth.digest.Mac(accessKey, secretKey);
const config = new qiniu.conf.Config();
config.zone = zoneConfig;

const formUploader = new qiniu.form_up.FormUploader(config);
const putExtra = new qiniu.form_up.PutExtra();

// 上传单个文件
function uploadFile(localFile, key) {
  return new Promise((resolve, reject) => {
    const options = { scope: bucket + ":" + key };
    const putPolicy = new qiniu.rs.PutPolicy(options);
    const uploadToken = putPolicy.uploadToken(mac);

    formUploader.putFile(uploadToken, key, localFile, putExtra, function (
      respErr,
      respBody,
      respInfo
    ) {
      if (respErr) {
        reject(respErr);
      } else {
        if (respInfo.statusCode == 200) {
          console.log("✅ 上传成功:", key);
          resolve(respBody);
        } else {
          reject(respBody);
        }
      }
    });
  });
}

// 生成文件哈希作为版本号
function getFileHash(filePath) {
  const fileBuffer = fs.readFileSync(filePath);
  return crypto.createHash('md5').update(fileBuffer).digest('hex').substring(0, 8);
}

// 遍历 dist 下的所有文件并上传
async function main() {
  const files = glob.sync("dist/**/*", { nodir: true });
  console.log(`开始上传 ${files.length} 个文件...`);

  for (const file of files) {
    const key = path.relative("dist", file).replace(/\\/g, "/"); // 兼容 Windows 路径
    try {
      await uploadFile(file, key);
    } catch (err) {
      console.error("❌ 上传失败:", file, err);
    }
  }

  console.log("🎉 全部文件上传完成！");
  //   for (const file of files) {
  //   let key = path.relative("dist", file).replace(/\\/g, "/");
    
  //   // 为关键文件添加版本号
  //   if (file.endsWith('.js') || file.endsWith('.css') || file.endsWith('.html')) {
  //     const hash = getFileHash(file);
  //     const ext = path.extname(key);
  //     const name = path.basename(key, ext);
  //     const dir = path.dirname(key);
  //     key = dir === '.' ? `${name}.${hash}${ext}` : `${dir}/${name}.${hash}${ext}`;
  //   }
    
  //   try {
  //     await uploadFile(file, key);
  //   } catch (err) {
  //     console.error("❌ 上传失败:", file, err);
  //   }
  // }
  // console.log("🎉 全部文件上传完成！");
}

main();
