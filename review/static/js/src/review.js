/* Javascript for ReviewXBlock. */
function ReviewXBlock(runtime, element) {
  $(function ($) {
    'use strict'

    $('.review-button').on('click', function(event) {
      var $btn = $(event.currentTarget),
          $content = $btn.siblings('.review-content'),
          $iframe = $content.find('iframe'),
          title,
          skipLink;

      if (!$btn.hasClass('disable-click')) {
        // Prevents double clicking which caused issues from seeing the problems
        $btn.addClass('disable-click');

        setTimeout(function() {
          $btn.removeClass('disable-click');
        }, 100);

        // iFrame loads after the button is clicked so there is not
        // a large amount of loading upon going to the xBlock
        if ($iframe.attr('src') === '') {
          $iframe.attr('src', $btn.data('iframe-src'));
        }


        // Prevent issues with cross-origin frames when in studio
        // (iFrames are hosted on courses.edx.org)
        if (window.location.hostname.indexOf("studio") == -1) {
          // Dynamically changes the height of the iFrame to the size of
          // the content inside. Sets the interval when the button is opened
          // and clears the interval when the button is closed
          if (!$btn.attr('class').includes('review-button--active')) {
            $btn.data('intervalID', setInterval(function() {
              $iframe.attr('height', $iframe['0'].contentWindow.document.body.offsetHeight + 'px');
            }, 1000));
          } else {
            clearInterval($btn.data('intervalID'));
          }

          // Need to wait for the iFrame to load so there is a body node
          $iframe['0'].addEventListener("load", function() {
            // Remove the 'skip to main content' link inside of an iFrame
            skipLink = $iframe['0'].contentDocument.body.querySelector('.nav-skip');
            $iframe['0'].contentDocument.body.removeChild(skipLink);
          });
        }

        // Toggle active state (+/-)
        $btn.toggleClass('review-button--active');

        // Toggle ARIA property
        // https://gist.github.com/toddmotto/bbb704d88cf39b06dbe0
        $btn.attr('aria-expanded', !$btn.attr('aria-expanded'));

        // Toggle active state (show/hide)
        $content.toggleClass('review-content--active');
      }
    });
  });
}
