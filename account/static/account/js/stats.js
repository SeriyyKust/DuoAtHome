/* DuoAtHome: отрисовка статистики на главной (heatmap, бар-чарт, донат). */
(function () {
    'use strict';

    var MONTHS_SHORT = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
    var MONTHS_FULL = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь',
        'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'];
    var WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
    var HEAT_WEEKS = 52;   // сколько недель показываем на heatmap (год, с гориз. прокруткой)

    /* ---------- Вспомогательные ---------- */

    function pad(n) { return (n < 10 ? '0' : '') + n; }

    function iso(d) {
        return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    }

    function parseISO(s) {
        var p = s.split('-');
        return new Date(+p[0], +p[1] - 1, +p[2]);
    }

    function addDays(d, n) {
        var r = new Date(d.getTime());
        r.setDate(r.getDate() + n);
        return r;
    }

    function plural(n, one, few, many) {
        var m10 = n % 10, m100 = n % 100;
        if (m10 === 1 && m100 !== 11) return one;
        if (m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20)) return few;
        return many;
    }

    function activitiesLabel(n) {
        return n + ' ' + plural(n, 'активность', 'активности', 'активностей');
    }

    function formatDateRu(d) {
        return d.getDate() + '.' + pad(d.getMonth() + 1) + '.' + d.getFullYear();
    }

    /* ---------- Общий тултип ---------- */

    var tooltip = document.createElement('div');
    tooltip.className = 'stats-tooltip';
    document.addEventListener('DOMContentLoaded', function () {
        document.body.appendChild(tooltip);
    });

    function moveTooltip(e) {
        var x = e.clientX + 14;
        var y = e.clientY - 34;
        var rect = tooltip.getBoundingClientRect();
        if (x + rect.width > window.innerWidth - 8) x = e.clientX - rect.width - 14;
        if (y < 8) y = e.clientY + 16;
        tooltip.style.left = x + 'px';
        tooltip.style.top = y + 'px';
    }

    function attachTooltip(el, text) {
        el.addEventListener('mouseenter', function (e) {
            tooltip.textContent = text;
            tooltip.classList.add('is-visible');
            moveTooltip(e);
        });
        el.addEventListener('mousemove', moveTooltip);
        el.addEventListener('mouseleave', function () {
            tooltip.classList.remove('is-visible');
        });
    }

    /* ---------- Heatmap ---------- */

    function heatLevel(count) {
        if (count <= 0) return 0;
        if (count < 10) return 1;
        if (count < 20) return 2;
        if (count < 30) return 3;
        return 4;
    }

    function renderHeatmap(days) {
        var grid = document.getElementById('heatmap-grid');
        var months = document.getElementById('heatmap-months');
        if (!grid || !months) return;

        var byDate = {};
        days.forEach(function (d) { byDate[d.date] = d.count; });

        var today = parseISO(days[days.length - 1].date);
        var dow = (today.getDay() + 6) % 7;            // 0 = Пн
        var mondayThis = addDays(today, -dow);
        var start = addDays(mondayThis, -(HEAT_WEEKS - 1) * 7);

        var frag = document.createDocumentFragment();
        var labeled = [];

        for (var w = 0; w < HEAT_WEEKS; w++) {
            var col = document.createElement('div');
            col.className = 'heat-col';

            for (var i = 0; i < 7; i++) {
                var day = addDays(start, w * 7 + i);
                var cell = document.createElement('i');
                cell.className = 'heat-cell';

                if (day > today) {
                    cell.classList.add('is-empty');
                } else {
                    var count = byDate[iso(day)] || 0;
                    cell.classList.add('l' + heatLevel(count));
                    attachTooltip(cell, activitiesLabel(count) + ' • ' + formatDateRu(day));
                }
                col.appendChild(cell);
            }
            frag.appendChild(col);

            // Подписи месяцев: когда неделя содержит начало нового месяца
            var monday = addDays(start, w * 7);
            if (monday.getDate() <= 7 && (labeled.length === 0 ||
                monday.getMonth() !== labeled[labeled.length - 1].month) &&
                (labeled.length === 0 || w - labeled[labeled.length - 1].col >= 3)) {
                labeled.push({ col: w, month: monday.getMonth() });
            }
        }
        grid.appendChild(frag);

        var fragM = document.createDocumentFragment();
        labeled.forEach(function (l) {
            var span = document.createElement('span');
            span.textContent = MONTHS_SHORT[l.month];
            span.style.left = 'calc(' + l.col + ' * (var(--heat-cell) + var(--heat-gap)))';
            fragM.appendChild(span);
        });
        months.appendChild(fragM);
    }

    /* ---------- Бар-чарт (ступенчатая диаграмма) ---------- */

    function buildBuckets(days, period) {
        var buckets = [];
        var i, d, key;

        if (period === 'week') {
            for (i = days.length - 7; i < days.length; i++) {
                d = parseISO(days[i].date);
                buckets.push({
                    count: days[i].count,
                    label: WEEKDAYS[(d.getDay() + 6) % 7],
                    tip: activitiesLabel(days[i].count) + ' • ' + formatDateRu(d),
                });
            }
        } else if (period === 'month') {
            for (i = days.length - 30; i < days.length; i++) {
                d = parseISO(days[i].date);
                buckets.push({
                    count: days[i].count,
                    label: d.getDate() % 5 === 0 ? String(d.getDate()) : '',
                    tip: activitiesLabel(days[i].count) + ' • ' + formatDateRu(d),
                });
            }
        } else { // year: последние 12 месяцев
            var byMonth = {};   // ключ YYYY-MM -> {count, m, y}, порядок вставки сохраняется
            var order = [];
            days.forEach(function (day) {
                key = day.date.slice(0, 7);
                if (!byMonth[key]) {
                    byMonth[key] = { count: 0, m: +key.slice(5, 7) - 1, y: +key.slice(0, 4) };
                    order.push(key);
                }
                byMonth[key].count += day.count;
            });
            var last12 = order.slice(-12);
            last12.forEach(function (k) {
                var b = byMonth[k];
                buckets.push({
                    count: b.count,
                    label: MONTHS_SHORT[b.m],
                    tip: activitiesLabel(b.count) + ' • ' + MONTHS_FULL[b.m] + ' ' + b.y,
                });
            });
        }
        return buckets;
    }

    function renderBars(days, period) {
        var canvas = document.getElementById('barchart');
        if (!canvas) return;
        canvas.innerHTML = '';

        var buckets = buildBuckets(days, period);
        var max = 0;
        buckets.forEach(function (b) { if (b.count > max) max = b.count; });

        var frag = document.createDocumentFragment();
        buckets.forEach(function (b) {
            var col = document.createElement('div');
            col.className = 'bar-col';

            var track = document.createElement('div');
            track.className = 'bar-track';

            var bar = document.createElement('div');
            bar.className = 'bar';
            var h = max > 0 ? Math.round(b.count / max * 100) : 0;
            if (b.count > 0 && h < 4) h = 4;
            bar.style.height = h + '%';
            attachTooltip(bar, b.tip);
            track.appendChild(bar);

            var label = document.createElement('span');
            label.className = 'bar-label';
            label.textContent = b.label;

            col.appendChild(track);
            col.appendChild(label);
            frag.appendChild(col);
        });
        canvas.appendChild(frag);
    }

    function initBarSwitch(days) {
        var switcher = document.getElementById('bar-period-switch');
        if (!switcher) return;
        switcher.addEventListener('click', function (e) {
            var btn = e.target.closest('.chart-switch__btn');
            if (!btn) return;
            switcher.querySelectorAll('.chart-switch__btn').forEach(function (b) {
                b.classList.toggle('is-active', b === btn);
            });
            renderBars(days, btn.dataset.period);
        });
    }

    /* ---------- Донат (круговая диаграмма слов) ---------- */

    function renderDonut(words) {
        var svg = document.getElementById('donut');
        if (!svg) return;

        var segments = [
            { cls: 'donut__seg--learned', label: 'Выучено', value: words.learned },
            { cls: 'donut__seg--review', label: 'На повторении', value: words.review },
            { cls: 'donut__seg--tolearn', label: 'К изучению', value: words.to_learn },
        ];
        var total = 0;
        segments.forEach(function (s) { total += s.value; });
        if (total === 0) return;

        var R = 60, C = 2 * Math.PI * R;
        var offset = 0;
        var NS = 'http://www.w3.org/2000/svg';

        segments.forEach(function (s) {
            var len = s.value / total * C;
            var circle = document.createElementNS(NS, 'circle');
            circle.setAttribute('cx', 80);
            circle.setAttribute('cy', 80);
            circle.setAttribute('r', R);
            circle.setAttribute('class', 'donut__seg ' + s.cls);
            circle.setAttribute('stroke-dasharray', len + ' ' + (C - len));
            circle.setAttribute('stroke-dashoffset', -offset);
            attachTooltip(circle, s.label + ': ' + s.value + ' ' + plural(s.value, 'слово', 'слова', 'слов'));
            svg.appendChild(circle);
            offset += len;
        });

        var t1 = document.createElementNS(NS, 'text');
        t1.setAttribute('x', 80); t1.setAttribute('y', 76);
        t1.setAttribute('class', 'donut__total');
        t1.textContent = total;
        var t2 = document.createElementNS(NS, 'text');
        t2.setAttribute('x', 80); t2.setAttribute('y', 94);
        t2.setAttribute('class', 'donut__caption');
        t2.textContent = 'всего слов';
        svg.appendChild(t1);
        svg.appendChild(t2);
    }

    /* ---------- Инициализация ---------- */

    function readJSON(id) {
        var el = document.getElementById(id);
        return el ? JSON.parse(el.textContent) : null;
    }

    document.addEventListener('DOMContentLoaded', function () {
        var activity = readJSON('activity-data');
        var words = readJSON('words-data');

        if (activity && activity.days) {
            renderHeatmap(activity.days);
            renderBars(activity.days, 'week');
            initBarSwitch(activity.days);
        }
        if (words) {
            renderDonut(words);
        }
    });
})();
