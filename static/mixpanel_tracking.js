window.MixpanelTracking = (function ($) {
    function handleRSSClick(){
        mixpanel.track('RSS Header Button Clicked');
    }

    function handleFBClick(){
        mixpanel.track('FB Header Button Clicked');
    }

    function handleTwitterClick(){
        mixpanel.track('Twitter Header Button Clicked');
    }

    function handleSubscribeClick() {
        mixpanel.track('Subscribe Button Click');
    }

    return {
        init: function() {
            $('#header-rss').on('click', handleRSSClick);
            $('#header-fb').on('click', handleFBClick);
            $('#header-twitter').on('click', handleTwitterClick);
            $('#subscribe-btn').on('click', handleSubscribeClick);
        }
    };
}(jQuery));