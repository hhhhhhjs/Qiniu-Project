import { defineConfig, loadEnv } from 'vite'
import Components from 'unplugin-vue-components/vite';
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers';
import vue from '@vitejs/plugin-vue'
import { resolve } from "path";
const pathResolve = (dir) => resolve(__dirname, dir);
export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd());
    return {
        base: "./", 
        resolve: {
            alias: {
                "@": pathResolve("./src"), // 新增
                'vue-i18n': 'vue-i18n/dist/vue-i18n.cjs.js',
            },
        },
        build: {
            chunkSizeWarningLimit: 1500,
            outDir: "../server/src/main/resources/public",
            emptyOutDir: true,
            rollupOptions: {
                output: {
                    manualChunks(id) {
                        if (id.includes('node_modules')) {
                            return id.toString().split('node_modules/')[1].split('/')[0].toString();
                        }
                    }
                }
            }
        },

        server: {
            cors: true,
            host: '0.0.0.0',
            proxy: {
                "/organization": {
                    target: 'http://127.0.0.1/zjimee-pbm/',
                    secure: false,
                    ws: false,
                    changeOrigin: true,
                    // rewrite: (path) => path.replace(/^\/api/, ""),
                }
            }
        },
        plugins: [
            vue(),
            Components({
                resolvers: [AntDesignVueResolver({ importStyle: 'less' })],
            }),
        ],
        css: {
            preprocessorOptions: {
                less: {
                    modifyVars: {
                        "primary-color": "#2454ca",
                        "theme-color": "#2454ca",
                        "success-color": "#0AC011",
                        "warning-color": "#F99D1F",
                        "error-color": "#EE3B2B",
                        "disabled-color": "#5a6672"
                    },
                    javascriptEnabled: true,
                }
            }
        }
    }
})

