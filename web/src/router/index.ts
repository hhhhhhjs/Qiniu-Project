import { createRouter, createWebHistory } from "vue-router";
import Home from '@/views/home.vue'

const routes = [
    {
        path: '/',
        redirect: '/home'
    },
    {
        path: "/home",
        name: "Home",
        component: Home
    },
    {
        path: '/conversation',
        name: 'Conversation',
        component: () => import('@/views/Conversation.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router