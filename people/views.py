import os, tempfile
import pandas as pd
from django.db.models import Count, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from .models import Student, Staff, Employee
from .serializers import StudentSerializer, StaffSerializer, EmployeeSerializer
from rest_framework.parsers import MultiPartParser
import pdfplumber

# Simple viewsets for CRUD
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

# ----- PDF upload and parsing -----
class PDFUploadView(APIView):
    parser_classes = [] 

    def post(self, request, format=None):
        f = request.FILES.get('file')
        if not f:
            return Response({'error': 'file required'}, status=400)

        # save temporary
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        for chunk in f.chunks():
            tmp.write(chunk)
        tmp.close()
        tmp_path = tmp.name

        try:
            # 1) Try extracting tables using pdfplumber
            import pdfplumber
            dfs = []
            with pdfplumber.open(tmp_path) as pdf:
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for t in tables:
                        if not t: 
                            continue
                        df = pd.DataFrame(t[1:], columns=t[0])
                        dfs.append(df)

            if dfs:
                combined = pd.concat(dfs, ignore_index=True)
                # normalize column names
                combined.columns = [str(c).strip().lower() for c in combined.columns]

                created = {'students':0,'staff':0,'employees':0}
                def safe_int(x):
                    try:
                        return int(float(x))
                    except:
                        return None

                for _, row in combined.iterrows():
                    # try to infer fields
                    name = row.get('name') or row.get('full name') or row.get('student name')
                    role = (row.get('role') or '').lower() if 'role' in row else ''
                    dept = row.get('department') or row.get('dept') or ''
                    age = safe_int(row.get('age')) if 'age' in row else None

                    if 'student' in role or 'roll' in combined.columns:
                        Student.objects.create(name=name or 'Unknown', age=age, department=dept)
                        created['students'] += 1
                    elif 'staff' in role:
                        Staff.objects.create(name=name or 'Unknown', age=age, department=dept)
                        created['staff'] += 1
                    else:
                        # fallback - create Employee
                        Employee.objects.create(name=name or 'Unknown', age=age, department=dept)
                        created['employees'] += 1

                return Response({'ok': True, 'created': created})

            # 2) If no tables found, try text extraction (pdfplumber) and simple parsing
            text_accum = []
            with pdfplumber.open(tmp_path) as pdf:
                for p in pdf.pages:
                    text_accum.append(p.extract_text() or '')
            text = '\n'.join(text_accum)
            # Example: very naive parsing — real PDFs need custom regex logic
            # We'll simply return the extracted text so frontend/dev can inspect it
            return Response({'ok': True, 'text_preview': text[:400]})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        finally:
            try:
                os.remove(tmp_path)
            except:
                pass

# ----- Stats endpoint for charts -----
@api_view(['GET'])
def stats_view(request):
    # students by department
    students = list(Student.objects.values('department').annotate(count=Count('id')).order_by('-count'))
    staff = list(Staff.objects.values('department').annotate(count=Count('id')).order_by('-count'))
    employees = list(Employee.objects.values('department').annotate(count=Count('id')).order_by('-count'))

    overall = {
        'total_students': Student.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_employees': Employee.objects.count(),
        'avg_employee_salary': Employee.objects.aggregate(avg=Avg('salary'))['avg'] or 0
    }
    return Response({
        'students_by_dept': students,
        'staff_by_dept': staff,
        'employees_by_dept': employees,
        'overall': overall
    })

class UploadPDFView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES['file']
        data_list = []

        # Example: extract text (you can extend for tables)
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                data_list.append(text)

        return Response({
            "status": "success",
            "parsed_data": data_list
        })


@api_view(['POST'])
def upload_pdf(request):
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({'error': 'No file uploaded'}, status=400)

    # Save file or process PDF
    with open(f'media/{uploaded_file.name}', 'wb+') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    return Response({'filename': uploaded_file.name, 'status': 'success'})