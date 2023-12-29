var ACCOUNTS = ["m"];
import React from 'react'
window.ga=window.ga||function(){(ga.q=ga.q||[]).push(arguments)};ga.l=+new Date;

  var consentCookie = getCookie('CookieConsent');

  if (consentCookie) {
    var hasConsent = Market.Helpers.CookieConsent.given('statistics');

    if (hasConsent) {
      setupGoogleAnalytics();
      loadGoogleAnalytics();
      loadClickTracker();
      loadLinkingForAllAccounts();
    }
  } else {
    setupGoogleAnalytics();
    loadGoogleAnalytics();
    loadClickTracker();
    loadLinkingForAllAccounts();
  }

  window.addEventListener('CookiebotOnAccept', handleCookiebotAcceptDeclineEvent, false);
  window.addEventListener('CookiebotOnDecline', handleCookiebotAcceptDeclineEvent, false);
removeOldExperimentCookies();
trimGacUaCookies();

function removeOldExperimentCookies() {
  let cookies = document.cookie.split('; ');
  for (let i in cookies) {
    let [cookieName, cookieVal] = cookies[i].split('=', 2);
    if (cookieName.startsWith('market_experiment_')) {
      $.removeCookie(cookieName, { path: '/', domain: '.' + window.location.host });
    }
  }
}

function trimGacUaCookies() {
  // Trim the list of gac cookies and only leave the most recent ones. This
  // prevents rejecting the request later on when the cookie size grows larger
  // than nginx buffers.
  let maxCookies = 15;
  var gacCookies = [];

  let cookies = document.cookie.split('; ');
  for (let i in cookies) {
    let [cookieName, cookieVal] = cookies[i].split('=', 2);
    if (cookieName.startsWith('_gac_UA')) {
      gacCookies.push([cookieName, cookieVal]);
    }
  }

  if (gacCookies.length <= maxCookies)
    return;

  gacCookies.sort((a, b) => { return (a[1] > b[1] ? -1 : 1); });

  for (let i in gacCookies) {
    if (i < maxCookies) continue;
    $.removeCookie(gacCookies[i][0], { path: '/', domain: '.' + window.location.host });
  }
}

function handleCookiebotAcceptDeclineEvent() {
  if (Cookiebot.consent.statistics) {
    if (!(window.ga && ga.create)) {
      setupGoogleAnalytics();
      loadGoogleAnalytics();
      loadClickTracker();
      loadLinkingForAllAccounts();
    }
  } else {
    unloadGoogleAnalytics()
  }

  if (!consentToExperimentsEnrollmentGiven()) {
    unenrollFromExperiments();
  }
}

function getCookie(name) {
  var name = name + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var cookieContent = decodedCookie.split(';');

  for(var i = 0; i <cookieContent.length; i++) {
    var c = cookieContent[i];

    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }

    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }

  return false;
}

function delete_cookie_by_name(name) {
  document.cookie = name + "=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
}

function unloadGoogleAnalytics() {
  var payload = {"name":"m","allowLinker":true};
  var accountId = "UA-11834194-7";

  // Set the GA User Opt-out flag
  window['ga-disable-'+accountId] = true;

  // Do not explicitly make any further calls to ga()
  ga(payload.name+".remove");

  // Delete any existing GA cookies (_ga, _gat & _gaid) and GA Client ID from localStorage
  delete_cookie_by_name('_ga');
  delete_cookie_by_name('_gat');
  delete_cookie_by_name('_gid');

  // Delete LocalStorage Entries
  if (Market.Helpers.GaLsUtils.localStorageAvailable()) {
    var clientId = Market.Helpers.GaLsUtils.getClientId();

    if (!clientId) {
      return;
    }

    Market.Helpers.GaLsUtils.removeClientId();
  }

    // Do not transmit the Client ID to other sites upon navigation (i.e. autoLink)
  }

  function domLoaded() {
    return new Promise(resolve => {
      if (
        document.readyState === 'interactive' ||
        document.readyState === 'complete'
      ) {
        resolve()
      } else {
        document.addEventListener(
          'DOMContentLoaded',
          () => {
            resolve()
          },
          {
            capture: true,
            once: true,
            passive: true
          }
        )
      }
    })
  }

  function consentToExperimentsEnrollmentGiven () {
    return Market.Helpers.CookieConsent.given('preferences') && Market.Helpers.CookieConsent.given('statistics');
  }

  function unenrollFromExperiments() {
    var experimentCookieNames = [
      'market_experiments',
      'mk_ex',
      'meqc',
      'meqc2',
      'meqc3'
    ]

    var deletedCookies = [];

    _.each(experimentCookieNames, function(cookieName) {
      if ($.cookie(cookieName)) {
        $.removeCookie(cookieName, { path: '/', domain: '.' + window.location.host });
        deletedCookies.push(cookieName);
      }
    });
    for (var i = 0; i < ACCOUNTS.length; i++) {
      var t = ACCOUNTS[i];
      if(deletedCookies.length > 0) {
        ga(t+'.set', "exp", null);
        ga(t+'.set', "dimension21", null);
        ga(t+'.set', "dimension22", null);
      }
    }
  }

  function setExperimentEnrollments(experimentEnrolmentsDataString) {
    for (var i = 0; i < ACCOUNTS.length; i++) {
      var t = ACCOUNTS[i];
      var cookieValue = $.cookie('mk_ex');
      if (cookieValue && cookieValue.replace(/\*/g, '!') === experimentEnrolmentsDataString) {
        ga(t+'.set', "exp", experimentEnrolmentsDataString);
        ga(t+'.set', "dimension21", experimentEnrolmentsDataString);
        ga(t+'.set', "dimension22", experimentEnrolmentsDataString);
      } else {
        ga(t+'.set', "exp", null);
        ga(t+'.set', "dimension21", null);
        ga(t+'.set', "dimension22", null);
      }
    }
  }

  function loadLinkingForAllAccounts() {
    domLoaded().then(() => {
      window._envGaTrackerNames = ACCOUNTS;

      for (var i = 0; i < ACCOUNTS.length; i++) {
        var t = ACCOUNTS[i];

        ga(t+'.require', 'linker');

        ga(t+'.require', 'linkid', 'linkid.js');
      };

      document.body.addEventListener('click', function(event) {
        decorateLink(event);
      });
      document.body.addEventListener('contextmenu', function(event) {
        // Aside from a normal click, we need to handle the variety of ways users
        // can open a link in a new tab
        // Right click to open context menu
        decorateLink(event);
      });
      document.body.addEventListener('mousedown', function(event) {
        // Aside from a normal click, we need to handle the variety of ways users
        // can open a link in a new tab
        // Middle mouse button click
        if (event.button === 1) {
          decorateLink(event);
        }
      });
    });
  }

  function decorateLink(event) {

    window._envGaTrackerNames = ACCOUNTS;

    var currentTarget = jQuery(event.target);
    var link = currentTarget.closest('a')[0];
    var ourDomains = ["audiojungle.net","themeforest.net","videohive.net","graphicriver.net","3docean.net","codecanyon.net","photodune.net","market.styleguide.envato.com","elements.envato.com","build.envatohostedservices.com","author.envato.com","tutsplus.com","sites.envato.com","account.envato.com","forums.envato.com"];
    var filteredDomains = ourDomains.filter(function(domain) {
      return domain !== document.location.hostname;
    });

    for (var i = 0; i < ACCOUNTS.length; i++) {
      var t = ACCOUNTS[i];

      if (link && link.href) {
        if (filteredDomains.includes(link.hostname) || currentSiteLinkOpensInNewWindow(link)) {
          ga(t+'.linker:decorate', link)
        }
      }
    }
  }

  function currentSiteLinkOpensInNewWindow(link) {
    return document.location.hostname === link.hostname && link.target === '_blank';
  }

  function setupGoogleAnalytics() {
    (function () {
      var accountId = "UA-11834194-7";
      window['ga-disable-'+accountId] = false;

      var options = {"name":"m","allowLinker":true};

      if (Market.Helpers.GaLsUtils.localStorageAvailable()) {
        if (Market.Helpers.GaLsUtils.clientIdNotPresent()) {
          options.clientId = Market.Helpers.GaLsUtils.retrieveClientId();
        }

        ga("create", accountId, options);
        ga(function() {
          var tracker = ga.getByName(options.name);
          Market.Helpers.GaLsUtils.storeClientId(tracker.get('clientId'));
          for (var i = 0; i < ACCOUNTS.length; i++) {
            var t = ACCOUNTS[i];
            ga(t+'.set', 'dimension18', Market.Helpers.GaLsUtils.retrieveClientId())
          }
        })
      } else {
        ga("create", accountId, options);
      }

      window._envGaTrackerNames = ACCOUNTS;

      for (var i = 0; i < ACCOUNTS.length; i++) {
        var t = ACCOUNTS[i];

        ga(t+'.require', "GTM-5VPWWP");

        ga(t+'.require', 'ec');

        ga(t+'.require', 'displayfeatures');

        ga(t+'.set', 'dimension20', 'other')

        var itemPageIdMatch = window.location.pathname.match(/^\/item\/[a-z-]+\/(?:reviews\/)?(\d+)(?:\/comments|\/support)?$/);
        if (itemPageIdMatch) {
          // Fetch item ID from path
          var itemId = itemPageIdMatch[1];
          ga(t+'.set', 'dimension23', itemId);
        }



        if (!getCookie('CookieConsent') || consentToExperimentsEnrollmentGiven()) {
          var experimentEnrolmentsDataString = ""
          setExperimentEnrollments(experimentEnrolmentsDataString);
        }

          if ('') {
            ga(t+'.send', {
              hitType: 'pageview',
              page: ''
            });
          } else if ('') {
            // append the analytics_suffix to the page path so the flash alert/error type can be tracked
            var analyticsSuffix = $.trim('').replace(/([A-Z])/g, '$1').replace(/[-_\s]+/g, '-').toLowerCase();
            var url = new URL(window.location.pathname + window.location.search, 'https://localhost');
            url.pathname += '/' + analyticsSuffix;
            var tracking_path = url.pathname + url.search;
            ga(t+'.send', {
              hitType: 'pageview',
              page: tracking_path,
            });
          } else {
            ga(t+'.send', 'pageview');
          }
      }

      loadLinkingForAllAccounts()
    }());
  }

  function loadGoogleAnalytics() {
    (function () {

      var s=document.createElement('script');
      s.type='text/javascript';
      s.async=true;
        s.src='https://www.google-analytics.com/analytics.js';
      var x=document.getElementsByTagName('script')[0];
      x.parentNode.insertBefore(s,x);
    }());
  }

  function loadClickTracker() {
    $('body').click( function (e) {
      sendStandardEvent(e.target, { eventType: 'click' });
    });
  }

  
    var accountId = "UA-48547564-1";

    var options = {
      name: "author_analytics",
      allowLinker: true,
      alwaysSendReferrer: true,
      cookieDomain: "auto",
    };

    if (Market.Helpers.GaLsUtils.localStorageAvailable()) {
      if (Market.Helpers.GaLsUtils.clientIdNotPresent()) {
        options.clientId = Market.Helpers.GaLsUtils.retrieveClientId();
      }

      ga("create", accountId, options);
    } else {
      ga("create", accountId, options);
    }


      ga("author_analytics.send", "pageview");



