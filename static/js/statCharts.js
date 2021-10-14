google.charts.load('current', {'packages':['corechart']});


window.onload = function() {
    hideChart()
}


function hideChart() {
    const chartsID = ['chartSh', 'chartSog', 'chartG', 'chartBlocks', 'chartHits', 'chartPenalty', 'chartTime_a']
    chartsID.forEach(function (item) {
        drawChart(item);
        document.getElementById(item).style.display = 'none';
    });
    document.getElementById('chartSh').style.display = 'block';
    }


function filterChart(elementID) {
    const chartsID = ['chartSh', 'chartSog', 'chartG', 'chartBlocks', 'chartHits', 'chartPenalty', 'chartTime_a']
    chartsID.forEach(function (item) {
        document.getElementById(item).style.display = 'none';
    });
    document.getElementById(elementID).style.display = 'block';
}

var statsSh = [];
var statsSog = [];
var statsG = [];
var statsBlocks = [];
var statsHits = [];
var statsPenalty = [];
var statsTime_a = [];

stats.forEach(function (item, i) {
    statsSh.push([i.toString(), item[0], item[7]])
    statsSog.push([i.toString(), item[1], item[8]])
    statsG.push([i.toString(), item[2], item[9]])
    statsBlocks.push([i.toString(), item[3], item[10]])
    statsHits.push([i.toString(), item[5]])
    statsPenalty.push([i.toString(), item[4]])
    statsTime_a.push([i.toString(), item[6], item[13]])
});

    var options = {
        curveType: 'function',
        'min-width': 1200,
        height: 400,
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




function drawChart(elementID) {
    switch (elementID) {
        case 'chartSh':
            var dataSh = google.visualization.arrayToDataTable(statsSh);
            var chartSh = new google.visualization.LineChart(document.getElementById('chartSh'));
            chartSh.draw(dataSh, options);
            break;
        case 'chartSog':
            var dataSog = google.visualization.arrayToDataTable(statsSog);
            var chartSog = new google.visualization.LineChart(document.getElementById('chartSog'));
            chartSog.draw(dataSog, options);
            break;
        case 'chartG':
            var dataG = google.visualization.arrayToDataTable(statsG);
            var chartG = new google.visualization.LineChart(document.getElementById('chartG'));
            chartG.draw(dataG, options);
            break;
        case 'chartBlocks':
            var dataBlocks = google.visualization.arrayToDataTable(statsBlocks);
            var chartBlocks = new google.visualization.LineChart(document.getElementById('chartBlocks'));
            chartBlocks.draw(dataBlocks, options);
            break;
        case 'chartHits':
            var dataHits = google.visualization.arrayToDataTable(statsHits);
            var chartHits = new google.visualization.LineChart(document.getElementById('chartHits'));
            chartHits.draw(dataHits, options);
            break;
        case 'chartPenalty':
            var dataPenalty = google.visualization.arrayToDataTable(statsPenalty);
            var chartPenalty = new google.visualization.LineChart(document.getElementById('chartPenalty'));
            chartPenalty.draw(dataPenalty, options);
            break;
        case 'chartTime_a':
            var dataTime_a = google.visualization.arrayToDataTable(statsTime_a);
            var chartTime_a = new google.visualization.LineChart(document.getElementById('chartTime_a'));
            chartTime_a.draw(dataTime_a, options);
            break;
    }
}
