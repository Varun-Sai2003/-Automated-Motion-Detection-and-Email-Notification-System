import cv2
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Function to send email notification
def send_email_notification(filename):
    from_address = "versionfps2024@gmail.com"  # Sender's email address
    to_address = "entertainervarunsai@gmail.com"  # Receiver's email address
    subject = "Motion Detected!"
    body = "Motion was detected in your area. Please check the attached image."

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_address, "wslh zrdz hexp lfne")
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()

# Force matplotlib to not use any Xwindows backend
plt.switch_backend('Agg')

# Initialize video capture
cap = cv2.VideoCapture(0)

# Capture video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define the codec and create VideoWriter object for saving marked video
codec = cv2.VideoWriter_fourcc(*'DIVX')
out_video = cv2.VideoWriter('C:/Users/varun/Desktop/CG mini/Captured images/output.avi', codec, fps, (frame_width, frame_height))

# Capture two frames
ret, frame1 = cap.read()
ret, frame2 = cap.read()

frame_number = 0
motion_counter = 0

while cap.isOpened():
    # Calculate absolute difference between frames
    diff = cv2.absdiff(frame1, frame2)
    
    # Convert to grayscale
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to remove noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Thresholding to create binary image
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    
    # Dilate the thresholded image to fill gaps
    dilated = cv2.dilate(thresh, None, iterations=3)
    
    # Find contours of moving objects
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw rectangles around moving objects and save image if there is motion
    motion_detected = False
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if cv2.contourArea(contour) < 1000:  # Adjust minimum area as needed
            continue
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame1, "Status: Movement", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        motion_detected = True
    
    # Write the frame with marked regions to the video file
    out_video.write(frame1)
    
    # Save the frame only if motion is detected
    if motion_detected:
        motion_counter += 1
        cv2.imwrite(f'C:/Users/varun/Desktop/CG mini/Captured images/motion_detection_{frame_number}.png', frame1)
        
        # Optionally, send an email notification with the captured image
        send_email_notification(f'C:/Users/varun/Desktop/CG mini/Captured images/motion_detection_{frame_number}.png')
        
        frame_number += 1
    
    # Update frames
    frame1 = frame2
    ret, frame2 = cap.read()
    
    # Exit loop after processing all frames
    if frame2 is None:
        break

# Release video capture and VideoWriter objects
cap.release()
out_video.release()

# Print total number of frames with motion detected
print(f"Total frames with motion detected: {motion_counter}")
