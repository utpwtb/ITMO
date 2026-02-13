'use strict';

const MainPage = {
    template: `
        <div>
            <div class="header-links">
                <button class="link-button" @click="logout">Выйти</button>
            </div>
            
            <div class="container">
                <header>
                    <h1>Веб‑лабораторная работа #4</h1>
                    <p>Студент: Чэнь Хаолинь &#160; Группа: P3216 &#160; Вариант: 32165</p>
                </header>
                
                <div class="graph-container">
                    <svg
                        id="graph-svg"
                        width="100%"
                        height="500"
                        viewBox="0 0 600 600"
                        preserveAspectRatio="xMidYMid meet"
                        xmlns="http://www.w3.org/2000/svg"
                        style="cursor: pointer;"
                        @click="handleGraphClick">
                        <defs>
                            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                                <polygon points="0 0, 10 3.5, 0 7" fill="#000"/>
                            </marker>
                        </defs>

                        <line x1="50" y1="300" x2="550" y2="300" class="axis" marker-end="url(#arrowhead)"/>
                        <text x="560" y="290" class="axis-label">X</text>
                        <line x1="100" y1="295" x2="100" y2="305" class="axis"/>
                        <text x="95" y="325" class="label">-R</text>
                        <line x1="200" y1="295" x2="200" y2="305" class="axis"/>
                        <text x="195" y="325" class="label">-R/2</text>
                        <line x1="400" y1="295" x2="400" y2="305" class="axis"/>
                        <text x="395" y="325" class="label">R/2</text>
                        <line x1="500" y1="295" x2="500" y2="305" class="axis"/>
                        <text x="495" y="325" class="label">R</text>

                        <line x1="300" y1="550" x2="300" y2="50" class="axis" marker-end="url(#arrowhead)"/>
                        <text x="310" y="40" class="axis-label">Y</text>
                        <line x1="295" y1="100" x2="305" y2="100" class="axis"/>
                        <text x="315" y="105" class="label">R</text>
                        <line x1="295" y1="200" x2="305" y2="200" class="axis"/>
                        <text x="315" y="205" class="label">R/2</text>
                        <line x1="295" y1="400" x2="305" y2="400" class="axis"/>
                        <text x="315" y="405" class="label">-R/2</text>
                        <line x1="295" y1="500" x2="305" y2="500" class="axis"/>
                        <text x="315" y="505" class="label">-R</text>

                        <polygon
                            v-if="showShapes"
                            :points="firstPolygonPoints"
                            class="shape"/>
                        <polygon
                            v-if="showShapes"
                            :points="secondPolygonPoints"
                            class="shape"/>
                        <path
                            v-if="showShapes"
                            :d="pathD"
                            class="shape"/>
                    </svg>
                    <p id="error-graph" style="color: #f41c52">{{ graphError }}</p>
                </div>
                
                <div class="form-container">
                    <h2>Проверка точки</h2>
                    <form @submit.prevent="checkPoint">
                        <div class="form-section select-X">
                            <span class="section-title">Выбор X:</span>
                            <div id="xButtons">
                                <button 
                                    v-for="value in xValues" 
                                    :key="value"
                                    type="button" 
                                    class="x-button"
                                    :class="{ active: x === value }"
                                    @click="selectX(value)">
                                    {{ value }}
                                </button>
                            </div>
                            <p v-if="xError" class="error-message">{{ xError }}</p>
                        </div>

                        <div class="form-section text-Y">
                            <span class="section-title">Введите Y (-3 ... 3):</span>
                            <input 
                                type="text" 
                                class="y-input"
                                v-model="y" 
                                placeholder="Введите значение от -3 до 3"
                            />
                            <p v-if="yError" class="error-message">{{ yError }}</p>
                        </div>

                        <div class="form-section text-R">
                            <span class="section-title">Выбор R:</span>
                            <div id="rLinks">
                                <button 
                                    v-for="value in rValues" 
                                    :key="value"
                                    type="button" 
                                    class="r-link"
                                    :class="{ active: r === value }"
                                    @click="r = value">
                                    {{ value }}
                                </button>
                            </div>
                            <p v-if="rError" class="error-message">{{ rError }}</p>
                        </div>

                        <div class="submit-btn">
                            <button type="submit" class="check-button">Проверить</button>
                            <button type="button" class="reset-button" @click="resetForm">Отменить</button>
                            <button type="button" class="clear-results-button" @click="clearResults">Очистить результаты</button>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="result-container">
                <h2>Результаты проверок</h2>
                <table v-if="store.state.points.length > 0" class="result-table">
                    <thead>
                        <tr>
                            <th>X</th>
                            <th>Y</th>
                            <th>R</th>
                            <th>Попадание</th>
                            <th>Время запроса</th>
                            <th>Время выполнения (мс)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="point in store.state.points" :key="point.id">
                            <td>{{ point.x }}</td>
                            <td>{{ point.y }}</td>
                            <td>{{ point.r }}</td>
                            <td>{{ point.hit ? 'Попал' : 'Промах' }}</td>
                            <td>{{ formatDateTime(point.currentTime) }}</td>
                            <td>{{ point.executionTime }}</td>
                        </tr>
                    </tbody>
                </table>
                <p v-else>Результатов пока нет. Выберите X, введите Y, выберите R и нажмите «Проверить».</p>
            </div>
        </div>
    `,
    inject: ['store'],
    data() {
        return {
            x: null,
            y: '',
            r: null,
            xError: '',
            yError: '',
            rError: '',
            graphError: '',
            xValues: [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2],
            rValues: [-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]
        };
    },
    computed: {
        firstPolygonPoints() {
            if (this.r === null || this.r === 0) return '';
            if (this.r > 0) {
                return `300,300 200,300 300,200`;
            } else {
                return `300,300 400,300 300,400`;
            }
        },
        secondPolygonPoints() {
            if (this.r === null || this.r === 0) return '';
            if (this.r > 0) {
                return `300,300 100,300 100,500 300,500`;
            } else {
                return `300,300 500,300 500,100 300,100`;
            }
        },
        pathD() {
            if (this.r === null || this.r === 0) return '';
            if (this.r > 0) {
                return `M300,300 L500,300 A200,200 0 0,1 300,500 Z`;
            } else {
                return `M 100,300 A 200,200 0 0 1 300,100 L 300,300 Z`;
            }
        },
        showShapes() {
            return this.r !== null && this.r !== 0;
        }
    },
    watch: {
        r() {
            this.redrawAllPoints();
        },
        'store.state.points'() {
            this.redrawAllPoints();
        }
    },
    methods: {
        async checkAuthStatus() {
            try {
                const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/auth/status', {
                    method: 'GET',
                    credentials: 'include'
                });
                
                const data = await response.json();
                if (!data.loggedIn) {
                    this.store.setAuth(false, null);
                    this.$router.push('/');
                } else {
                    this.store.setAuth(true, data.username);
                }
            } catch (error) {
                console.error('Error checking auth status:', error);
                this.store.setAuth(false, null);
                this.$router.push('/');
            }
        },
        async logout() {
            try {
                const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/auth/logout', {
                    method: 'POST',
                    credentials: 'include'
                });
                
                if (response.ok) {
                    this.store.setAuth(false, null);
                    this.$router.push('/');
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        },
        async checkPoint() {
            this.xError = '';
            this.yError = '';
            this.rError = '';
            let hasError = false;
            
            if (this.x === null) {
                this.xError = 'Выберите значение X';
                hasError = true;
            }
            
            const yValue = parseFloat(this.y.replace(',', '.'));
            if (isNaN(yValue) || yValue < -3 || yValue > 3) {
                this.yError = 'Y должно быть числом от -3 до 3';
                hasError = true;
            }
            
            if (this.r === null) {
                this.rError = 'Выберите значение R';
                hasError = true;
            }
            
            if (hasError) {
                return;
            }
            
            try {
                const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/points/check', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({
                        x: this.x,
                        y: yValue,
                        r: this.r
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const newPoint = {
                        ...data
                    };
                    await this.loadPoints();
                } else {
                    this.yError = data.error;
                }
            } catch (error) {
                console.error('Check point error:', error);
                this.yError = 'Ошибка при проверке точки';
            }
        },
        async loadPoints() {
            try {
                const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/points', {
                    method: 'GET',
                    credentials: 'include'
                });
                
                if (response.ok) {
                    const points = await response.json();
                    this.store.setPoints(points);
                    this.redrawAllPoints();
                }
            } catch (error) {
                console.error('Load points error:', error);
            }
        },
        async clearResults() {
            try {
                const response = await fetch('/WebLab4-1.0-SNAPSHOT/api/points', {
                    method: 'DELETE',
                    credentials: 'include'
                });
                
                if (response.ok) {
                    this.store.setPoints([]);
                    this.redrawAllPoints();
                }
            } catch (error) {
                console.error('Clear points error:', error);
            }
        },
        resetForm() {
            this.x = null;
            this.y = '';
            this.r = null;
            this.xError = '';
            this.yError = '';
            this.rError = '';
            this.graphError = '';
        },
        selectX(value) {
            this.x = value;
        },
        handleGraphClick(event) {
            if (this.r === null) {
                this.graphError = 'Выберите значение R перед кликом по графику';
                return;
            }
            
            const svg = document.getElementById('graph-svg');
            const rect = svg.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            
            const viewBoxWidth = 600;
            const viewBoxHeight = 600;
            const actualWidth = rect.width;
            const actualHeight = rect.height;
            
            const scaleX = viewBoxWidth / actualWidth;
            const scaleY = viewBoxHeight / actualHeight;
            
            const scaledX = x * scaleX;
            const scaledY = y * scaleY;
            
            const planeCoords = this.transformSvgToPlane(scaledX, scaledY, this.r);
            const svgX = planeCoords.x;
            const svgY = planeCoords.y;
            
            if (svgX < -2 || svgX > 2 || svgY < -3 || svgY > 3) {
                this.graphError = 'Точка вне допустимого диапазона';
                return;
            }
            
            this.x = svgX;
            this.y = svgY.toString();
            this.checkPoint();
        },
        formatDateTime(dateTimeString) {
            const date = new Date(dateTimeString);
            return date.toLocaleString('ru-RU');
        },
        drawPoint(x, y, r, result) {
            const svg = document.getElementById('graph-svg');
            if (!svg) return;

            const cx = x * 200 / r + 300;
            const cy = -y * 200 / r + 300;
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", cx);
            circle.setAttribute("cy", cy);
            circle.setAttribute("r", 5);
            circle.style.fill = result ? "#09a53d" : "#a50909";
            circle.style.stroke = "#000";
            circle.style.strokeWidth = "1";
            svg.appendChild(circle);
        },
        transformSvgToPlane(svgX, svgY, r) {
            return {
                x: (svgX - 300) * r / 200,
                y: (300 - svgY) * r / 200
            };
        },
        redrawAllPoints() {
            const svg = document.getElementById('graph-svg');
            if (!svg) return;

            svg.querySelectorAll('circle').forEach(circle => {
                if (circle.getAttribute('r') === '5') circle.remove();
            });

            this.store.state.points.forEach(point => {
                if (this.r !== null && Math.abs(point.r - this.r) < 1e-6) {
                    this.drawPoint(point.x, point.y, point.r, point.hit);
                }
            });
        }
    },
    mounted() {
        this.r = 1;
        this.checkAuthStatus();
        this.loadPoints();
        
        window.addEventListener('pointsUpdated', () => {
            this.redrawAllPoints();
        });
    }
};
