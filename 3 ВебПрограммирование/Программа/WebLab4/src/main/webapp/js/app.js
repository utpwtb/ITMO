'use strict';

const { createApp, reactive } = Vue;

const store = {
    state: reactive({
        isLoggedIn: false,
        username: null,
        points: [],
        lastUpdateTime: 0
    }),
    
    setAuth(isLoggedIn, username) {
        this.state.isLoggedIn = isLoggedIn;
        this.state.username = username;
        localStorage.setItem('auth', JSON.stringify({
            isLoggedIn,
            username,
            timestamp: Date.now()
        }));
    },
    
    setPoints(points) {
        this.state.points.splice(0, this.state.points.length, ...points);
        this.state.lastUpdateTime = Date.now();
        localStorage.setItem('points', JSON.stringify({
            points,
            timestamp: this.state.lastUpdateTime
        }));
    },
    
    getAuth() {
        try {
            const auth = localStorage.getItem('auth');
            return auth ? JSON.parse(auth) : { isLoggedIn: false, username: null };
        } catch (e) {
            return { isLoggedIn: false, username: null };
        }
    },
    
    getPoints() {
        try {
            const points = localStorage.getItem('points');
            return points ? JSON.parse(points).points : [];
        } catch (e) {
            return [];
        }
    },
    
    init() {
        const auth = this.getAuth();
        this.state.isLoggedIn = auth.isLoggedIn;
        this.state.username = auth.username;
        const points = this.getPoints();
        this.state.points.splice(0, this.state.points.length, ...points);
    }
};

store.init();

window.addEventListener('storage', (event) => {
    if (event.key === 'auth') {
        try {
            const auth = JSON.parse(event.newValue);
            store.state.isLoggedIn = auth.isLoggedIn;
            store.state.username = auth.username;
           
            if (auth.isLoggedIn && router.currentRoute.value.path === '/') {
                router.push('/main');
            } else if (!auth.isLoggedIn && router.currentRoute.value.path !== '/') {
                router.push('/');
            }
        } catch (e) {
            console.error('Error parsing auth storage event:', e);
        }
    } else if (event.key === 'points') {
        try {
            const data = JSON.parse(event.newValue);
            if (data.timestamp > store.state.lastUpdateTime) {
                store.state.points.splice(0, store.state.points.length, ...data.points);
                store.state.lastUpdateTime = data.timestamp;
                window.dispatchEvent(new CustomEvent('pointsUpdated'));
            }
        } catch (e) {
            console.error('Error parsing points storage event:', e);
        }
    }
});

// 创建应用
const app = createApp({
    template: `
        <router-view></router-view>
    `,
    provide() {
        return {
            store
        };
    }
});

app.use(router);

app.mount('#app');

setInterval(async () => {
    if (store.state.isLoggedIn) {
        try {
            const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/auth/status', {
                method: 'GET',
                credentials: 'include'
            });
            
            const data = await response.json();
            if (!data.loggedIn) {
                store.setAuth(false, null);
                if (router.currentRoute.value.path !== '/') {
                    router.push('/');
                }
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
        }
    }
}, 500);
