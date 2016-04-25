function teamportal(teamemail){
    $.fn.dataTable.moment( 'dddd, MMMM Do, YYYY, hh:mm A' );
    var inject_table = $('#injects').DataTable( {
        "ajax": "/injects/api/list/" + teamemail,
        "order": [[ 2, "desc" ]]
    });
    $('#injects tbody').on('click', '#inject_submit', function () {
        var rowiter = $('td:first', $(this).parents('tr'));
        var id = rowiter.text();
        var name = rowiter.next().text();
        $('.inject-modal-title').html("Submit Inject: " + name);
        if ($(this).text() == "Manual"){
            $(".inject-modal-warning").html("WHITE TEAM MUST CHECK THIS BEFORE THE END TIME FOR YOU TO GET ANY CREDIT");
        } else {
            $(".inject-modal-warning").html("");
        }
        $('#injectid').val(id);
        $('#inject-modal').modal('toggle');
    });
    sub_table = $('#submissions').DataTable( {
        "paging": false,
        "order": [[ 0, "desc" ]],
        "bAutoWidth": false
    } );
    $('#injects tbody').on('click', '#sub_view', function () {
        var rowiter = $('td:first', $(this).parents('tr'));
        var id = rowiter.text();
        var name = rowiter.next().text();
        $('.sub-modal-title').html("Submissions: " + name);
        sub_table.ajax.url("/injects/api/submissions/" + teamemail + "/" + id);
        sub_table.ajax.reload(null, false);
        $('#sub-modal').modal('toggle');
    });
    $('#submissions tbody').on('click', '[id^=sub_delete]', function (e) {
        var id = $(this).attr('id').split("-")[1];
        if (!confirm("Are you sure you want to delete this submission?")){
            return;
        }
        $.ajax({
            url: '/injects/api/submissions/delete/' + id,
            type: 'GET'
        });
        sub_table.ajax.reload(null, false);
    });
    update_announcements();
    setInterval( function () { inject_table.ajax.reload(null, false); }, 2000);
    setInterval( update_announcements, 20000);
}

function update_announcements() {
    $.ajax({
        url: '/api/announcements',
        type: 'GET',
        dataType: 'json',
        contentType: "application/json",
        success: function(data, stat, xhr){
            $('#announcements').html("");
            $.each(data, function(i, ann){
                $('#announcements').append("<li>" + ann + "</li>")
            });
        }
    });
}
