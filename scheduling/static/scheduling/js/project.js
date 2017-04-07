$(document).ready(function () {
    $('.genetic-algorithm-form').submit(function (event) {
        event.preventDefault();
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                console.log(response);
                if (response.status === 'OK') {
                    var statistic = response.statistic;
                    $('.statistic').show();
                    init_statistic_ga(statistic);
                }
            }).fail(function (xhr, responseText) {
        });
    });

    $('.branch-and-bound-algorithm-form').submit(function (event) {
        event.preventDefault();
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                $('.statistic').show();
                init_statistic_branch_bounds(response.statistic);
            }).fail(function (xhr, responseText) {
        });
    });

    function init_statistic_ga(data) {
        var bestValues = data.best_fit;
        var aveValues = data.ave_fit;


        $('.statistic').highcharts({
            title: {
                style: {
                    color: '#fff'
                },
                text: 'Результат работы генетического алгоритма',
                x: -20 //center
            },
            chart: {
                backgroundColor: '#fff',
                borderColor: '#64a1e8',
                borderWidth: 1,
                zoomType: 'x'
            },

            yAxis: {
                title: {
                    style: {
                        color: '#000'
                    },
                    text: 'durations'
                },
                labels: {
                    style: {
                        color: '#fff'
                    }
                }
            },

            plotOptions: {
                series: {
                    pointStart: 0
                }
            },
            series: [{
                name: 'Best Fitness',
                data: bestValues
            }, {
                name: 'Average Fitness',
                data: aveValues
            }]
        });
    }

    function init_statistic_branch_bounds(data) {

        $('.statistic').highcharts({
            title: {
                style: {
                    color: '#fff'
                },
                text: 'Результат работы метода ветвей и границ',
                x: -20 //center
            },
            chart: {
                backgroundColor: '#fff',
                borderColor: '#64a1e8',
                borderWidth: 1,
                zoomType: 'x'
            },

            yAxis: {
                title: {
                    style: {
                        color: '#000'
                    },
                    text: 'durations'
                },
                labels: {
                    style: {
                        color: '#fff'
                    }
                }
            },

            plotOptions: {
                series: {
                    pointStart: 0
                }
            },
            series: [{
                name: 'Best Fitness',
                data: data
            }]
        });
    }
});