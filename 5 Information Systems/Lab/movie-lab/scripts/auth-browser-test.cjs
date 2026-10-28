/* Disposable accounts use a unique test prefix. No passwords are written to evidence. */
const {chromium, request} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs = require('node:fs');
const path = require('node:path');
const base = process.env.MOVIE_BASE_URL || 'http://127.0.0.1:18084/movie-lab/';
const out = process.env.MOVIE_TEST_OUTPUT || path.resolve(__dirname, '../../deployment/verification/auth-2026-10-02');
const password = 'Disposable test password 2026!';
const results = [];
fs.mkdirSync(out, {recursive:true});
function check(name, value) {
    results.push({name, passed:!!value});
    if (!value) throw Error(name);
    console.log('PASS ' + name);
}
(async () => {
    let browser, client;
    const evidencePath = path.join(out, 'auth-browser-results.json');
    const username = process.env.AUTH_RESTART_CHECK ? JSON.parse(fs.readFileSync(evidencePath, 'utf8')).username
        : 'authcheck_' + Date.now();
    try {
        if (process.env.AUTH_RESTART_CHECK) {
            client = await request.newContext({baseURL:base});
            const response = await client.post('api/auth', {data:{username,password}});
            check('Registered account can log in after Payara restart', response.status() === 200 && (await response.json()).user === username);
            check('Persisted account can read protected collection', (await client.get('api/movies')).status() === 200);
            return;
        }
        browser = await chromium.launch({executablePath:process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', headless:true});
        const context = await browser.newContext({viewport:{width:852,height:884}});
        const page = await context.newPage();
        const errors = [];
        page.on('pageerror', e => errors.push(e.message));
        await page.goto(base);
        check('Login page offers registration', await page.getByRole('button', {name:'Зарегистрироваться',exact:true}).isVisible());
        check('Removed login explanation is absent', !(await page.locator('#login').innerText()).includes('Все авторизованные пользователи'));
        check('Footer contains only the requested title', (await page.locator('footer').innerText()) === 'Лабораторная работа № 1');
        await page.screenshot({path:path.join(out,'login.png'),fullPage:true});
        await page.locator('#show-register').click();
        const form = page.locator('#register-form');
        await form.locator('[name=username]').fill(username);
        await form.locator('[name=password]').fill(password);
        await form.locator('[name=confirmation]').fill(password + 'x');
        await form.getByRole('button',{name:'Создать аккаунт',exact:true}).click();
        await page.locator('#register-error').getByText('Пароли не совпадают',{exact:true}).waitFor();
        check('Password confirmation mismatch is explained', await form.isVisible());
        await form.locator('[name=confirmation]').fill(password);
        await page.screenshot({path:path.join(out,'registration.png'),fullPage:true});
        const created = page.waitForResponse(r => r.url().endsWith('/api/auth/register') && r.request().method() === 'POST');
        await form.getByRole('button',{name:'Создать аккаунт',exact:true}).click();
        const response = await created;
        const session = await response.json();
        check('Registration creates account and session', response.status() === 201 && session.user === username && !!session.csrf);
        check('Auth response exposes no password material', Object.keys(session).sort().join(',') === 'authenticated,csrf,user');
        await page.locator('#workspace').waitFor({state:'visible'});
        check('New account opens the collection immediately', (await page.locator('#session').innerText()).includes(username));
        await page.locator('#session button').click();
        await page.locator('#login-form').waitFor({state:'visible'});
        await page.locator('#show-register').click();
        await form.locator('[name=username]').fill(username);
        await form.locator('[name=password]').fill(password);
        await form.locator('[name=confirmation]').fill(password);
        await form.getByRole('button',{name:'Создать аккаунт',exact:true}).click();
        await page.locator('#register-error').getByText('Это имя пользователя уже занято',{exact:true}).waitFor();
        check('Duplicate username is explained in registration form', await form.isVisible());
        await page.locator('#show-login').click();
        await page.locator('#login-form [name=username]').fill(username);
        await page.locator('#login-form [name=password]').fill(password);
        await page.getByRole('button',{name:'Войти',exact:true}).click();
        await page.locator('#workspace').waitFor({state:'visible'});
        check('Registered account can log out and log in again', true);
        await context.close();
        const mobile = await browser.newContext({viewport:{width:390,height:844}});
        const mobilePage = await mobile.newPage();
        await mobilePage.goto(base);
        await mobilePage.locator('#show-register').click();
        check('Registration form fits narrow screens', await mobilePage.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
        await mobilePage.screenshot({path:path.join(out,'registration-mobile.png'),fullPage:true});
        await mobile.close();
        client = await request.newContext({baseURL:base});
        check('Short password rejected by API', (await client.post('api/auth/register',{data:{username:'invalid_' + Date.now(),password:'short'}})).status() === 400);
        check('Invalid username rejected by API', (await client.post('api/auth/register',{data:{username:'bad name',password}})).status() === 400);
        check('Failed registration does not authenticate', (await client.get('api/movies')).status() === 401);
        check('No browser JavaScript errors', errors.length === 0);
    } finally {
        if (browser) await browser.close();
        if (client) await client.dispose();
        fs.writeFileSync(path.join(out, process.env.AUTH_RESTART_CHECK ? 'auth-restart-results.json' : 'auth-browser-results.json'),
            JSON.stringify({date:new Date().toISOString(),username,results},null,2));
    }
})().catch(e => {console.error(e);process.exitCode=1;});
