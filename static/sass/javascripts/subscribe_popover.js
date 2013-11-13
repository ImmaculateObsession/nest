window.SubscribePopover = (function ($) {
    function handleSubscription() {
        $('#subscribe-btn').popover('hide');
        $('#popover-action').removeClass('fa fa-times').addClass('caret');
        $('#mc-embedded-subscribe-form').submit();
    }

    function handleSubscribeOpen() {
        $('#popover-action').toggleClass('caret').toggleClass('fa fa-times');
        $("#subscribe-btn").popover();
        $('#subscribe-submit-btn').on('click', handleSubscription);
    }

    return {
        init: function() {
            var $popover = $("#subscribe-btn").popover({
            title: 'Sign up for weekly updates!',
            html: 'true',
            placement: 'bottom',
            content: '<form action="http://inkpebble.us3.list-manage1.com/subscribe/post?u=0591f32c13358b969bde9f7c9&amp;id=274876cee0" method="post" id="mc-embedded-subscribe-form" name="mc-embedded-subscribe-form" class="validate" target="_blank" novalidate>\
                <div class="form-group">\
                <input type="email" value="" name="EMAIL" class="email form-control" id="mce-EMAIL" placeholder="email address" required>\
                </div>\
                </form>\
                <button id="subscribe-submit-btn" class="btn btn-default">Get weekly updates!</button>'
            });
            $('#subscribe-btn').on('click', handleSubscribeOpen);
        }
    };
}(jQuery));
