import json
import os
import base64
import tempfile
import numpy as np
from PIL import Image
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import tensorflow as tf
import boto3
from botocore.exceptions import ClientError

# Global model variable to cache the loaded model
_clf_model = None


class DepthwiseConv2D_Compat(tf.keras.layers.DepthwiseConv2D):
    """Compatibility layer for DepthwiseConv2D"""
    def __init__(self, *args, **kwargs):
        kwargs.pop("groups", None)  # ignore 'groups'
        super().__init__(*args, **kwargs)


def load_model_from_s3():
    """
    Load model from S3: s3://prod-aviara-bucket/models/efficientnetv2s.h5
    Downloads to a temporary file, loads into memory, then deletes temp file.
    Requires IAM permission s3:GetObject on the bucket/object (403 = Forbidden
    means the role/user needs s3:GetObject on prod-aviara-bucket/models/*).
    """
    bucket_name = os.getenv('S3_MODEL_BUCKET_NAME', 'prod-aviara-bucket')
    s3_key = 'models/efficientnetv2s.h5'

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.h5')
    temp_path = temp_file.name
    temp_file.close()

    try:
        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, s3_key, temp_path)

        model = tf.keras.models.load_model(
            temp_path,
            custom_objects={"DepthwiseConv2D": DepthwiseConv2D_Compat}
        )
        os.unlink(temp_path)
        return model
    except ClientError as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == '403' or e.response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 403:
            raise PermissionError(
                "S3 access denied (403). Ensure the IAM role or user has s3:GetObject "
                f"permission on s3://{bucket_name}/{s3_key}. Check bucket policy and IAM permissions."
            ) from e
        raise FileNotFoundError(f"Failed to download model from S3: {str(e)}") from e
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def load_model():
    """
    Load the model from S3 once and cache it in memory. Subsequent calls
    return the cached model; the model is always sourced from S3, not from env.
    """
    global _clf_model
    if _clf_model is None:
        _clf_model = load_model_from_s3()
    return _clf_model


def preprocess_image(image_data, target_size=(224, 224)):
    """
    Preprocess image for model input
    Args:
        image_data: bytes or PIL Image
        target_size: tuple of (width, height)
    Returns:
        numpy array ready for model prediction
    """
    if isinstance(image_data, bytes):
        img = Image.open(BytesIO(image_data)).convert("RGB")
    else:
        img = image_data.convert("RGB")
    
    img = img.resize(target_size)
    arr = np.array(img) / 255.0
    return np.expand_dims(arr, axis=0), img


@csrf_exempt
def classify_skin_lesion(request):
    """
    Classify skin lesion from uploaded image
    POST /skin-lesion/classify/
    
    Request body:
    {
        "image_base64": "base64-encoded-image-string"
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_base64 = data.get('image_base64') or data.get('image')
            
            if not image_base64:
                return JsonResponse({
                    'error': 'image_base64 is required'
                }, status=400)
            
            # Decode base64 image
            try:
                # Remove data URL prefix if present
                if ',' in image_base64:
                    image_base64 = image_base64.split(',')[1]
                
                image_data = base64.b64decode(image_base64)
            except Exception as e:
                return JsonResponse({
                    'error': f'Invalid base64 image data: {str(e)}'
                }, status=400)
            
            # Preprocess image
            try:
                img_input, _ = preprocess_image(image_data)
            except Exception as e:
                return JsonResponse({
                    'error': f'Error preprocessing image: {str(e)}'
                }, status=400)
            
            # Load model and predict
            try:
                model = load_model()
                probs = model.predict(img_input, verbose=0)
                pred_class = np.argmax(probs, axis=1)[0]
                confidence = float(np.max(probs))
            except Exception as e:
                return JsonResponse({
                    'error': f'Error during prediction: {str(e)}'
                }, status=500)
            
            # Class names mapping
            class_names = {
                0: "Actinic Keratoses and Intraepithelial Carcinoma (AKIEC)",
                1: "Basal Cell Carcinoma (BCC)",
                2: "Benign Keratosis-like Lesions (BKL)",
                3: "Dermatofibroma (DF)",
                4: "Melanoma (MEL)",
                5: "Melanocytic Nevi (NV)",
                6: "Vascular Lesions (VASC)"
            }
            
            pred_class_name = class_names.get(pred_class, "Unknown")
            
            # Prepare response (classification result only, no image storage)
            response_data = {
                'predicted_class': pred_class_name,
                'predicted_class_id': int(pred_class),
                'confidence': round(confidence, 4),
                'confidence_percentage': f"{confidence * 100:.2f}%",
                'all_probabilities': {
                    class_names[i]: float(probs[0][i]) for i in range(len(class_names))
                }
            }
            
            return JsonResponse(response_data, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            return JsonResponse({
                'error': f'Unexpected error: {str(e)}'
            }, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
