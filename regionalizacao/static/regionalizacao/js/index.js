let style = el => window.getComputedStyle(el);
let margin = (name, el) => parseFloat(style(el)['margin' + name]) || 0;
let px = n => parseFloat(n) + 'px';

function height(el) {
    let baseHeight = el.getClientRects()[0].height
    let margins = margin('Top', el) + margin('Bottom', el);
    return baseHeight + margins;
}

function byLabel(a, b) {
    let nameA = a.dataset.label.toUpperCase();
    let nameB = b.dataset.label.toUpperCase();
    if (nameA < nameB) {
        return -1;
    }
    if (nameA > nameB) {
        return 1;
    }
    return 0;
}

function byValue(a, b) {
    return b.dataset.value - a.dataset.value;
}

window.addEventListener("DOMContentLoaded", function () {
    let barsEl = document.querySelectorAll('#localidade .barchart > .bar');
    let bars = Array.prototype.slice.call(barsEl);
    let ys = bars.map((bar, i) => height(bar) * i);

    let style = document.createElement('style');
    style.type = 'text/css';
    let rule = (y, i) => `.localidade-bar-${i}{ transform: translateY(${px(y)}); }`;
    let rules = ys.map(rule);
    style.innerHTML = rules.join('\n');
    document.getElementsByTagName('head')[0].appendChild(style);

    let barchart = document.querySelector('#localidade .barchart');
    barchart.style.position = 'relative';
    barchart.style.height = px(height(bars[0]) + ys[ys.length - 1]);

    function sortOnChange() {
        let sortFunc = this.checked ? byLabel : byValue;
        bars.sort(sortFunc)
        bars.forEach((bar, i) => {
            bar.style.position = 'absolute';
            bar.className = `bar localidade-bar-${i}`;
        });

    }

    let localidadeOrderSwitch = document.querySelector('#localidade-order');
    localidadeOrderSwitch.addEventListener('change', sortOnChange);
    sortOnChange.call(localidadeOrderSwitch)
});

let baseUrl = '/static/regionalizacao/maps/'


let levels = [
    {
        filename: 'zonas.topojson',
        objName: 'zonas',
    },
    {
        filename: 'dre.topojson',
        objName: 'dre',
    },
    {
        filename: 'distritos.topojson',
        objName: 'distritos',
    },
]

window.addEventListener("DOMContentLoaded", function () {
    let levelIndex = document.querySelectorAll('#mapa .breadcrumb li').length - 1;
    let level = levels[levelIndex > 2 ? 2 : levelIndex];

    let svg = d3.select('svg.map-container');

    let x = svg.node().parentNode.offsetLeft,
        y = svg.node().parentNode.offsetTop,
        canvasWidth = svg.node().parentNode.offsetWidth * 3 / 3 + x,
        canvasHeight = Math.min((svg.node().parentNode.offsetHeight + y), 957);

    let width = Math.round(parseFloat(svg.style('width'))),
        height = Math.round(parseFloat(svg.style('height')));

    svg.attr('viewBox', '0 0 ' + width + ' ' + height);
    svg.style('position', 'relative');

    var gMap = svg.select('g.map');

    d3.json(baseUrl + level.filename).then(function (data) {
        let features = topojson.feature(data, data.objects[level.objName]);

        let bg = gMap.selectAll('path')
            .data(features.features)
            .enter().append('path')
        let focus = svg.selectAll('.focus path')
            .data(features.features, function (d) {
                return d ? d.id : this.dataset.id;
            })

        let focusFeatures = {features: focus.data(), type: 'FeatureCollection'}
        let projection = d3.geoMercator()
            .fitExtent([[x, y], [canvasWidth, canvasHeight]], focusFeatures)

        var path = d3.geoPath().projection(projection)
        let tooltip = d3.select('#map-tooltip')

        function tooltipOut(d) {
            tooltip.node().classList.remove('over');
        }

        focus
            .on("mouseover", function (d) {
                if (!(this.dataset.name && this.dataset.total)) return
                tooltip.node().classList.add('over');
                let point = projection(d3.geoCentroid(d)),
                    x = point[0],
                    y = point[1];
                if (200 < y && y <= 300) {
                    y *= 1.55;
                } else if (300 < y && y <= 400) {
                    y *= 1.4;
                } else if (400 < y && y <= 500) {
                    y *= 1.3;
                } else if (500 < y && y <= 600) {
                    y *= 1.2;
                } else if (600 < y && y <= 800) {
                    y *= 1.02;
                }
                tooltip.style("left", x * 0.77 + 'px')
                tooltip.style("top", y + 'px')
                tooltip.select('.content').html(
                    `<h4>${this.dataset.name}</h4>
                    <p>R$ ${this.dataset.total} em recursos</p>`
                )
            })
            .on("mouseout", tooltipOut)
            .merge(bg)
            .attr('d', path)
            .append('title')
            .text(d => d.properties.name);

        let schools = svg.selectAll('.schools use')
            .attr('transform', function () {
                let coord = projection([this.dataset.long, this.dataset.lat]);
                return `translate(${coord[0]} ${coord[1]})`
            })
            .attr('y', -70)
            .attr('x', -45)
            .on("mouseover", function () {
                if (!this.dataset.name) return
                tooltip.node().classList.add('over');
                let point = projection([this.dataset.long, this.dataset.lat]),
                    x = point[0],
                    y = point[1];
                if (200 < y && y <= 300) {
                    y *= 1.5
                } else if (300 < y && y <= 400) {
                    y *= 1.4
                } else if (400 < y && y <= 500) {
                    y *= 1.2
                } else if (500 < y && y <= 550) {
                    y *= 1.15
                }else if (550 < y && y <= 600) {
                    y *= 1.12
                } else if (600 < y && y <= 700) {
                    y *= 1.08
                } else if (700 < y && y <= 800) {
                    y *= 1.02
                }
                tooltip.style("left", x * 0.75 + 'px')
                tooltip.style("top", y + 'px')
                tooltip.select('.content').html(
                    `<h4>${this.dataset.name}</h4>`
                )
            })
            .on("mouseout", tooltipOut)
            .style('visibility', 'visible')
    });
});
