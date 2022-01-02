google.charts.load('current', {'packages':['corechart']});


function hideChart() {
    drawChart(0);
    addButtons();
    setSidebarTopValue();
    }


const stat_values = stats[0]
const stat_short_names = stats[1]
const stat_full_names = stats[2]

const stat_num = stat_short_names.length
let stats_data = [];

let i = 0;
while (i !== stat_num) {
    stats_data.push([])
    i += 1
}


stat_values.forEach(function (item, i) {
    let ii = 0 ;
    while (ii !== stat_num) {
        stats_data[ii].push([i.toString(), item[ii], item[stat_num + ii]])
        ii += 1
    }
});

let options = {
        curveType: 'function',
        'min-width': 1200,
        height: 400,
        colors: [],
        legend: {
            position: 'bottom',
            alignment: 'center',
            textStyle: {
                color: '#d9d2d2'
        }},
        hAxis: {
            gridlines: {
                color: '#8f8c8c',
                opacity: 0.1
            },
            textStyle: {
                color: '#d9d2d2'
            },
            titleTextStyle: {
                color: '#d9d2d2'
            }
        },
        vAxis: {
            gridlines: {
                color: '#8f8c8c',
                opacity: 0.1
            },
            textStyle: {
                color: '#d9d2d2'
            },
            titleTextStyle: {
                color: '#d9d2d2'
            }
        },
        chartArea: {
            width: '90%',
            height: '90%',
        },
        backgroundColor: {
                fill: '#ffffff',
                fillOpacity: 0.1,
                stroke: '#FFFFFF33',
                strokeWidth: 1
            }
    };



function drawChart(i) {
    let left_color = getComputedStyle(document.getElementById('chart-stat_left')).color
    let right_color =  getComputedStyle(document.getElementById('chart-stat_right')).color
    options['colors'] = [left_color, right_color]
    let data = google.visualization.arrayToDataTable(stats_data[i]);
    let chart = new google.visualization.LineChart(document.getElementById('chart'));
    chart.draw(data, options);

    let title1 = document.getElementById('chartTitle1')
    let title2 = document.getElementById('chartTitle2')

    if (title1 !== null) {
        title1.innerHTML = stat_full_names[i]
    }
    if (title2 !== null) {
        title2.innerHTML = stat_short_names[i]
    }
}

function addButtons() {
    let ul = document.getElementById('chartList')
    stat_short_names.forEach(function (item, i) {
        ul.innerHTML = ul.innerHTML + `<a onclick=drawChart(${i}) id="BchartSh"><li>${item}</li></a>`
    })

}

function setSidebarTopValue() {
    let chart = document.getElementById('chart')
    let sidebar = document.getElementById('rightSideBar')
    let coords = getCoords(chart)

    let top = coords['top'] - 236
    sidebar.style.marginTop = `${top}px`
}


// координаты элемента в контексте документа
function getCoords(elem) {
  let box = elem.getBoundingClientRect();

  return {
    top: box.top + window.pageYOffset,
    right: box.right + window.pageXOffset,
    bottom: box.bottom + window.pageYOffset,
    left: box.left + window.pageXOffset
  };
}