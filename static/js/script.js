// Smart Fitness Monitor - simple client-side helpers
document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss success alerts after a few seconds
  document.querySelectorAll(".alert-success").forEach(function (el) {
    setTimeout(function () {
      el.classList.add("fade");
      el.style.opacity = "0";
    }, 4000);
  });

  console.log("Smart Fitness Monitor UI loaded.");
});
/* ==========================================
   SQUAT DETECTION DASHBOARD
   ========================================== */

let squatCameraRunning = false;
let squatDataTimer = null;


/* ==========================================
   START CAMERA
   ========================================== */

function startSquatCamera() {

    const camera =
        document.getElementById("squatCamera");

    const placeholder =
        document.getElementById("cameraPlaceholder");

    const status =
        document.getElementById("squatStatus");


    camera.src = "/video_feed";

    camera.style.display = "block";

    placeholder.style.display = "none";

    squatCameraRunning = true;

    status.textContent =
        "🟢 Squat detection is active.";

    startSquatDataUpdates();
}


/* ==========================================
   STOP CAMERA
   ========================================== */

function stopSquatCamera() {

    const camera =
        document.getElementById("squatCamera");

    const placeholder =
        document.getElementById("cameraPlaceholder");

    const status =
        document.getElementById("squatStatus");


    camera.src = "";

    camera.style.display = "none";

    placeholder.style.display = "block";

    squatCameraRunning = false;

    status.textContent =
        "Camera is stopped.";

    stopSquatDataUpdates();
}


/* ==========================================
   UPDATE SQUAT DATA
   ========================================== */

function startSquatDataUpdates() {

    if (squatDataTimer) {
        clearInterval(squatDataTimer);
    }

    squatDataTimer = setInterval(
        updateSquatData,
        500
    );
}


function stopSquatDataUpdates() {

    if (squatDataTimer) {

        clearInterval(
            squatDataTimer
        );

        squatDataTimer = null;
    }
}


/* ==========================================
   GET DATA FROM FLASK
   ========================================== */

async function updateSquatData() {

    if (!squatCameraRunning) {
        return;
    }

    try {

        const response =
            await fetch("/squat_data");

        const data =
            await response.json();


        document.getElementById(
            "squatCount"
        ).textContent =
            data.squats;


        document.getElementById(
            "kneeAngle"
        ).textContent =
            data.angle + "°";


        document.getElementById(
            "squatPosition"
        ).textContent =
            data.position;


    } catch (error) {

        console.error(
            "Unable to get squat data:",
            error
        );

    }
}


/* ==========================================
   RESET COUNTER
   ========================================== */

async function resetSquatCounter() {

    try {

        await fetch(
            "/reset_squats"
        );

        document.getElementById(
            "squatCount"
        ).textContent = "0";

        document.getElementById(
            "kneeAngle"
        ).textContent = "0°";

        document.getElementById(
            "squatPosition"
        ).textContent = "UP";

    } catch (error) {

        console.error(
            "Unable to reset squat counter:",
            error
        );

    }

}