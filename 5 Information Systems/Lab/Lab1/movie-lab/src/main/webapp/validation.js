'use strict';
const Validation = (() => {
    let nextId = 0;
    const decimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
    function message(input) {
        const value = input.value;
        const form = input.form;
        if (input.id === 'filter-value' && document.getElementById('filter-enabled').checked) {
            const field = document.getElementById('filter-column').value;
            const allowed = field === 'genre' ? ['WESTERN','COMEDY','TRAGEDY','HORROR'] : field === 'mpaaRating' ? ['G','PG','PG_13','R','NC_17'] : null;
            if (allowed && !allowed.includes(value)) return ['Введите одно из значений: {values}.', {values: allowed.join(', ')}];
        }
        if (!value) return input.required ? (input.tagName === 'SELECT' ? 'Выберите значение.' : 'Введите значение.') : '';
        const type = input.dataset.valueType;
        if (type === 'integer' || type === 'long') {
            if (!/^[+-]?\d+$/.test(value)) return 'Введите целое число.';
            const number = BigInt(value);
            const min = BigInt(input.dataset.min ?? (type === 'long' ? '-9223372036854775808' : '-2147483648'));
            const max = BigInt(input.dataset.max ?? (type === 'long' ? '9223372036854775807' : '2147483647'));
            if (number < min || number > max) return ['Введите целое число от {min} до {max}.', {min: String(min), max: String(max)}];
        } else if (type === 'number') {
            if (!decimal.test(value)) return 'Введите число, например 12.5.';
            const number = Number(value);
            if (!Number.isFinite(number)) return 'Введите конечное число.';
            if (input.dataset.positive === 'true' && number <= 0) return 'Введите число больше 0.';
            if (input.dataset.max && number > Number(input.dataset.max)) return ['Введите число не больше {max}.', {max: input.dataset.max}];
            if (['height', 'weight'].includes(input.name) && Math.fround(number) === 0)
                return 'Введите положительное число, которое не округляется до нуля в формате Float (например, 0.1).';
        }
        if (['totalBoxOffice', 'usaBoxOffice'].includes(input.name)) {
            const total = form?.elements?.totalBoxOffice?.value ?? '';
            const usa = form?.elements?.usaBoxOffice?.value ?? '';
            // 两个字段各自合法时再比较；总票房留空表示未知，不参与比较。
            if (decimal.test(total) && /^[+-]?\d+$/.test(usa)
                    && Number.isFinite(Number(total)) && Number(total) > 0
                    && Number(usa) > 0 && Number(usa) <= 2147483647 && Number(usa) > Number(total)) {
                return input.name === 'usaBoxOffice'
                    ? 'Сборы в США не могут превышать общие сборы. Уменьшите сборы в США или увеличьте общие сборы.'
                    : 'Общие сборы не могут быть меньше сборов в США. Увеличьте общие сборы или уменьшите сборы в США.';
            }
        }
        if (input.name === 'birthday') {
            const match = value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d{1,9})?)?(Z|[+-]\d{2}:\d{2})(?:\[([^\]]+)\])?$/);
            if (!match) return 'Введите дату и время с часовым поясом, например 1990-01-01T12:00:00+03:00[Europe/Moscow].';
            const [, ys, ms, ds, hs, mins, ss, offset, zone] = match;
            const y = Number(ys), m = Number(ms), d = Number(ds);
            const leap = y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
            const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
            const offsetHour = offset === 'Z' ? 0 : Number(offset.slice(1,3));
            const offsetMinute = offset === 'Z' ? 0 : Number(offset.slice(4));
            if (m < 1 || m > 12 || d < 1 || d > days[m-1] || +hs > 23 || +mins > 59 || +(ss || 0) > 59 || offsetHour > 18 || offsetMinute > 59 || (offsetHour === 18 && offsetMinute)) return 'Несуществующая дата или часовой пояс.';
            if (zone) { try { new Intl.DateTimeFormat('en', {timeZone: zone}); } catch { return 'Несуществующая дата или часовой пояс.'; } }
        }
        if (form?.id === 'register-form') {
            if (input.name === 'username' && !/^[\p{L}\p{N}_.-]{3,64}$/u.test(value.trim())) return 'Имя пользователя: от 3 до 64 букв, цифр или символов _ . -';
            if (input.name === 'password' && (value.length < 8 || value.length > 128)) return 'Пароль должен содержать от 8 до 128 символов';
            if (input.name === 'confirmation' && value !== form.elements.password.value) return 'Пароли не совпадают';
        }
        if (form?.dataset?.operation === 'redistribute' && input.name === 'to' && value === form.elements.from.value) return 'Выберите два разных жанра';
        return '';
    }
    function setError(input, error, server = false) {
        const output = input.parentElement.querySelector('.field-error');
        if (!output) return;
        input.setAttribute('aria-invalid', error ? 'true' : 'false');
        output.hidden = !error;
        UiText.render(output, () => server ? error : Array.isArray(error) ? UiText.format(...error) : UiText.format(error));
    }
    function validate(input) {
        const error = message(input);
        setError(input, error);
        return !error;
    }
    function attach(form) {
        form.noValidate = true;
        form.querySelectorAll('input:not([type=checkbox]), select').forEach(input => {
            if (input.dataset.validationReady) return;
            input.dataset.validationReady = 'true';
            if (input.type === 'number') {
                input.dataset.valueType = 'integer';
                input.dataset.min = input.min || '-2147483648';
                input.dataset.max = input.max || '2147483647';
                input.type = 'text';
                input.inputMode = 'numeric';
            }
            const output = document.createElement('small');
            output.className = 'field-error'; output.id = 'field-error-' + ++nextId;
            output.hidden = true; output.setAttribute('aria-live', 'polite');
            input.parentElement.append(output);
            input.setAttribute('aria-describedby', [input.getAttribute('aria-describedby'), output.id].filter(Boolean).join(' '));
            const onInput = () => {
                input.dataset.touched = 'true'; validate(input);
                if (input.name === 'password' && form.elements.confirmation?.dataset.touched) validate(form.elements.confirmation);
                if (input.name === 'from' && form.elements.to?.dataset.touched) validate(form.elements.to);
                // 改任一票房字段时同时更新另一字段的提示，修正后清除两处旧错误。
                if (['totalBoxOffice', 'usaBoxOffice'].includes(input.name)) {
                    const other = form.elements.namedItem(input.name === 'totalBoxOffice' ? 'usaBoxOffice' : 'totalBoxOffice');
                    if (other?.dataset.validationReady && (other.dataset.touched || other.value !== '')) validate(other);
                }
            };
            input.addEventListener('input', onInput); input.addEventListener('change', onInput); input.addEventListener('blur', onInput);
        });
    }
    function form(form) {
        let first;
        form.querySelectorAll('[data-validation-ready]').forEach(input => {
            input.dataset.touched = 'true';
            if (!validate(input) && !first) first = input;
        });
        first?.focus(); return !first;
    }
    function server(form, raw) {
        let mapped = false;
        for (const part of raw.split('; ')) {
            const key = part.match(/^(\w+):/)?.[1] || part.match(/^Некорректное поле (\w+):/)?.[1];
            const input = key && form.elements.namedItem(key);
            if (input) { setError(input, part, true); mapped = true; }
        }
        if (form.id === 'register-form' && raw === 'Это имя пользователя уже занято') { setError(form.elements.username, raw, true); mapped = true; }
        return mapped;
    }
    function clear(form) {
        form.querySelectorAll('[data-validation-ready]').forEach(input => { delete input.dataset.touched; setError(input, ''); });
    }
    return {attach, form, server, clear, message};
})();
