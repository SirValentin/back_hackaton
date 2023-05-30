import json
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from decouple import config
import docx2txt
import PyPDF2
import requests
import openai

api_key_openai = config("API_KEY_OPENAI")
openai.api_key = api_key_openai

api_key_infojobs = config("API_KEY_INFOJOBS")


# Create your views here.
class InfojobsViewSet(ModelViewSet):
    @action(detail=False, methods=["post"])
    def get_offer_list(self, request):
        page = request.data["page"]
        category = request.data["category"]
        endpoint = "https://api.infojobs.net/api/9/offer?page=" + str(page)
        if category:
            endpoint += "&category=" + category
        response = requests.get(
            endpoint,
            headers={"Authorization": api_key_infojobs},
        )
        data = response.json()
        return Response(data)

    @action(detail=False, methods=["post"])
    def get_offer_detail(self, request):
        offer_id = request.data["offer_id"]
        response = requests.get(
            "https://api.infojobs.net/api/7/offer/" + offer_id,
            headers={"Authorization": api_key_infojobs},
        )
        data = response.json()
        return Response(data)

    @action(detail=True, methods=["post"])
    def extract_content(self, request):
        file = request.FILES.get("file")
        offer = request.POST.get("offer")

        file_extension = file.name.split(".")[-1]

        if file_extension == "pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()

        elif file_extension in ["doc", "docx"]:
            content = docx2txt.process(file)

        else:
            return JsonResponse({"error": "Formato de archivo no compatible."})

        prompt = f"Eres un experto en recursos humanos y en reclutamiento y seleccion de personal, \
            te entregare un texto delimitado por tres asteriscos que corresponde a un curriculum de un postulante,\
            y un texto delimitado por tres comillas simples que corresponde a la descripcion de un empleo al que el postulante quiere aplicar.\
            Solamente genera un JSON como respuesta con las siguientes keys y su tipo: \
            porcentaje_compatibilidad tipo numero, debilidades tipo lista, fortalezas tipo lista , sugerencias tipo lista.\
            las keys deben estar delimitadas con doble comilla.\
            Entregar siempre un valor numerico para la key porcentaje_compatibilidad, analizar que tan compatible es el curriculum del postulante con la oferta de empleo \
            considerando la coherencia del curriculum del postulante con la oferta de empleo \
            Agregar en las fortalezas las habilidades o experiencias del postulante que estan descritas en su curriculum y tambien en la oferta de empleo \
            , no agregar a las fortalezas las habilidades o experiencias del postulante que no \
            sean de la misma area que la oferta de empleo.\
            Agregar a las debilidades las habilidades o experiencias del postulante que no estan descritas en su curriculum.\
            ***{content}*** \
            '''{offer}'''"
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])

        return JsonResponse({"response": json.loads(response.choices[0].message["content"])})
