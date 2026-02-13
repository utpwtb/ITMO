'use strict';

const { createRouter, createWebHashHistory } = VueRouter;

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            component: LoginPage
        },
        {
            path: '/register',
            component: RegisterPage
        },
        {
            path: '/main',
            component: MainPage
        }
    ]
});
