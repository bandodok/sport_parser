var SEASON = window.season
var NEXT_PAGE_URL = 2


initCalendar = () => {
    let url = '/api/khl/calendar/?season=' + SEASON;
    let f = new XMLHttpRequest();
    f.open('GET', url);
    f.responseType = 'json';
    f.send();
    f.onload = function() {
        const response = f.response;
        NEXT_PAGE_URL = response['next']
        const finished_matches = response['results']
        createMatchFrame('team1', finished_matches)
    }
};

document.addEventListener('scroll', function(event) {
    if (NEXT_PAGE_URL !== null) {
        if (document.documentElement.scrollHeight < document.documentElement.scrollTop + window.innerHeight + 500) {
            let f = new XMLHttpRequest();
            f.open('GET', NEXT_PAGE_URL);
            f.responseType = 'json';
            f.send();
            NEXT_PAGE_URL = null
            f.onload = function() {
                const response = f.response;
                NEXT_PAGE_URL = response['next']
                const finished_matches = response['results']
                createMatchFrame('team1', finished_matches)
            }
        }
    }
    else {
    }
});


window.addEventListener( "load", function () {
  function sendData() {
    const XHR = new XMLHttpRequest();
    const FD = new FormData( form );

    // Define what happens on successful data submission
    XHR.addEventListener( "load", function(event) {
        clearBody('team1')
        const response = event.target.response;
        NEXT_PAGE_URL = response['next']
        const finished_matches = response['results']
        createMatchFrame('team1', finished_matches)
    } );

    // Define what happens in case of error
    XHR.addEventListener( "error", function( event ) {
      alert( 'Oops! Something went wrong.' );
    } );

    // Set up our request
    fd = FD.entries()
    a = fd.next()
    var params = "?"
    while (a['done'] === false) {
        params += a['value'][0] + "=" + a['value'][1] + "&"
        a = fd.next()
    }
    url = "/api/khl/calendar/" + params + "season=" + SEASON
    XHR.open( "GET", url );
    XHR.responseType = 'json';

    // The data sent is what the user provided in the form
    XHR.send( FD );
  }

  // Access the form element...
  const form = document.getElementById( "calendar_filter" );

  // ...and take over its submit event.
  form.addEventListener( "submit", function ( event ) {
    event.preventDefault();

    sendData();
  } );
} );


function toggleOrdering() {
   var element = document.getElementById("ordering-checkbox");
   var input = document.getElementById("id_ordering");
   element.classList.toggle("on");
   switch (input.value) {
       case "-date": {
           input.value = 'date'
           break
       }
       case "date":
           input.value = '-date'
           break
       }
}

function toggleOrderingAsc() {
   var element = document.getElementById("ordering-checkbox");
   var input = document.getElementById("id_ordering");
   element.classList = "ordering-checkbox";
   input.value = 'date'
}