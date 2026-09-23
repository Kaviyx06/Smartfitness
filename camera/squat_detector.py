
import cv2
import mediapipe as mp
import math


class SquatDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.reps = 0
        self.stage = None

    def calculate_angle(self, a, b, c):
        """Calculate angle between three body landmarks."""

        angle = math.degrees(
            math.atan2(c[1] - b[1], c[0] - b[0])
            - math.atan2(a[1] - b[1], a[0] - b[0])
        )

        angle = abs(angle)

        if angle > 180:
            angle = 360 - angle

        return angle

    def process_frame(self, frame):
        """Process one camera frame and detect squat."""

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = self.pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:

            landmarks = results.pose_landmarks.landmark

            # Right hip, knee and ankle
            hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
            knee = landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE]
            ankle = landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE]

            h, w, _ = frame.shape

            hip_point = (int(hip.x * w), int(hip.y * h))
            knee_point = (int(knee.x * w), int(knee.y * h))
            ankle_point = (int(ankle.x * w), int(ankle.y * h))

            angle = self.calculate_angle(
                hip_point,
                knee_point,
                ankle_point
            )

            # Squat detection
            if angle > 150:
                self.stage = "up"

            if angle < 120 and self.stage == "up":
                self.stage = "down"
                self.reps += 1

            # Display angle
            cv2.putText(
                image,
                f"Knee Angle: {int(angle)}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            # Draw pose
            self.mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

        # Display repetition count
        cv2.putText(
            image,
            f"Squats: {self.reps}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        return image


def run_camera():

    print("Starting camera...")

    # Try the default Windows camera
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        print("Please check that your webcam is available.")
        return

    detector = SquatDetector()

    print("Camera started.")
    print("Perform squats in front of the camera.")
    print("Press Q to stop.")

    try:

        while True:

            success, frame = camera.read()

            if not success:
                print("ERROR: Could not read camera frame.")
                break

            frame = detector.process_frame(frame)

            cv2.imshow(
                "Smart Fitness - Squat Detection",
                frame
            )

            # Press Q to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        camera.release()
        cv2.destroyAllWindows()

        print()
        print("--------------------------------")
        print("Workout completed.")
        print(f"Squats detected: {detector.reps}")
        print("--------------------------------")


if __name__ == "__main__":
    run_camera()
