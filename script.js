function loadData() {

}

function safetyNav() {
    window.open('safety.html', '_top');
}

function activityNav() {
    window.open('activity.html', '_top');
}

function mapNav() {
    window.open('map.html', '_top');
}

function openLogin() {
    window.open('entry.html', '_top');
}

function openProfileCreation() {
    window.open('profileCreation.html', '_top');
}

function initMap() {
    
    // get user location 
    var userLocation = {lat: 0, lng: 0};

    // place marker
    var map = new google.maps.Map(document.getElementById('map'), {zoom: 4, center: userLocation});    
    var marker = new google.maps.Marker({position: userLocation, map: map});
}

// async script add to allow site-content to load while maps API is fetched 
let script = document.createElement('script');

//smth wrong with my API key I'll fix later
script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyC5M3-cQQxqkSBfaGxb-PvulpHiyxo6hEM&callback=initMap";
document.body.append(script);


//loads list of confirmed patients into first panel in spread page
function loadConfirmedPatients()
{
    // Fake Data used as temp
    var tag = document.createElement("ul");
    let fakePeople = ['John Milkner', "Raj Gopalan", "Sydney Chao", 'John Milkner', "Raj Gopalan", "Sydney Chao", ];

    for(i = 0; i < fakePeople.length; i++)
    {
        var other = document.createElement("li");
        var text = document.createTextNode(fakePeople[i]);
        other.appendChild(text); 
        tag.appendChild(other);
    }
    var element = document.getElementById("confirmed");
    element.appendChild(tag);
}

//loads list of patients in contact with user who are either 
// a) at high risk of dying if they get infected 
// b) are not confirmed but conditions indicate they are infected
// tag each patient in the list with either a or b to indicate what they are 
function loadContactedPatients()
{
    var tag = document.createElement("p");
    tag.style.fontSize = "1.3vw";
    var text = document.createTextNode("No Possible Patients Contacted");
    tag.appendChild(text);
    var element = document.getElementById("contact");
    element.appendChild(tag);
}

//creates user-susceptibility index and displays it in format 
function buildPIS()
{
    var tag = document.createElement("p");
    tag.style.fontSize = "1.3vw";
    var text = document.createTextNode("Personal Susceptibility Index Not Available At This Time.");
    tag.appendChild(text);
    var element = document.getElementById("personal");
    element.appendChild(tag);
}