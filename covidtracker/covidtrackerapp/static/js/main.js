var updateInterval = null;
var tracking = false;
var proceed = true;
var submit = false;

var submitName;

var rBtnState = 'I HAVE TESTED POSITIVE FOR COVID-19+background-color:red; color:white; width:25vw';
var lBtnState = "I'M SICK+background-color:red; color:white; width:25vw";

var sickcheck = false;
var positivecheck = false;

function redirect(resource){
  window.location = resource;
}

function positionReceived(position){
  if(proceed){
    if(updateInterval == null){
      updateInterval = setInterval(
        function(){
          navigator.geolocation.getCurrentPosition(positionReceived, error);
        }, 1000
      );
    }
    if(tracking){
    proceed = false;
    $.ajax({
      type:'POST',
      url:'/update/',
      data:{
        csrfmiddlewaretoken:document.cookie.substring(10),
        'lat' : position.coords.latitude,
        'long' : position.coords.longitude
      },
      success: function(){
        proceed = true;
      }
    });
  }
}
}

function error(){
  stopTracker();
  alert('Please enable location services in order to use the tracker');
}

function initiateTracker(){
  tracking = true;
  proceed = true;
  if(navigator.geolocation){
    document.getElementById('track-btn').innerHTML = 'STOP TRACKING';
    $.ajax({
      type:'POST',
      url:'/initiate/',
      data:{csrfmiddlewaretoken:document.cookie.substring(10)},
      success: function(){
        navigator.geolocation.getCurrentPosition(positionReceived, error);
      }
    });
  } else {
    alert("Unfortunately, location services are unavailable on this browser.");
  }
}

function toggleTracker(){
  if(!tracking){
    initiateTracker();
  } else {
    stopTracker();
  }
}

function stopTracker(){
  tracking = false;
  clearInterval(updateInterval);
  updateInterval = null;
  document.getElementById('track-btn').innerHTML = 'START TRACKING';
  $.ajax({
    type:'POST',
    url:'/suspend/',
    data:{csrfmiddlewaretoken:document.cookie.substring(10)},
  });
}

function setDeclareOptions(sick, positive){
  submit = false;
  var data;
  data = positive.split("+");

  if(data[0] == '1'){
    positivecheck = true;


      if(Date.now()/1000 - parseInt(data[1]) > 1728000){
        rBtnState = "I NO LONGER CARRY COVID-19" + "+" + rBtnState;
        document.getElementById('right-action-btn').innerHTML = rBtnState.split("+")[0];
      } else {
        rBtnState = "YOU'VE TESTED POSITIVE FOR COVID-19! WAIT " + timeNotation(1728000 - (Date.now()/1000 - parseInt(data[1]))) + " TO UPDATE YOUR STATUS" + "+" + 'background-color:transparent; color:red; width:30vw; border-style:solid; border-color:red;';
        document.getElementById('right-action-btn').style = rBtnState.split("+")[1];
        document.getElementById('right-action-btn').innerHTML = rBtnState.split("+")[0];
      }
      return;
  }
  document.getElementById('left-action-btn').style.visibility = 'visible';
  data = sick.split("+");
  if(data[0] == '1'){
    sickcheck = true;

    if(Date.now()/1000 - parseInt(data[1]) > 432000){
      lBtnState = "I'M NO LONGER SICK" + "+" + lBtnState;
      document.getElementById('left-action-btn').innerHTML = lBtnState.split("+")[0];
    } else {
      lBtnState = 'YOU ARE SICK! WAIT ' + timeNotation(432000 - (Date.now()/1000 - parseInt(data[1]))) + ' TO UPDATE YOUR STATUS' + "+" + 'background-color:transparent; color:red; width:30vw; border-style:solid; border-color:red;';
      document.getElementById('left-action-btn').style = lBtnState.split("+")[1];
      document.getElementById('left-action-btn').innerHTML = lBtnState.split("+")[0];
    }
  }
}

function timeNotation(time){
  var lbltext = 'seconds'
  var lbl = 0;
  while(time > 60){
      switch(lbl){
        case 0:
          time = Math.round(time/60);
          lbltext = 'minutes';
          break;
        case 1:
          time = Math.round(time/60);
          lbltext = 'hours';
          break;
        case 2:
          time = Math.round(time/24);
          lbltext = 'days';
          break;
        case 3:
          time = Math.round(time/30);
          lbltext = 'months';
          break;
        case 4:
          time = Math.round(time/12);
          lbltext = 'years';
          break;
        }
      lbl++;
  }
  return time.toString() + " " + lbltext;
}

function fillList(contacted, health){
  var elements = [];
  for(var idx = 0; idx < contacted.length; idx++){
    if(contacted[idx] == '0'){
      continue;
    }
    var data = contacted[idx].split("+");
    var time = Math.round(Date.now()/1000 - parseInt(data[2]));
    var timeRaw = time;

    time = timeNotation(time);

    lat = (parseFloat(data[0])/(2*Math.PI)) * 360;
    long = (parseFloat(data[1])/(2*Math.PI)) * 360;

    var insert = "<li style = 'color:white';> Contact detected " + time + ' ago. ' + '<a style = "color:#ffff00" target="_blank" href = https://www.google.com/maps/place/' + lat + ',' + long + '> Click here for approximate location of contact.</a>';

    switch(health[idx]){
      case 0:
        insert += '<strong> This person reports that they are healthy</strong>';
        break;
      case 1:
        insert += '<strong> This person reports that they are under the weather</strong>';
        break;
      case 2:
        insert += '<strong> This person reports that they have tested positive for COVID-19</strong>';
        break;
    }
    insert += '</li>\n';
    insert = timeRaw + '+' + insert;

    insertListElem(elements, insert);
  }
  var res = "";

  for(var idx = 0; idx < elements.length; idx++){
    res += elements[idx].split("+")[1];
  }
  if(res == ""){
    res = '<li style = "color:white";>No contacts detected</li>';
  }
  document.getElementById('contact-list').innerHTML = res;
}

function handleClaim(btn){

  if(btn == 'right'){
    if(document.getElementById('right-action-btn').innerHTML == 'CANCEL'){

      document.getElementById('warning').style.visibility = 'hidden';
      document.getElementById('right-action-btn').style = rBtnState.split("+")[1];
      document.getElementById('right-action-btn').innerHTML = rBtnState.split("+")[0];

      document.getElementById('left-action-btn').style = lBtnState.split("+")[1];
      document.getElementById('left-action-btn').innerHTML = lBtnState.split("+")[0];
    } else {

      submitName = 'positive'
      if(positivecheck){
        document.getElementById('right-action-btn').name = submitName;
        submit = true;
      } else {
        promptConfirm(20);
      }
    }
  } else {

    if(document.getElementById('left-action-btn').innerHTML == 'CONFIRM'){
      submit = true;
    } else {
      submitName = 'sick';
      if(sickcheck){
        document.getElementById('left-action-btn').name = submitName;
        submit = true;
      } else {
        promptConfirm(5);
      }
    }
  }
}

function promptConfirm(duration){

  document.getElementById('warning').innerHTML = 'Are you sure? Users who came in contact with you will be notified with your health update and email. You will not be able to update your status for ' + duration + ' days';
  document.getElementById('warning').style.visibility = 'visible';
  document.getElementById('left-action-btn').name = submitName;
  document.getElementById('right-action-btn').style = "background-color:red; color:white; width:15vw";
  document.getElementById('right-action-btn').innerHTML = "CANCEL";
  document.getElementById('left-action-btn').style = "background-color:red; color:white; width:15vw";
  document.getElementById('left-action-btn').innerHTML = "CONFIRM";
}

function checkSubmit(){
  return submit;
}

function insertListElem(arr, insert){

  if(arr.length == 0){
    arr[0] = insert;
    return;
  }

  var lo = 0
  var hi = arr.length - 1;

  var mid = -1
  while(lo <= hi){
    var mid = (lo+hi)/2;
    if(parseInt(arr[mid].split("+")[0]) < parseInt(insert.split("+")[0])){
        lo = mid+1;
    } else {
        hi = mid-1;
    }
  }

  if(parseInt(arr[mid].split("+")[0]) > parseInt(insert.split("+")[0])){
    arr.splice(mid, 0, insert);
  } else {
    arr.splice(mid+1, 0, insert);
  }
}
