'use strict';

const RegisterPage = {
    template: `
        <div class="container login-container">
            <header>
                <h1>Веб‑лабораторная работа #4</h1>
                <p>Студент: Чэнь Хаолинь &#160; Группа: P3216 &#160; Вариант: 32165</p>
            </header>
            
            <div class="login-form">
                <h2>Регистрация</h2>
                <div v-if="error" class="error-message">{{ error }}</div>
                <div v-if="message" class="success-message">{{ message }}</div>
                
                <form @submit.prevent="register">
                    <div class="form-group">
                        <label for="username">Логин:</label>
                        <input type="text" id="username" v-model="username" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="password">Пароль:</label>
                        <input type="password" id="password" v-model="password" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="confirmPassword">Подтвердите пароль:</label>
                        <input type="password" id="confirmPassword" v-model="confirmPassword" required>
                    </div>
                    
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Зарегистрироваться</button>
                        <button type="button" class="btn btn-secondary" @click="goToLogin">
                            Вернуться к входу
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `,
    data() {
        return {
            username: '',
            password: '',
            confirmPassword: '',
            error: '',
            message: ''
        };
    },
    methods: {
        goToLogin() {
            this.$router.push('/');
        },
        async register() {
            if (this.password !== this.confirmPassword) {
                this.error = 'Пароли не совпадают';
                this.message = '';
                return;
            }
            
            try {
                const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/auth/register', {
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
                    this.message = 'Регистрация успешна!';
                    this.error = '';
                    setTimeout(() => {
                        this.$router.push('/');
                    }, 500);
                } else {
                    this.error = data.error;
                    this.message = '';
                }
            } catch (error) {
                console.error('Registration error:', error);
                this.error = 'Ошибка при регистрации';
                this.message = '';
            }
        }
    }
};
