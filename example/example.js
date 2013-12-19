/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

var wsUri = 'ws://localhost:8844/';
var bmoRestUrl = 'http://localhost:8080/bmo/rest';
var websocket;

function init() {
  $('#subscribeform').submit(function() {
    subscribe($('#bug').val());
    $('#bug').val('');
    return false;
  });
  showDisconnected();
  connect(wsUri);
}

function connect(uri) {
  clearError();
  websocket = new WebSocket(wsUri);
  websocket.onopen = function(evt) { onOpen(evt); };
  websocket.onclose = function(evt) { onClose(evt); };
  websocket.onmessage = function(evt) { onMessage(evt); };
  websocket.onerror = function(evt) { onError(evt); };
}

function onOpen(evt) {
  clearError();
  showConnected();
  getVersion();
  getSubscriptions();
}

function onClose(evt) {
  var error = '';
  if (evt.code == 1006) {
    error = 'connection abnormally terminated';
  } else if (evt.code != 1000 && evt.code != 1005) {
    error = 'unknown error (' + evt.code + ')';
  }
  displayError(error);
  showDisconnected();
}

function onMessage(evt) {
  var msg = JSON.parse(evt.data);
  clearError();
  if (msg.error) {
    displayError(msg.error);
  }
  if (msg.command == 'version') {
    $('#bugzfeed').text('Bugzfeed version ' + msg.version + '.');
  } else if (msg.command == 'update') {
    getChanges(msg);
  } else if (msg.command == 'subscriptions' || msg.command == 'subscribe' ||
             msg.command == 'unsubscribe') {
    displaySubscriptions(msg);
  }
}

function onError(evt) {
  displayError(evt.data);
}

function doSend(message) {
  websocket.send(message);
}

function clearError(err) {
  $('#error').text('');
}

function displayError(err) {
  $('#error').text(err);
}

function findHistoryEntry(when, history, field) {
  for (var i = 0; i < history.length; i++) {
    if (history[i][field].slice(0, history[i][field].length-1) == when) {
      return history[i];
    }
  }
  return null;
}

function updateHtml(who, change) {
  var changes = [];
  if (change.removed) {
    changes.push('removed ' + change.removed);
  }
  if (change.added) {
    changes.push('added ' + change.added);
  }
  return '<li>' + who + ': ' + change.field_name + ': ' + changes.join(', ');
}

function commentHtml(comment) {
  return '<li>' + comment.author + ': comment: ' + comment.text;
}

function attachmentHtml(attachment) {
  var html = '<li>' + attachment.attacher + ': attachment ' + attachment.id +
        ' (' + attachment.description + ')';
  // Work around bug 937180.
  if (attachment.last_change_time.slice(0, 16) ==
      attachment.creation_time.slice(0, 16)) {
    html += ' created';
  } else {
    html += ' modified';
  }
  return html;
}

function getChanges(msg) {
  $('#feed').append('bug ' + msg.bug + ' changed at ' + msg.when + ':<br/>');
  var updates = $('<ul></ul>');
  $('#feed').append(updates);

  var bugUrl = bmoRestUrl + '/bug/' + msg.bug;
  // new_since argument expects one second *before*...blech.
  // Should be fixed with new unified history API call.

  $.getJSON(bugUrl + '/history?include_fields=when,who', function(data) {
    var history = findHistoryEntry(msg.when, data.bugs[0].history, 'when');
    if (!history) {
      return;
    }
    for (var j = 0; j < history.changes.length; j++) {
      var change = history.changes[j];
      updates.html(updates.html() + updateHtml(history.who, change));
    }
  });

  $.getJSON(bugUrl + '/comment?include_fields=author,text,time', function(data) {
    var comment = findHistoryEntry(msg.when, data.bugs[msg.bug].comments,
                                   'time');
    if (!comment) {
      return;
    }
    updates.html(updates.html() + commentHtml(comment));
  });

  $.getJSON(bugUrl + '/attachment?include_fields=attacher,creation_time,'
            + 'description,id,last_change_time', function(data) {
    var attachment = findHistoryEntry(msg.when, data.bugs[msg.bug],
                                      'last_change_time');
    if (!attachment) {
      return;
    }
    updates.html(updates.html() + attachmentHtml(attachment));
  });
}

function showConnected() {
  $('#connection').html('Connected. <button id="disconnect">disconnect</button>');
  $('#disconnect').click(function() { websocket.close(); });
  $('#controlscontainer').show();
}

function showDisconnected() {
  $('#controlscontainer').hide();
  $('#bugzfeed').text('');
  $('#feed').text('');
  $('#connection').html('Disconnected. <button id="connect">connect</button>');
  $('#connect').click(function() { connect(wsUri); });
}

function getVersion() {
  doSend('{"command": "version"}');
}

function getSubscriptions() {
  doSend('{"command": "subscriptions"}');
}

function displaySubscriptions(msg) {
  if (msg.bugs === undefined) {
    return;
  }
  $('#subscriptions').text('');
  if (msg.bugs.length == 0) {
    $('#subscriptions').text('None');
  } else {
    var button;
    for (var i = 0; i < msg.bugs.length; i++) {
      button = $('<button id="del' + msg.bugs[i] + '">X</button>');
      button.click(function() { unsubscribe($(this).attr('id').slice(3)); });
      $('#subscriptions').append(button);
      $('#subscriptions').append(' ' + msg.bugs[i] + '<br/>');
    }
  }
}

function subscribe(bug) {
  doSend(JSON.stringify({command: "subscribe", bug: bug}));
}

function unsubscribe(bug) {
  doSend(JSON.stringify({command: 'unsubscribe', bug: bug}));
}

window.addEventListener("load", init, false);
