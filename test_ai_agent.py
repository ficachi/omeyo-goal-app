import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.ai_agent import generate_image_with_imagen

@pytest.mark.asyncio
async def test_generate_image_with_imagen_success():
    """
    Tests successful image generation with Imagen.
    Mocks the Vertex AI client and its predict method.
    """
    mock_prediction = MagicMock()
    # Simulate a response structure that the function expects.
    # This needs to align with how `generate_image_with_imagen` processes predictions.
    # Assuming it expects a dictionary with a 'url' key.
    mock_prediction.predictions = [{'url': 'http://example.com/generated_image.png'}]

    # Mock google.cloud.aiplatform
    mock_aiplatform = MagicMock()
    mock_endpoint_instance = MagicMock()
    mock_endpoint_instance.predict.return_value = mock_prediction
    mock_aiplatform.Endpoint.return_value = mock_endpoint_instance
    mock_aiplatform.init.return_value = None

    with patch.dict('sys.modules', {'google.cloud.aiplatform': mock_aiplatform}):
        prompt = "A beautiful sunset over a mountain range"
        result = await generate_image_with_imagen(prompt)

        mock_aiplatform.init.assert_called_once()
        mock_aiplatform.Endpoint.assert_called_once()
        mock_endpoint_instance.predict.assert_called_once()

        # Check the arguments passed to predict (or the prompt construction)
        called_instances = mock_endpoint_instance.predict.call_args[1]['instances']
        assert len(called_instances) == 1
        assert called_instances[0]['prompt'] == f"{prompt}, no text, photorealistic, forward-looking view"

        assert result == 'http://example.com/generated_image.png'

@pytest.mark.asyncio
async def test_generate_image_with_imagen_api_error():
    """
    Tests how the function handles an error from the Imagen API (e.g., predict fails).
    """
    mock_aiplatform = MagicMock()
    mock_endpoint_instance = MagicMock()
    mock_endpoint_instance.predict.side_effect = Exception("Imagen API Error")
    mock_aiplatform.Endpoint.return_value = mock_endpoint_instance
    mock_aiplatform.init.return_value = None

    with patch.dict('sys.modules', {'google.cloud.aiplatform': mock_aiplatform}):
        prompt = "A futuristic city"
        result = await generate_image_with_imagen(prompt)
        assert "Error generating image: Imagen API Error" in result

@pytest.mark.asyncio
async def test_generate_image_with_imagen_import_error():
    """
    Tests how the function handles an ImportError if google.cloud.aiplatform is not available.
    """
    with patch.dict('sys.modules', {'google.cloud.aiplatform': None}):
        prompt = "A serene beach"
        result = await generate_image_with_imagen(prompt)
        assert result == "Error: Image generation library not installed."

@pytest.mark.asyncio
async def test_generate_image_with_imagen_no_predictions():
    """
    Tests the case where the API returns a response but no predictions.
    """
    mock_empty_prediction = MagicMock()
    mock_empty_prediction.predictions = [] # No predictions

    with patch('google.cloud.aiplatform', autospec=True) as mock_aiplatform:
        mock_endpoint_instance = MagicMock()
        mock_endpoint_instance.predict.return_value = mock_empty_prediction
        mock_aiplatform.Endpoint.return_value = mock_endpoint_instance
        mock_aiplatform.init.return_value = None

        prompt = "An abstract painting"
        result = await generate_image_with_imagen(prompt)
        assert result == "Error: AI service did not return an image."

@pytest.mark.asyncio
async def test_generate_image_with_imagen_unexpected_response_structure():
    """
    Tests the case where the prediction object doesn't have the expected keys (e.g., 'url').
    """
    mock_bad_structure_prediction = MagicMock()
    # Simulate a prediction that doesn't contain 'url', 'gcsUri', or 'bytesBase64Encoded'
    mock_bad_structure_prediction.predictions = [{'unexpected_key': 'some_value'}]

    with patch('google.cloud.aiplatform', autospec=True) as mock_aiplatform:
        mock_endpoint_instance = MagicMock()
        mock_endpoint_instance.predict.return_value = mock_bad_structure_prediction
        mock_aiplatform.Endpoint.return_value = mock_endpoint_instance
        mock_aiplatform.init.return_value = None

        prompt = "A vintage car"
        result = await generate_image_with_imagen(prompt)
        assert result == "Error: Could not extract image from AI response."
