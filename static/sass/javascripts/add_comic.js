window.AddComic = (function ($) {
    function facebookTextCount() {
        $('#facebook-count').text('Characters: ' + $(this).val().length);
    }

    function twitterTextCount() {
        var charsLeft = 120 - $(this).val().length;
        $('#twitter-count').text('Characters Left: ' + charsLeft);
    }

    return {
        init: function() {
            $('#id_facebook_post_message').on('keyup', facebookTextCount);
            $('#id_twitter_post_message').on('keyup', twitterTextCount);
        }
    };
}(jQuery));