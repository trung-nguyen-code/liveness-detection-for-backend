from handlers.dtos.detect_liveness_dto import DetectLivnessDTO

def handler_detect_response(img, usecaseDetect):
    # Dependency injection
    image_info = usecaseDetect.face_detect(img)
    
    detectLiveness_response = DetectLivnessDTO(
        label= "RealFace" if image_info["label"] ==1 and image_info["value"]>=0.8 else "FakeFace",
        probability= image_info["value"],
        test_speed= image_info["test_speed"],
        bbox= image_info["image_bbox"],
        width= image_info["width"],
        height= image_info["height"]
    )
            
    return detectLiveness_response
    