import cv2  # OpenCV for video processing
import mediapipe as mp  # MediaPipe for hand, face, and pose detection
import numpy as np  # NumPy for numerical operations

# Initialize MediaPipe utilities
mp_drawing = mp.solutions.drawing_utils  # Drawing helper
mp_drawing_styles = mp.solutions.drawing_styles  # Style helper
mp_sign_tracker = mp.solutions.holistic  # Renamed "holistic" to "signTracker" for personalization

# Background color (gray)
BG_COLOR = (192, 192, 192)

def process_static_images(image_files):
    """ Process static images for ASL sign detection. """
    with mp_sign_tracker.Holistic(  # Initialize MediaPipe sign tracker
        static_image_mode=True,  # Process a single image at a time
        model_complexity=2,  # Use high model accuracy
        enable_segmentation=True,  # Enable background segmentation
        refine_face_landmarks=True  # Improve face landmark accuracy
    ) as signTracker:
        for idx, file in enumerate(image_files):  
            image = cv2.imread(file)  # Load the image
            if image is None:
                print(f"⚠️ Cannot load image: {file}")
                continue

            image_height, image_width, _ = image.shape  # Get image dimensions
            results = signTracker.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # Process image

            # Print nose coordinates if a pose is detected
            if results.pose_landmarks:
                nose = results.pose_landmarks.landmark[mp_sign_tracker.PoseLandmark.NOSE]
                print(f"📍 Nose coordinates: ({nose.x * image_width:.2f}, {nose.y * image_height:.2f})")

            # Apply background segmentation
            annotated_image = apply_segmentation(image, results)

            # Save the processed image
            output_path = f"/tmp/annotated_image_{idx}.png"
            cv2.imwrite(output_path, annotated_image)
            print(f"✅ Processed image saved: {output_path}")

            # Draw pose landmarks in 3D space
            mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_sign_tracker.POSE_CONNECTIONS)

def apply_segmentation(image, results):
    """ Apply background segmentation to focus on the subject. """
    if results.segmentation_mask is not None:
        condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.1  # Create mask
        bg_image = np.zeros(image.shape, dtype=np.uint8)  # Create background image
        bg_image[:] = BG_COLOR  # Fill with gray color
        return np.where(condition, image, bg_image)  # Apply segmentation
    return image  # Return original image if no segmentation mask

def draw_landmarks(image, results):
    """ Draw facial, hand, and pose landmarks on the image. """
    mp_drawing.draw_landmarks(
        image, results.face_landmarks, mp_sign_tracker.FACEMESH_CONTOURS,  # Draw face mesh
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
    )
    mp_drawing.draw_landmarks(
        image, results.pose_landmarks, mp_sign_tracker.POSE_CONNECTIONS,  # Draw body pose
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )

def process_webcam():
    """ Capture and process live video from the webcam for ASL detection. """
    cap = cv2.VideoCapture(0)  # Open webcam
    
    with mp_sign_tracker.Holistic(
        min_detection_confidence=0.5,  # Minimum confidence for detection
        min_tracking_confidence=0.5  # Minimum confidence for tracking
    ) as signTracker:
        while cap.isOpened():
            success, image = cap.read()  # Capture frame
            if not success:
                print("⚠️ Skipping empty frame.")
                continue

            image.flags.writeable = False  # Optimize processing speed
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB
            results = signTracker.process(image)  # Process image

            image.flags.writeable = True  # Allow image modifications
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Convert back to BGR

            draw_landmarks(image, results)  # Draw detected landmarks

            # Flip image for a selfie view
            cv2.imshow("ASL Detection - Sign Tracker", cv2.flip(image, 1))

            # Press 'ESC' to exit
            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()  # Release webcam
    cv2.destroyAllWindows()  # Close all OpenCV windows

# Choose mode: Process static images or webcam input
if __name__ == "__main__":
    MODE = "webcam"  # Change to "static" to process images

    if MODE == "static":
        IMAGE_FILES = ["test_image.jpg"]  # Add images to process
        process_static_images(IMAGE_FILES)
    else:
        process_webcam()  # Run real-time ASL detection