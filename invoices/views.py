from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

def welcome(request):
    return render(request, 'welcome.html')

def upload(request):
    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('invoices')
        errors = []
        for uploaded_file in uploaded_files:
            # Validate the file (for simplicity, we just check the extension here)
            if not uploaded_file.name.endswith('.pdf'):
                errors.append(f"File {uploaded_file.name} is not a valid PDF file.")
                continue

            # Save the file
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            # Perform further validation (like checking contents of the file)
            # This is where you'd implement your custom validation logic
            
        if errors:
            return render(request, 'upload.html', {'errors': errors})
        return HttpResponse("Files uploaded successfully")
    return render(request, 'upload.html')

def dashboard(request):
    return render(request, 'dashboard.html')
