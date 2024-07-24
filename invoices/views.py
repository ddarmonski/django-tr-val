from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from azure.storage.blob import BlobServiceClient
from .llm_extraction import pdf_to_base64_images, call_openai_api
import uuid
import logging
import os
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

logger = logging.getLogger(__name__)

def welcome(request):
    return render(request, 'welcome.html')

def upload(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('invoices')
        errors = []
        extracted_data = []

        # Initialize Azure Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_name = 'invoices'
        container_client = blob_service_client.get_container_client(container_name)

        for uploaded_file in uploaded_files:
            # Validate the file (for simplicity, we just check the extension here)
            if not uploaded_file.name.endswith('.pdf'):
                errors.append(f"File {uploaded_file.name} is not a valid PDF file.")
                continue

            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"

            # Upload the file to Azure Blob Storage
            try:
                blob_client = container_client.get_blob_client(unique_filename)
                blob_client.upload_blob(uploaded_file, overwrite=True)
                logger.info(f"Uploaded {uploaded_file.name} to Azure Blob Storage as {unique_filename}")
            except Exception as e:
                errors.append(f"Could not upload {uploaded_file.name} to Azure Blob Storage: {str(e)}")
                continue

            # Convert PDF to base64 images
            try:
                # Read the file directly from Azure Blob Storage
                pdf_content = blob_client.download_blob().readall()
                #print(pdf_content)
                base64_images = pdf_to_base64_images(pdf_content)
                #print(base64_images)
                logger.info(f"Converted {uploaded_file.name} to base64 images")
            except Exception as e:
                errors.append(f"Could not convert {uploaded_file.name} to image: {str(e)}")
                continue

            # Call the OpenAI API for each image and aggregate results
            for base64_image in base64_images:
                try:
                    print("calling the openai_api: ", base64_image)
                    df = call_openai_api(base64_image)
                    logger.info(f"Received data from OpenAI API for {uploaded_file.name}")
                    extracted_data.append(df.to_dict(orient='records'))
                except Exception as e:
                    errors.append(f"Error processing {uploaded_file.name}: {str(e)}")
                    break

        logger.info(f"Extracted data: {extracted_data}")

        if errors:
            return JsonResponse({'errors': errors}, status=400)
        return JsonResponse({'extracted_data': extracted_data})
    return render(request, 'upload.html')

def dashboard(request):
    return render(request, 'dashboard.html')