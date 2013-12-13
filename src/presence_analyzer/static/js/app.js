function parseInterval(value) {
    var result = new Date(1, 1, 1);
    result.setMilliseconds(value * 1000);
    return result;
}


function show_avatar(avatar_url) {
    $('#user_data').empty()
    $('#user_data').append($('<img />').attr('src', avatar_url));
}


(function ($) {
    $(document).ready(function () {

        var loading = $('#loading');

        $.getJSON("/api/v1/users", function (result) {

            var dropdown = $("#user_id");

            $.each(result, function (item) {
                // add avatar
                dropdown.append($("<option />").attr('data-avatar', this.avatar).val(this.user_id).text(this.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function () {

            var selected_user = $("#user_id").val(),
                chart_div = $('#chart_div'),
                name = $('#selected').attr('name'),
                // add avatar variable and call function
                avatar_url = $('#user_id option[value=' + selected_user + ']').data('avatar');
            show_avatar(avatar_url);

            if (selected_user === '') {
                // hide previous chart if user is not selected
                chart_div.hide();
            } else {
                chart_div.hide();
                loading.show();

                if (name === "mean_time") {
                    $.getJSON("/api/v1/mean_time_weekday/" + selected_user, function (result) {

                        var data = new google.visualization.DataTable(),
                            options = { hAxis: {title: 'Weekday'}},
                            formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                            chart = new google.visualization.ColumnChart(chart_div[0]);

                        $.each(result, function (index, value) {
                            value[1] = parseInterval(value[1]);
                        });

                        console.log(result);
                        data.addColumn('string', 'Weekday');
                        data.addColumn('datetime', 'Mean time (h:m:s)');
                        data.addRows(result);
                        formatter.format(data, 1);
                        chart_div.show();
                        loading.hide();
                        chart.draw(data, options);
                    });
                } else if (name === "presense_weekday") {
                    $.getJSON("/api/v1/presence_weekday/" + selected_user, function (result) {

                        var data = google.visualization.arrayToDataTable(result),
                            options = {},
                            chart = new google.visualization.PieChart(chart_div[0]);

                        chart_div.show();
                        loading.hide();
                        chart.draw(data, options);
                    });
                } else {
                    $.getJSON("/api/v1/presence_start_end/" + selected_user, function (result) {

                        var data = new google.visualization.DataTable(),
                            options = { hAxis: {title: 'Weekday'}},
                            formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'}),
                            chart = new google.visualization.Timeline(chart_div[0]);

                        $.each(result, function (index, value) {
                            value[1] = parseInterval(value[1]);
                            value[2] = parseInterval(value[2]);
                        });

                        data.addColumn('string', 'Weekday');
                        data.addColumn({ type: 'datetime', id: 'Start' });
                        data.addColumn({ type: 'datetime', id: 'End' });
                        data.addRows(result);
                        formatter.format(data, 1);
                        formatter.format(data, 2);
                        chart_div.show();
                        loading.hide();
                        chart.draw(data, options);
                    });
                }
            }
        });
    });
})(jQuery);