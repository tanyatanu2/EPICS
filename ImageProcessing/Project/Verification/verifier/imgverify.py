import cv2 
import numpy as np

class Verifier:
    
    def __init__(self):
        print("Verifier Created.")
        self.MIN_WIDTH = 312
        self.MIN_HEIGHT = 312

        # NOTE : LOOK INTO THIS LATER 
        
        self.BLUR_THRESHOLD = 60.0

        self.DARK_THRESHOLD = 40
        self.BRIGHT_THRESHOLD = 220

        self.MIN_VALID_RATIO = 0.5
        self.MAX_VALID_RATIO = 1.5
    

    def set_image(self , path : str):
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Error for image : {path}")

        res_ver = self.verify_resolution_channels(img)
        if not res_ver["passed"]:
            raise Exception("Please Verify Image Resolution and channels : > 512 , > 512, == 3")
        
        blurscore = self.verify_blur(img)
        if not blurscore["passed"]:
            raise Exception(f"Image too blurry - Score :{blurscore["score"]}")

        exposure_info = self.check_exposure(img)
        if not exposure_info["passed"]:
            raise Exception("Verify Exposure of the Input image")


        return img
        
        

    
    def verify_resolution_channels(self,img):
        height , width , channels = img.shape
        status = (height >= self.MIN_HEIGHT and width >=self.MIN_WIDTH and channels == 3)

        return {
            "passed" : status,
            "width" : width,
            "height" : height,
            "channels" : channels
        }

    def verify_blur(self,img):
        gray = cv2.cvtColor(img , cv2.COLOR_BGR2GRAY)
        score = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        return {
            "passed" : score >= self.BLUR_THRESHOLD,
            "score" : score
        }

    def check_exposure(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        mean_brightness = float(np.mean(gray))

        dark_ratio = float(
            np.mean(gray < self.DARK_THRESHOLD)
        )

        bright_ratio = float(
            np.mean(gray > self.BRIGHT_THRESHOLD)
        )

        passed = (
            dark_ratio < self.MAX_VALID_RATIO and
            bright_ratio < self.MAX_VALID_RATIO
        )

        return {
            "passed": passed,
            "mean_brightness": mean_brightness,
            "dark_ratio": dark_ratio,
            "bright_ratio": bright_ratio
        }

    def normalize_image(
        self,
        image,
        target_size=(512, 512)
    ):
        """
        Resize while preserving aspect ratio.
        Adds padding instead of cropping.
        """

        target_w, target_h = target_size

        h, w = image.shape[:2]

        scale = min(
            target_w / w,
            target_h / h
        )

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(
            image,
            (new_w, new_h),
            interpolation=cv2.INTER_AREA
        )

        canvas = np.zeros(
            (target_h, target_w, 3),
            dtype=np.uint8
        )

        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2

        canvas[
            y:y + new_h,
            x:x + new_w
        ] = resized

        return canvas


        



