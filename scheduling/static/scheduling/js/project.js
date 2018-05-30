$(document).ready(function () {

    $('.methods-list').on('click', '.methods-list__item:not(.active)', function() {
        $(this).addClass('active').siblings().removeClass('active');
    });

    $('.js-open-ga-form').click( function (event) {
        event.preventDefault();
        $('.project-right-col > *:not(.genetic-algorithm-form)').hide();
        $('.genetic-algorithm-form').toggle();
    });

    $('.js-create-schedule').click( function (event) {
        event.preventDefault();
        $('.project-right-col > *').hide();
        $('.create-schedule-form').attr('action', $(this).attr('data-url'));
        $('.create-schedule-form').submit();
    });


    $('.create-schedule-form').submit(function (event) {
        event.preventDefault();
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                if (response.show_statistic){
                    $('.statistic').show();
                    init_statistic(response.statistic);
                }
                init_gantt(response.statistic.data_dict);
                $('.gantt').show();
            }).fail(function (xhr, responseText) {
        });
    });

    $('.genetic-algorithm-form').submit(function (event) {
        event.preventDefault();
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                if (response.status === 'OK') {
                    var statistic = response.statistic;
                    init_statistic(statistic);
                    init_gantt(statistic.data_dict);
                    $('.gantt, .statistic').show()
                }
            }).fail(function (xhr, responseText) {
        });
    });

    function init_statistic(data) {
        var settings = {
            title: {
                style: {
                    color: '#fff'
                },
                text: 'Результат работы алгоритма',
                x: -20 //center
            },
            chart: {
                backgroundColor: '#fff',
                borderColor: '#64a1e8',
                borderWidth: 1,
                zoomType: 'x',
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
        };
        if (data.ave_fit) {
            settings.series.push({
                name: 'Average Fitness',
                data: data.ave_fit
            });
        }
        $('.statistic').highcharts(settings);
    }


    function init_gantt(schedule) {
        g.setCaptionType('Complete');
        g.setQuarterColWidth(68);
        g.setShowRes(1); // Show/Hide Responsible (0/1)
        g.setShowDur(1); // Show/Hide Duration (0/1)
        g.setShowComp(0); // Show/Hide % Complete(0/1)
        g.setShowDeps(1);
        g.setShowTaskInfoRes(1); // Show/hide resource in the task tooltip
        g.setCaptionType('Resource'); // Set to Show Caption (None,Caption,Resource,Duration,Complete)
        // Parameters (pID, pName, pStart, pEnd, pColor,   pLink, pMile, pRes,  pComp - 0, pGroup- 0, pParent - 0, pOpen 1, pDepend, pCaption, pNotes, pGantt)

        if( g ) {
            for( var s in schedule) {
                var item = schedule[s];
                g.AddTaskItem(new JSGantt.TaskItem(item.id_num, item.name,  item.start_time, item.end_time, 'gtaskred', '', 0, 'fdsf'/*item.executor_name*/, 0, 0, 0, 1, item.predecessors, '', '', g));
            }

            g.Draw();
            g.DrawDependencies();
          }
          else {
            alert("not defined");
          }
    }
});