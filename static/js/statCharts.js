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


    stats.forEach(function (item, i) {
        statsSh.push([i.toString(), item[1], item[2]])
        statsSog.push([i.toString(), item[3], item[4]])
        statsG.push([i.toString(), item[5], item[6]])
        statsBlocks.push([i.toString(), item[8], item[9]])
        statsHits.push([i.toString(), item[7]])
        statsPenalty.push([i.toString(), item[10]])
    });


    var dataSh = google.visualization.arrayToDataTable(statsSh);
    var dataSog = google.visualization.arrayToDataTable(statsSog);
    var dataG = google.visualization.arrayToDataTable(statsG);
    var dataBlocks = google.visualization.arrayToDataTable(statsBlocks);
    var dataHits = google.visualization.arrayToDataTable(statsHits);
    var dataPenalty = google.visualization.arrayToDataTable(statsPenalty);

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

    chartSh.draw(dataSh, options);
    chartSog.draw(dataSog, options);
    chartG.draw(dataG, options);
    chartBlocks.draw(dataBlocks, options);
    chartHits.draw(dataHits, options);
    chartPenalty.draw(dataPenalty, options);
}