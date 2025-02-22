import cv2
import numpy as np
import pytesseract
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def detect_menu_text(image_path, output_path='annotated_image.jpg'):
    """
    Detect and extract text from a menu image using Tesseract OCR.

    Args:
        image_path (str): Path to the menu image file.
        output_path (str): Path where the annotated image will be saved.

    Returns:
        list: List of dictionaries containing detected text with bounding boxes.
    """
    try:
        # Load the image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image at {image_path}")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_bgr = img.copy()

        # Perform OCR
        results = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)

        # Extract text with bounding boxes
        text_items = []
        for i in range(len(results['text'])):
            text = results['text'][i].strip()
            if text and int(results['conf'][i]) > 50:  # Confidence threshold
                x, y, w, h = (int(results['left'][i]), int(results['top'][i]), 
                              int(results['width'][i]), int(results['height'][i]))
                text_items.append({
                    'text': text,
                    'confidence': float(results['conf'][i]) / 100,
                    'x1': x,
                    'y1': y,
                    'x2': x + w,
                    'y2': y + h
                })
                
                # Draw bounding box and text on the image
                cv2.rectangle(img_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img_bgr, text, (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        # Save the annotated image
        cv2.imwrite(output_path, img_bgr)
        logging.debug(f"Detected {len(text_items)} text items in {image_path}. Annotated image saved to {output_path}")

        return text_items

    except Exception as e:
        logging.error(f"Error in detect_menu_text: {e}")
        return []

# Example usage
if __name__ == "__main__":
    image_path = 'temp.jpeg'
    output_path = 'annotated_menu_image_1.jpg'
    text_items = detect_menu_text(image_path, output_path)
    
    # Print detected text
    for item in text_items:
        print(f"Detected: {item['text']} (Confidence: {item['confidence']:.2f}) at "
              f"[{item['x1']}, {item['y1']}] - [{item['x2']}, {item['y2']}]")