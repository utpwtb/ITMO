'use strict';

const LoginPage = {
    template: `
        <div class="container login-container">
            <header>
                <h1>Веб‑лабораторная работа #4</h1>
                <p>Студент: Чэнь Хаолинь &#160; Группа: P3216 &#160; Вариант: 32165</p>
            </header>
            
            <div class="login-form">
                <h2>Авторизация</h2>
                <div v-if="error" class="error-message">{{ error }}</div>
                
                <form @submit.prevent="login">
                    <div class="form-group">
                        <label for="username">Логин:</label>
                        <input type="text" id="username" v-model="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Пароль:</label>
                        <input type="password" id="password" v-model="password" required>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Войти</button>
                        <button type="button" class="btn btn-secondary" @click="goToRegister">
                            Зарегистрироваться
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `,
    inject: ['store'],
    data() {
        return {
            username: '',
            password: '',
            error: ''
        };
    },
    methods: {
        goToRegister() {
            this.$router.push('/register');
        },
        async login() {
            try {
                const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // 更新状态管理
                    this.store.setAuth(true, data.username);
                    this.$router.push('/main');
                } else {
                    this.error = data.error;
                }
            } catch (error) {
                console.error('Login error:', error);
                this.error = 'Ошибка при авторизации';
            }
        }
    },
    mounted() {
        // 如果已经登录，跳转到主页面
        if (this.store.state.isLoggedIn) {
            this.$router.push('/main');
        }
    }
};
