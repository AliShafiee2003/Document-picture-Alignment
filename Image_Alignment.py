import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load and validate images
refFilename = os.path.join("images", "form.jpg")
imFilename = os.path.join("images", "scanned-form.jpg")

im1 = cv2.imread(refFilename)
if im1 is None:
    raise ValueError(f"Reference image not found at {refFilename}")

im2 = cv2.imread(imFilename)
if im2 is None:
    raise ValueError(f"Image to be aligned not found at {imFilename}")

im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

# Detect ORB features and descriptors
MAX_NUM_FEATURES = 500
orb = cv2.ORB_create(MAX_NUM_FEATURES)
keypoints1, descriptors1 = orb.detectAndCompute(im1_gray, None)
keypoints2, descriptors2 = orb.detectAndCompute(im2_gray, None)

# Match features
matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = list(matcher.match(descriptors1, descriptors2))  # تبدیل به لیست
matches.sort(key=lambda x: x.distance)

# Draw feature matches
im_matches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None, matchColor=(0, 255, 0))

# Find homography
points1 = np.zeros((len(matches), 2), dtype=np.float32)
points2 = np.zeros((len(matches), 2), dtype=np.float32)
for i, match in enumerate(matches):
    points1[i, :] = keypoints1[match.queryIdx].pt
    points2[i, :] = keypoints2[match.trainIdx].pt

h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)
im2_reg = cv2.warpPerspective(im2, h, (im1.shape[1], im1.shape[0]))

# Save and display results
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)
cv2.imwrite(os.path.join(output_folder, "aligned_form.jpg"), im2_reg)
cv2.imwrite(os.path.join(output_folder, "feature_matches.jpg"), im_matches)

print("Alignment complete. Results saved in 'output' folder.")

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(im1, cv2.COLOR_BGR2RGB))
plt.title("Reference Image")
plt.axis("off")
plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(im2_reg, cv2.COLOR_BGR2RGB))
plt.title("Aligned Image")
plt.axis("off")
plt.tight_layout()
plt.show()
