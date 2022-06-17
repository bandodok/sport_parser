let SEASON = window.season
let NEXT_PAGE_URL = 2


/**
 * Получает список матчей сезона при загрузке страницы.
 */
function initCalendar() {
    let url = `/api/calendar/?ordering=date&config=${CONFIG}&season=${SEASON}`;
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

    const form = document.getElementById( "calendar_filter" );
    form.addEventListener( "submit", function ( event ) {
        event.preventDefault();
        sendData(form);
    });
}

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


/**
 * Отправляет данные формы, обрабатывает ответ.
 * @param {HTMLElement} form
 */
function sendData(form) {
    const XHR = new XMLHttpRequest();
    const FD = new FormData( form );

    // Define what happens on successful data submission
    XHR.addEventListener( "load", function(event) {
        const response = event.target.response;
        successSubmission(response)
    } );

    // Define what happens in case of error
    XHR.addEventListener( "error", function( event ) {
        errorSubmission()
    } );

    // Set up our request
    let url = getUrl(FD);
    XHR.open( "GET", url );
    XHR.responseType = 'json';

    // The data sent is what the user provided in the form
    XHR.send( FD );
}


/**
 * Вызывается при успешном получении ответа после отправки формы.
 * @param response данные ответа
 */
function successSubmission(response) {
    clearBody('team1')
    NEXT_PAGE_URL = response['next']
    const matches = response['results']
    createMatchFrame('team1', matches)
}


/**
 * Вызывается при возникновении ошибки во время отправки формы.
 */
function errorSubmission() {
    alert( 'Oops! Something went wrong.' );
}


/**
 * Возвращает url, сформированный на основе данных формы.
 * @param {FormData} formData данные формы
 * @returns {string} url с параметрами
 */
function getUrl(formData) {
    let fd = formData.entries()
    let param = fd.next()
    let params = "?"
    while (param['done'] === false) {
        if (param['value'][1] === "") {
            param = fd.next()
            continue
        }
        params += param['value'][0] + "=" + param['value'][1] + "&"
        param = fd.next()
    }
    return `/api/calendar/${params}config=${CONFIG}&season=${SEASON}`
}


function toggleOrdering() {
   let element = document.getElementById("ordering-checkbox");
   let input = document.getElementById("id_ordering");
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
   let element = document.getElementById("ordering-checkbox");
   let input = document.getElementById("id_ordering");
   element.classList = "ordering-checkbox";
   input.value = 'date'
}