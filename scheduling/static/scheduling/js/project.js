$(document).ready(function () {
    
    
    $('.js-open-ga-form').click( function (event) {
        event.preventDefault();
        $('.genetic-algorithm-form').toggle();
    });

    $('.js-submit-bb').click( function (event) {
        event.preventDefault();
        $('.branch-and-bound-algorithm-form').submit();
    });

    $('.js-submit-ph').click( function (event) {
        event.preventDefault();
        $('.heuristic-form').submit();
    });

    $('.genetic-algorithm-form').submit(function (event) {
        event.preventDefault();
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                if (response.status === 'OK') {
                    var statistic = response.statistic;
                    $('.statistic').show();

                    init_statistic_ga(statistic);
                    init_gantt(statistic.data_dict);
                    $('.gantt').show()
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
                init_gantt(response.statistic.data_dict);
                $('.gantt').show();
            }).fail(function (xhr, responseText) {
        });
    });

    $('.heuristic-form').submit(function (event) {
        event.preventDefault();
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                $('.heuristic-form').append('<div>Best Fit: '+ response.statistic.best_fit + '</div>');
                init_gantt(response.statistic.data_dict);
            $('.gantt').show();
            }).fail(function (xhr, responseText) {
        });
    });

    function init_statistic_ga(data) {
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
            },

            plotOptions: {
                series: {
                    pointStart: 0
                }
            },
            series: [{
                name: 'Best Fitness',
                data: data.best_fit
            }, {
                name: 'Average Fitness',
                data: data.ave_fit
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
                }
            },

            xAxis: {
                title: {
                    style: {
                        color: '#000'
                    },
                    text: 'iterations'
                }
            },

            plotOptions: {
                series: {
                    pointStart: 0
                }
            },
            series: [{
                name: 'Best Fitness',
                data: data.best_fit
            }]
        });
    };

    function init_gantt(schedule) {
        g.setShowRes(1); // Show/Hide Responsible (0/1)
        g.setShowDur(1); // Show/Hide Duration (0/1)
        g.setShowComp(0); // Show/Hide % Complete(0/1)
        g.setCaptionType('Resource');  // Set to Show Caption

        // Parameters (pID, pName, pStart, pEnd, pColor,   pLink, pMile, pRes,  pComp - 0, pGroup- 0, pParent - 0, pOpen 1, pDepend)

        if( g ) {
            for( var s in schedule) {
                var item = schedule[s]
                g.AddTaskItem(new JSGantt.TaskItem(item.id_num, item.name,  item.start_time, item.end_time, 'ff0000', '', 0, schedule[s].executor_name, 0, 0, 0, 1, item.predecessors));
            }

            g.Draw();
            g.DrawDependencies();
          }
          else {
            alert("not defined");
          }
    }
});