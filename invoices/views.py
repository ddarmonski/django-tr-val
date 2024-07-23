from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from .llm_extraction import pdf_to_base64_images, call_openai_api

def welcome(request):
    return render(request, 'welcome.html')

def upload(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('invoices')
        errors = []
        extracted_data = []
        for uploaded_file in uploaded_files:
            # Validate the file (for simplicity, we just check the extension here)
            if not uploaded_file.name.endswith('.pdf'):
                errors.append(f"File {uploaded_file.name} is not a valid PDF file.")
                continue

            # Save the file
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)

            # Convert PDF to base64 images
            try:
                base64_images = pdf_to_base64_images(fs.path(filename))
            except Exception as e:
                errors.append(f"Could not convert {uploaded_file.name} to image: {str(e)}")
                continue

            # Call the OpenAI API for each image and aggregate results
            for base64_image in base64_images:
                try:
                    df = call_openai_api(base64_image)
                    print(df)  # Print the dataframe to the terminal
                    extracted_data.append(df.to_dict(orient='records'))
                except Exception as e:
                    errors.append(f"Error processing {uploaded_file.name}: {str(e)}")
                    break

        print('Extracted data:', extracted_data)  # Add this line

        if errors:
            return JsonResponse({'errors': errors}, status=400)
        return JsonResponse({'extracted_data': extracted_data})
    return render(request, 'upload.html')

def dashboard(request):
    return render(request, 'dashboard.html')