google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);


function hideChart() {
    var chartsID = ['chartSh', 'chartSog', 'chartG', 'chartBlocks', 'chartHits', 'chartPenalty']
    chartsID.forEach(function (item) {
        document.getElementById(item).style.display = 'none';
    });
    }


function filterChart(elementID) {
    var chartsID = ['chartSh', 'chartSog', 'chartG', 'chartBlocks', 'chartHits', 'chartPenalty']
    chartsID.forEach(function (item) {
        document.getElementById(item).style.display = 'none';
    });
    document.getElementById(elementID).style.display = 'block';
}


function drawChart() {

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


    var dataSh = google.visualization.arrayToDataTable(statsSh);
    var dataSog = google.visualization.arrayToDataTable(statsSog);
    var dataG = google.visualization.arrayToDataTable(statsG);
    var dataBlocks = google.visualization.arrayToDataTable(statsBlocks);
    var dataHits = google.visualization.arrayToDataTable(statsHits);
    var dataPenalty = google.visualization.arrayToDataTable(statsPenalty);
    var dataTime_a = google.visualization.arrayToDataTable(statsTime_a);

    // https://developers.google.com/chart/interactive/docs/gallery/linechart#configuration-options
    var options = {
        curveType: 'function',
        title: 'Company Performance',
        legend: { alignment: 'center'},
        width: 1900,
        height: 500,
        backgroundColor: 'white',
    };

    var chartSh = new google.visualization.LineChart(document.getElementById('chartSh'));
    var chartSog = new google.visualization.LineChart(document.getElementById('chartSog'));
    var chartG = new google.visualization.LineChart(document.getElementById('chartG'));
    var chartBlocks = new google.visualization.LineChart(document.getElementById('chartBlocks'));
    var chartHits = new google.visualization.LineChart(document.getElementById('chartHits'));
    var chartPenalty = new google.visualization.LineChart(document.getElementById('chartPenalty'));
    var chartTime_a = new google.visualization.LineChart(document.getElementById('chartTime_a'));

    chartSh.draw(dataSh, options);
    chartSog.draw(dataSog, options);
    chartG.draw(dataG, options);
    chartBlocks.draw(dataBlocks, options);
    chartHits.draw(dataHits, options);
    chartPenalty.draw(dataPenalty, options);
    chartTime_a.draw(dataTime_a, options);
}