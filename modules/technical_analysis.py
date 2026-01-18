import cv2
import numpy as np
from tensorflow.keras.models import load_model

class TechnicalAnalyzer:
    """Technical analysis using CNN model"""
    
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.class_labels = ['downtrend', 'sideways', 'uptrend']
        self.img_size = (224, 224)
    
    def preprocess_image(self, image_path):
        """Preprocess chart image for CNN"""
        img = cv2.imread(image_path)
        img = cv2.resize(img, self.img_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    
    def predict(self, image_path):
        """Predict trend from chart image"""
        processed_img = self.preprocess_image(image_path)
        predictions = self.model.predict(processed_img, verbose=0)
        
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]
        trend = self.class_labels[predicted_class]
        
        # Calculate technical score (0-50)
        if trend == 'uptrend':
            score = 30 + (confidence * 20)  # 30-50 points
        elif trend == 'sideways':
            score = 15 + (confidence * 15)  # 15-30 points
        else:  # downtrend
            score = confidence * 15  # 0-15 points
        
        result = {
            'trend': trend.upper(),
            'confidence': float(confidence * 100),
            'score': float(score),
            'probabilities': {
                'downtrend': float(predictions[0][0] * 100),
                'sideways': float(predictions[0][1] * 100),
                'uptrend': float(predictions[0][2] * 100)
            }
        }
        
        return result
