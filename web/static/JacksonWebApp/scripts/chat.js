(function($) {
    var CHAT_ENDPOINT = '/jackson/chat/',
        sendButton = $('#chat_btn_send'),
        chatLogContainer = $('#chat_chat_log'),
        inputField = $('#chat_user_input'),
        row = $('<div class="row"></div>'),
        input = $('<div class="pull-right"></div>'),
        output = $('<div></div>'),
        ENTER = 13;

    $('nav-index').removeClass("active");
    $('nav-chat').addClass("active");

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }

        return cookieValue;
    }

    function sendRequest(inputText) {
        $('#img-think-bubble').css('display', 'block');
        $.ajax({
            url: CHAT_ENDPOINT,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                user_input: inputText,
            })
        })
        .done(function(result) {
            showMessage(result.answer, false);
            $('#img-think-bubble').css('display', 'none');
        });
    }

    function showMessage(text, messageIsFromUser = true) {
        var newRow = row.clone();
        if (messageIsFromUser) {
            var inputBox = input.clone().text(text);
            newRow
                .addClass('chat_user_input')
                .append(inputBox);
        } else {
            var outputBox = output.clone().text(text);
            newRow
                .addClass('chatbot_output')
                .append(outputBox);
        }

        newRow.hide();

        chatLogContainer.append(newRow);
        newRow.fadeIn("slow");

        if(chatLogContainer.length)
        chatLogContainer.scrollTop(chatLogContainer[0].scrollHeight - chatLogContainer.height());
    }

    var csrfToken = getCookie('csrftoken') || $(":input[name='csrfmiddlewaretoken']").val();

    $(document).keypress(function(e) {
        if(e.which == ENTER) {
            var inputText = inputField.val();
            showMessage(inputText);
            sendRequest(inputText);
            inputField.val('');
        }
    });

    sendButton.on('click', function(event) {
        event.preventDefault();

        var inputText = inputField.val();
        showMessage(inputText);
        sendRequest(inputText);
        inputField.val('');
    });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrfToken);
        }
    });
})(jQuery)
