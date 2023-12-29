if (typeof Cookiebot !== 'undefined' && Cookiebot.consent && Cookiebot.consent.statistics ) {
    enableGoogleAnalyticsLinkWrapper();
  } else {
    window.addEventListener('CookiebotOnAccept', function (e) {
      if (Cookiebot.consent.statistics) {
        enableGoogleAnalyticsLinkWrapper();
      }
    }, false);
  }

function enableGoogleAnalyticsLinkWrapper() {
  // GA: universal analytics link wrapper
  (function(){
      window._envTrkrs = [["m", "UA-11834194-7"]];

      var debug = false;
      var MAX_RETRIES = 10;

      /*
         The script needs to wait until the Analytics script
         has been downloaded from Google before initializing
      */
      var waitForAnalytics = function(){
          this.count = this.count || 0;

          if (window.ga && ga.getByName) {
              e.init();
          } else {
              if (count < MAX_RETRIES) { setTimeout(waitForAnalytics, 250); }
              count++;
          }
      };

      var e = {
          _envArray: [],
          _envTrkrs: (window._envTrkrsCust && window._envTrkrsCust.length) ? window._envTrkrs.concat(window._envTrkrsCust) : window._envTrkrs,
          init: function() {
              for (var i=0; i < _envTrkrs.length; i++) {
                  var name = _envTrkrs[i][0];

                  if (!ga.getByName(name)) {
                      var accountId = _envTrkrs[i][1];

                      var options = {
                          name: name,
                          allowLinker: true,
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
                  }
              }

              document.addEventListener('DOMContentLoaded', function(){
                  e.wrapperInit();
              });

              if (debug) {console.log('Initiated');}
          },
          wrapperInit: function() {
              if (typeof window._envIsRunning != 'undefined' || window._envIsRunning == true) {
                  return
              }
              window._envIsRunning = true;

              if (document.addEventListener) {
                  document.addEventListener('click', function(event){
                      var target = event.target;
                      if (target && target.tagName === 'A') {
                          e._envLinksTracker(event);
                      }
                  });
              }
          },
          isInArray: function(e, t) {
              for (var n = 0; n < t.length; n++) {
                  var r = new RegExp(t[n], 'i');
                  if (r.test(e)) {
                      return n
                  }
              }
              return -1
          },
          _envTrackevent: function(e, t, n, r) {
              for (var i = 0; i < this._envTrkrs.length; i++) {
                  var s = this._envTrkrs[i][0].length == 0 ? '' : this._envTrkrs[i][0] + '.';
                  r.length == 0 ? ga(s + 'send', 'event', e, t, n) : ga(s + 'send', 'event', e, t, n, r)
              }
          },
          _envTrackpageview: function(e, t) {
              t = t.charAt(0) == '/' ? t : '/' + t;
              for (var n = 0; n < this._envTrkrs.length; n++) {
                  var r = this._envTrkrs[n][0].length == 0 ? '' : this._envTrkrs[n][0] + '.';
                  ga(r + 'send', 'pageview', e + t);
              }
          },
          _envLinksTracker: function(t) {
              var r = false;
              var i = {
                  outbound: {
                      run: true,
                      useEvent: true
                  },
                  download: {
                      run: true,
                      useEvent: true,
                      reg: ''
                  },
                  self: {
                      run: false,
                      useEvent: true
                  },
                  mail: {
                      run: true,
                      useEvent: true
                  },
                  ext: /\.(doc.?|xls.?|ppt.?|exe|zip|rar|gz|tar|tgz|dmg|csv|pdf|xpi|txt|mp3)$/i
              };
              var s = t.srcElement ? t.srcElement : this;
              if (t.srcElement) {
                  r = true
              }
              while (s.tagName != 'A') {
                  s = s.parentNode
              }
              if (s.href == undefined || s.href == null) {
                  return true
              }
              var o = s.href;
              if (o.length == 0) return;
              var u = s.hostname.toLowerCase();
              var a = s.pathname;
              if (a.length == 0) {
                  a = '/'
              } else if (a.substr(0, 1) != '/') {
                  a = '/' + a
              }
              var f = s.protocol;
              var l = s.search;
              var c = location.hostname;
              c = c.replace(/^www\./i, '').toLowerCase();
              u = u.replace(/^www\./i, '').toLowerCase();
              if (o.match(/^#/)) {
                  if (i.self.run) {
                      i.self.useEvent ? e._envTrackevent('self', 'click - ' + c, o, '') : e._envTrackpageview('/virtual/self', '/' + o);
                      return true
                  }
              } else if (f.match(/^mailto:/i)) {
                  if (i.mail.run) {
                      o = o.replace(/^mailto:/i, '');
                      i.mail.useEvent ? e._envTrackevent('mailto', 'click - ' + c, o, '') : e._envTrackpageview('/virtual/mailto', o);
                      return true
                  }
              } else if ((new RegExp(i.ext)).test(a)) {
                  if (i.download.run) {
                      o = o.replace(/^https?:\/\//i, '');
                      i.download.useEvent ? e._envTrackevent('download', 'click - ' + c, o, '') : e._envTrackpageview('/virtual/download', o);
                      return true
                  }
              } else if (u == undefined || u.length == 0 || f.match(/^javascript:/i)) {
                  return
              } else if ((new RegExp(c + '$', 'i')).test(u) || (new RegExp(u + '$', 'i')).test(c)) {
                  if (i.download.run && i.download.reg.length != 0) {
                      if ((new RegExp(i.download.reg, 'i')).test(a + l)) {
                          o = o.replace(/^https?:\/\//i, '');
                          i.download.useEvent ? e._envTrackevent('download', 'click - ' + c, o, '') : e._envTrackpageview('/virtual/download', o);
                          return true
                      }
                  }
              } else if (u != c) {
                  if (e.isInArray(u, e._envArray) == -1) {
                      if (i.outbound.run) {
                          i.outbound.useEvent ? e._envTrackevent('outbound', 'click - ' + c, u + a + l, '') : e._envTrackpageview('/virtual/outbound', u + a);
                          return true
                      }
                  } else if (e.isInArray(u, e._envArray) != -1) {
                      var h = s.target;
                      if (h != null && h == '_blank') {
                          if ((new RegExp(/_utma=/)).test(l)) {
                              return true
                          }
                          var p = e._envTrkrs[0][0].length == 0 ? '' : _envTrkrs[0][0] + '.';
                          return true
                      } else {
                          return false
                      }
                  }
              }
          }
      };

      waitForAnalytics();
  })()
}
