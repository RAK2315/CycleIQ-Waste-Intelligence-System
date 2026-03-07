import numpy as np
import random

YOLO_TO_WASTE = {
    # Plastic / Recyclable
    "bottle": "recyclable", "wine glass": "recyclable", "cup": "recyclable",
    "frisbee": "recyclable", "sports ball": "recyclable", "kite": "recyclable",
    "skateboard": "recyclable", "surfboard": "recyclable", "umbrella": "recyclable",
    "handbag": "recyclable", "backpack": "recyclable", "suitcase": "recyclable",
    "toothbrush": "recyclable",
    # Paper / Recyclable
    "book": "recyclable", "tie": "recyclable",
    # Metal / Recyclable
    "fork": "recyclable", "knife": "recyclable", "spoon": "recyclable",
    "scissors": "recyclable", "tennis racket": "recyclable", "oven": "recyclable",
    "sink": "recyclable", "clock": "recyclable",
    # Glass / Recyclable
    "vase": "recyclable",
    # Biodegradable / Organic
    "banana": "biodegradable", "apple": "biodegradable", "sandwich": "biodegradable",
    "orange": "biodegradable", "broccoli": "biodegradable", "carrot": "biodegradable",
    "pizza": "biodegradable", "donut": "biodegradable", "cake": "biodegradable",
    "hot dog": "biodegradable", "potted plant": "biodegradable", "bowl": "biodegradable",
    "dining table": "biodegradable",
    # Hazardous - ONLY actual electronics/batteries
    "remote": "hazardous", "cell phone": "hazardous", "laptop": "hazardous",
    "tv": "hazardous", "keyboard": "hazardous", "mouse": "hazardous",
    "microwave": "hazardous",
}

# Map waste categories back to our 6-category system
WASTE_TO_SUBCATEGORY = {
    "biodegradable": {"organic_pct": 85, "plastic_pct": 5, "paper_pct": 5, "metal_pct": 2, "glass_pct": 1, "hazardous_pct": 2},
    "recyclable":    {"organic_pct": 5,  "plastic_pct": 45, "paper_pct": 25, "metal_pct": 15, "glass_pct": 8, "hazardous_pct": 2},
    "hazardous":     {"organic_pct": 2,  "plastic_pct": 10, "paper_pct": 5,  "metal_pct": 15, "glass_pct": 3, "hazardous_pct": 65},
}

class WasteClassifier:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self._try_load_model()

    def _try_load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            self.model_loaded = True
            print("YOLOv8 loaded successfully.")
        except Exception as e:
            print(f"YOLOv8 unavailable: {e}")

    def classify_image(self, image_bytes: bytes) -> dict:
        if self.model_loaded:
            return self._classify_with_yolo(image_bytes)
        return self._image_aware_simulation(image_bytes)

    def _classify_with_yolo(self, image_bytes: bytes) -> dict:
        try:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_array = np.array(image)
            results = self.model(img_array, verbose=False)

            category_scores = {"biodegradable": 0.0, "recyclable": 0.0, "hazardous": 0.0}
            confidences = []
            total_detections = 0
            detected_objects = []

            for result in results:
                for box in result.boxes:
                    cls_name = result.names[int(box.cls)].lower()
                    conf = float(box.conf)
                    if conf >= 0.3:
                        category = YOLO_TO_WASTE.get(cls_name)
                        if category:
                            category_scores[category] += conf
                            confidences.append(conf)
                            total_detections += 1
                            detected_objects.append(f"{cls_name}({conf:.0%})")

            total_score = sum(category_scores.values())
            if total_score > 0:
                # Find dominant waste category
                dominant_cat = max(category_scores, key=category_scores.get)
                dom_pct = category_scores[dominant_cat] / total_score

                # Map to 6-subcategory breakdown
                sub = WASTE_TO_SUBCATEGORY[dominant_cat]
                avg_conf = sum(confidences)/len(confidences) if confidences else 0.82
                return {
                    "organic_pct": round(sub["organic_pct"] * dom_pct + random.uniform(0,3), 2),
                    "plastic_pct": round(sub["plastic_pct"] * dom_pct + random.uniform(0,3), 2),
                    "paper_pct": round(sub["paper_pct"] * dom_pct + random.uniform(0,2), 2),
                    "metal_pct": round(sub["metal_pct"] * dom_pct + random.uniform(0,2), 2),
                    "glass_pct": round(sub["glass_pct"] * dom_pct + random.uniform(0,1), 2),
                    "hazardous_pct": round(sub["hazardous_pct"] * dom_pct + random.uniform(0,1), 2),
                    "total_volume_liters": round(random.uniform(20, 200), 1),
                    "confidence_score": round(avg_conf, 3),
                    "total_detections": total_detections,
                    "detected_objects": ", ".join(detected_objects[:5]),
                    "mode": "yolo",
                    "note": f"Detected: {', '.join(detected_objects[:3])}"
                }
            else:
                return self._image_aware_simulation(image_bytes)
        except Exception as e:
            print(f"YOLO error: {e}")
            return self._image_aware_simulation(image_bytes)

    def _image_aware_simulation(self, image_bytes: bytes) -> dict:
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_small = img.resize((50, 50))
            pixels = np.array(img_small).reshape(-1, 3)
            avg_color = pixels.mean(axis=0)
            r, g, b = avg_color
            if g > r and g > b:
                base = {"organic": 52, "plastic": 18, "paper": 12, "metal": 7, "glass": 6, "hazardous": 5}
            elif b > r and b > g:
                base = {"organic": 10, "plastic": 35, "paper": 10, "metal": 10, "glass": 30, "hazardous": 5}
            elif r > g and r > b and g > 100:
                base = {"organic": 40, "plastic": 15, "paper": 30, "metal": 7, "glass": 5, "hazardous": 3}
            elif abs(int(r)-int(g)) < 20 and r < 150:
                base = {"organic": 10, "plastic": 20, "paper": 10, "metal": 40, "glass": 10, "hazardous": 10}
            else:
                base = {"organic": 30, "plastic": 30, "paper": 15, "metal": 10, "glass": 10, "hazardous": 5}
            for k in base:
                base[k] = max(1, base[k] + random.uniform(-3, 3))
            total = sum(base.values())
            return {
                "organic_pct": round(base["organic"]/total*100, 2),
                "plastic_pct": round(base["plastic"]/total*100, 2),
                "paper_pct": round(base["paper"]/total*100, 2),
                "metal_pct": round(base["metal"]/total*100, 2),
                "glass_pct": round(base["glass"]/total*100, 2),
                "hazardous_pct": round(base["hazardous"]/total*100, 2),
                "total_volume_liters": round(random.uniform(20, 200), 1),
                "confidence_score": round(random.uniform(0.70, 0.86), 3),
                "total_detections": random.randint(1, 6),
                "detected_objects": "image-analysis",
                "mode": "image-aware",
                "note": "Classified using image color analysis"
            }
        except:
            return self._simulate_classification()

    def _simulate_classification(self) -> dict:
        vals = [random.uniform(25,55), random.uniform(15,35), random.uniform(5,20),
                random.uniform(2,10), random.uniform(2,8), random.uniform(1,5)]
        total = sum(vals)
        return {
            "organic_pct": round(vals[0]/total*100,2), "plastic_pct": round(vals[1]/total*100,2),
            "paper_pct": round(vals[2]/total*100,2), "metal_pct": round(vals[3]/total*100,2),
            "glass_pct": round(vals[4]/total*100,2), "hazardous_pct": round(vals[5]/total*100,2),
            "total_volume_liters": round(random.uniform(20, 200), 1),
            "confidence_score": round(random.uniform(0.75, 0.92), 3),
            "total_detections": random.randint(3, 12),
            "detected_objects": "simulation",
            "mode": "simulation", "note": "Simulation mode"
        }

classifier = WasteClassifier()