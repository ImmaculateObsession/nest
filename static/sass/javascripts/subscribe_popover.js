window.SubscribePopover = (function ($) {
    function handleSubscription() {
        $('#subscribe-btn').popover('hide');
        $('#popover-action').removeClass('fa fa-times').addClass('caret');
    }

    function handleSubscribeOpen() {
        $('#popover-action').toggleClass('caret').toggleClass('fa fa-times');
        $("#subscribe-btn").popover();
        $('#popover-subscription-form').on('submit', handleSubscription);
    }

    return {
        init: function() {
            var $popover = $("#subscribe-btn").popover({
            title: 'Sign up for weekly updates!',
            html: 'true',
            placement: 'bottom',
            content: '<form action="http://inkpebble.us3.list-manage1.com/subscribe/post?u=0591f32c13358b969bde9f7c9&amp;id=274876cee0" method="post" id="popover-subscription-form" name="mc-embedded-subscribe-form" class="validate" target="_blank" novalidate>\
                <div class="form-group">\
                <input type="email" value="" name="EMAIL" class="email form-control" id="mce-EMAIL" placeholder="email address" required>\
                </div>\
                <input type="submit" value="Get weekly updates!" name="subscribe" id="mc-embedded-subscribe" class="btn btn-default">\
                </form>'
            });
            $('#subscribe-btn').on('click', handleSubscribeOpen);
        }
    };
}(jQuery));
