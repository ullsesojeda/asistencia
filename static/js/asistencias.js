// ==========================================================
// SCA - SISTEMA DE CONTROL DE ASISTENCIA
// static/js/asistencias.js
// ==========================================================

let video;
let canvas;
let preview;
let btnFoto;
let form;

let latitud;
let longitud;
let precision;
let direccion;

let estadoGPS;

let fotoBlob = null;
let stream = null;

// ==========================================================
// INICIAR
// ==========================================================

document.addEventListener("DOMContentLoaded", async function () {

    video = document.getElementById("video");
    canvas = document.getElementById("canvas");
    preview = document.getElementById("preview");

    btnFoto = document.getElementById("btnFoto");
    form = document.getElementById("formAsistencia");

    latitud = document.getElementById("latitud");
    longitud = document.getElementById("longitud");
    precision = document.getElementById("precision");
    direccion = document.getElementById("direccion");

    estadoGPS = document.getElementById("estadoGPS");

    await iniciarCamara();

    obtenerGPS();

    btnFoto.addEventListener(
        "click",
        capturarFotografia
    );

    form.addEventListener(
        "submit",
        enviarFormulario
    );

});

// ==========================================================
// INICIAR CAMARA
// ==========================================================

async function iniciarCamara() {

    try {
        console.log(location.href);
        console.log(window.isSecureContext);
        console.log(navigator.mediaDevices);
        stream = await navigator.mediaDevices.getUserMedia({

            video: {

                facingMode: "user",

                width: {
                    ideal: 1280
                },

                height: {
                    ideal: 720
                }

            },

            audio: false

        });

        video.srcObject = stream;

    }

    catch (error) {

    console.error(error);

    alert(
        "Error: " +
        error.name +
        "\n" +
        error.message
    );

}

}

// ==========================================================
// CAPTURAR FOTOGRAFIA
// ==========================================================

function capturarFotografia() {

    canvas.width = video.videoWidth;

    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");

    ctx.drawImage(

        video,

        0,

        0,

        canvas.width,

        canvas.height

    );

    preview.src = canvas.toDataURL(

        "image/jpeg",

        0.90

    );

    preview.style.display = "block";

    canvas.toBlob(

        function(blob){

            fotoBlob = blob;

        },

        "image/jpeg",

        0.90

    );

}
// ==========================================================
// OBTENER GPS
// ==========================================================

function obtenerGPS() {

    if (!navigator.geolocation) {

        estadoGPS.innerHTML =
            "Este dispositivo no soporta geolocalización.";

        return;
    }

    estadoGPS.innerHTML =
        "Obteniendo ubicación...";

    navigator.geolocation.getCurrentPosition(

        async function (posicion) {

            latitud.value = posicion.coords.latitude;
            longitud.value = posicion.coords.longitude;
            precision.value = posicion.coords.accuracy;

            estadoGPS.innerHTML =
                "Ubicación obtenida.";

            await obtenerDireccion(
                posicion.coords.latitude,
                posicion.coords.longitude
            );

        },

        function (error) {

            console.error(error);

            estadoGPS.innerHTML =
                "No fue posible obtener la ubicación.";

        },

        {

            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0

        }

    );

}

// ==========================================================
// OBTENER DIRECCION
// ==========================================================

async function obtenerDireccion(lat, lng) {

    try {

        const respuesta = await fetch(

            "https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat="

            + lat +

            "&lon=" +

            lng

        );

        const datos = await respuesta.json();

        if (datos.display_name) {

            direccion.value = datos.display_name;

        }

    }

    catch (error) {

        console.error(error);

    }

}

// ==========================================================
// ENVIAR FORMULARIO
// ==========================================================

async function enviarFormulario(e) {

    e.preventDefault();

    if (fotoBlob === null) {

        alert("Debe tomar la fotografía.");

        return;

    }

    if (latitud.value === "") {

        alert("No se obtuvo la ubicación.");

        return;

    }

    const datos = new FormData();

    datos.append(
        "foto",
        fotoBlob,
        "asistencia.jpg"
    );

    datos.append(
        "latitud",
        latitud.value
    );

    datos.append(
        "longitud",
        longitud.value
    );

    datos.append(
        "precision",
        precision.value
    );

    datos.append(
        "direccion",
        direccion.value
    );

    datos.append(
        "observaciones",
        document.querySelector(
            "textarea[name='observaciones']"
        ).value
    );
        try {

        const respuesta = await fetch(

            form.action,

            {

                method: "POST",

                body: datos

            }

        );

        if (respuesta.redirected) {

            window.location.href = respuesta.url;

            return;

        }

        if (respuesta.ok) {

            alert("Asistencia registrada correctamente.");

            window.location.reload();

            return;

        }

        alert("No fue posible registrar la asistencia.");

    }

    catch (error) {

        console.error(error);

        alert("Ocurrió un error al enviar la información.");

    }

}