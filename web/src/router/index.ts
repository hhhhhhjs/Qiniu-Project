import { createRouter, createWebHistory } from "vue-router";
import Home from '@/views/home.vue'


const routes = [
    {
        path: "/",
        name: "Home",
        component: Home
    },
    {
        path: "/login",
        name: "Login",
        component: () => import("@/views/user/login.vue")
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router