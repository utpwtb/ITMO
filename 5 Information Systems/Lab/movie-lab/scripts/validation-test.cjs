/* Pure field-rule regression checks; no browser, server or database mutations. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(path.join(__dirname, '../src/main/webapp/validation.js'), 'utf8');
const validation = vm.runInNewContext(source + '\nValidation;', {Intl});
let count = 0;
function check(name, value, expectedValid, options = {}) {
    const input = {value, name: '', id: '', required: false, tagName: 'INPUT', dataset: {}, ...options};
    assert.equal(!validation.message(input), expectedValid, name);
    console.log('PASS ' + name); count++;
}
const long = {dataset:{valueType:'long'}};
const integer = {dataset:{valueType:'integer',min:'-2147483648',max:'826'}};
const number = {dataset:{valueType:'number'}};
check('Long rejects letters', 'abc', false, long);
check('Long rejects fractions', '1.2', false, long);
check('Long max exact', '9223372036854775807', true, long);
check('Long max plus one', '9223372036854775808', false, long);
check('Long min exact', '-9223372036854775808', true, long);
check('Long min minus one', '-9223372036854775809', false, long);
check('Long scientific notation rejected', '1e3', false, long);
check('Coordinate max', '826', true, integer);
check('Coordinate max plus one', '827', false, integer);
check('Coordinate negatives valid', '-1', true, integer);
check('Coordinate int underflow', '-2147483649', false, integer);
check('Decimal letters rejected', 'abc', false, number);
check('Decimal valid', '-12.5', true, number);
check('Decimal zero valid', '0', true, number);
check('Decimal scientific valid', '1e3', true, number);
check('Decimal infinity rejected', '1e309', false, number);
check('Decimal NaN rejected', 'NaN', false, number);
check('Positive field rejects zero', '0', false, {dataset:{valueType:'number',positive:'true'}});
check('Positive field allows omitted', '', true, {dataset:{valueType:'number',positive:'true'}});
check('Float upper bound', '3.5e38', false, {dataset:{valueType:'number',max:'3.4028235e38'}});
check('Required empty', '', false, {required:true});
check('Optional empty tagline', '', true);
check('Birthday without zone', '1990-01-01T12:00:00', false, {name:'birthday'});
check('Birthday valid zone', '1990-01-01T12:00:00+03:00[Europe/Moscow]', true, {name:'birthday'});
check('Birthday nonexistent date', '2025-02-29T00:00:00Z', false, {name:'birthday'});
check('Birthday leap date', '2024-02-29T00:00:00Z', true, {name:'birthday'});
check('Birthday invalid zone', '2024-02-29T00:00:00Z[Bad/Zone]', false, {name:'birthday'});
check('Birthday invalid offset', '2024-02-29T00:00:00+18:30', false, {name:'birthday'});
check('Registration short password', 'short', false, {name:'password',form:{id:'register-form'}});
check('Registration valid username', '测试_user', true, {name:'username',form:{id:'register-form'}});
check('Registration invalid username', 'has spaces', false, {name:'username',form:{id:'register-form'}});
check('Confirmation mismatch', 'different', false, {name:'confirmation',form:{id:'register-form',elements:{password:{value:'correct'}}}});
check('Redistribute same genre', 'COMEDY', false, {name:'to',form:{dataset:{operation:'redistribute'},elements:{from:{value:'COMEDY'}}}});
for (const field of ['oscarsCount', 'length', 'usaBoxOffice']) {
    const options = {name:field,required:true,dataset:{valueType:'integer',min:'1',max:'2147483647'}};
    check(field + ' required', '', false, options);
    check(field + ' rejects zero', '0', false, options);
    check(field + ' accepts one', '1', true, options);
    check(field + ' rejects overflow', '2147483648', false, options);
}
for (const field of ['budget', 'goldenPalmCount']) {
    const options = {name:field,required:field==='budget',dataset:{valueType:'long',min:'1'}};
    check(field + ' empty rule', '', field!=='budget', options);
    check(field + ' rejects zero', '0', false, options);
    check(field + ' accepts max long', '9223372036854775807', true, options);
}
for (const field of ['height', 'weight']) {
    const options = {name:field,dataset:{valueType:'number',positive:'true',max:'3.4028235e38'}};
    check(field + ' may be absent', '', true, options);
    check(field + ' rejects zero', '0', false, options);
    check(field + ' rejects Float underflow', '1e-46', false, options);
    check(field + ' accepts small positive Float', '1e-45', true, options);
    check(field + ' accepts usual decimal', '175.5', true, options);
}
function checkBox(total, usa, valid, description) {
    const elements = {totalBoxOffice:{value:total},usaBoxOffice:{value:usa}};
    for (const field of ['totalBoxOffice','usaBoxOffice']) {
        check(description + ' / ' + field, elements[field].value, valid, {
            name:field, form:{elements}, required:field==='usaBoxOffice',
            dataset:field==='usaBoxOffice' ? {valueType:'integer',min:'1',max:'2147483647'} : {valueType:'number',positive:'true'}
        });
    }
}
checkBox('100', '200', false, 'USA above total rejected');
checkBox('200', '200', true, 'USA equals total accepted');
checkBox('200.5', '200', true, 'Decimal total above USA accepted');
checkBox('199.5', '200', false, 'Decimal total below USA rejected');
checkBox('', '200', true, 'Unknown total accepted');
checkBox('2e2', '200', true, 'Scientific total accepted');
checkBox('2147483647', '2147483647', true, 'Max int equality accepted');
checkBox('1.7976931348623157e308', '2147483647', true, 'Large total accepted');
console.log(`${count} checks passed`);
