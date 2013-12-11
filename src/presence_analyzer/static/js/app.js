function parseInterval(value) {
    var result = new Date(1,1,1);
    result.setMilliseconds(value*1000);
    return result;
    }



(function($) {
    $(document).ready(function(){
        var loading = $('#loading');
        $.getJSON("/api/v1/users", function(result) {
            var dropdown = $("#user_id");
            $.each(result, function(item) {
                dropdown.append($("<option />").val(this.user_id).text(this.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function(){
            var selected_user = $("#user_id").val();
            var chart_div = $('#chart_div');
            if(selected_user) {
                loading.show();
                chart_div.hide();

                var name = $('#selected').attr('name');
                if (name ==="mean_time"){
                    $.getJSON("/api/v1/mean_time_weekday/"+selected_user, function(result) {
                        $.each(result, function(index, value) {
                            value[1] = parseInterval(value[1]);
                        });
                        console.log(result);
                        var data = new google.visualization.DataTable();
                        data.addColumn('string', 'Weekday');
                        data.addColumn('datetime', 'Mean time (h:m:s)');
                        data.addRows(result);
                        var options = {
                            hAxis: {title: 'Weekday'}
                        };
                        var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                        formatter.format(data, 1);

                        chart_div.show();
                        loading.hide();
                        var chart = new google.visualization.ColumnChart(chart_div[0]);
                        chart.draw(data, options);
                    });                    
                }
                else if (name==="presense_weekday"){
                    $.getJSON("/api/v1/presence_weekday/"+selected_user, function(result) {
                        var data = google.visualization.arrayToDataTable(result);
                        var options = {};
                        chart_div.show();
                        loading.hide();
                        var chart = new google.visualization.PieChart(chart_div[0]);
                        chart.draw(data, options);
                    });                    
                } else {
                    $.getJSON("/api/v1/presence_start_end/"+selected_user, function(result) {
                        $.each(result, function(index, value) {
                            value[1] = parseInterval(value[1]);
                            value[2] = parseInterval(value[2]);
                        });
   
                        var data = new google.visualization.DataTable();
                        data.addColumn('string', 'Weekday');
                        data.addColumn({ type: 'datetime', id: 'Start' });
                        data.addColumn({ type: 'datetime', id: 'End' });
                        data.addRows(result);
                        var options = {
                            hAxis: {title: 'Weekday'}
                        };
                        var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                        formatter.format(data, 1);
                        formatter.format(data, 2);
                    
                        chart_div.show();
                        loading.hide();
                        var chart = new google.visualization.Timeline(chart_div[0]);
                        chart.draw(data, options);
                    });
                                    
                }
                
            }
        });
    });
})(jQuery);