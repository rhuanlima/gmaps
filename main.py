import json
import requests
import pandas as pd


# =====================================================================================
# = PARAMETROS
# =====================================================================================

g_key = "chave_google"  # Incluir a chave de API Google
radius = 1000
lojas = pd.read_csv(
    "data/parametros.csv", sep=";", encoding="utf-8", decimal=",", header=0
)
keywords = [
    "Estacionamento",
    "Parking",
    "Parque de Estacionamento",
    "Estacionamento com garagem",
    "CP",
    "Comboio",
    "Estação de Comboios",
    "Metro",
    "Estação de Metropolitano",
    "Ponto de ônibus",
    "Paragem de autocarro",
    "Terminal Rodoviário",
    "Continente",
    "Pingo doce",
    "Auchan",
    "Lidl",
    "Shopping",
    "Centro Comercial",
    "Mini preço",
    "Meu Super",
    "Farmacia",
    "Banco",
    "Lojas de produtos cosméticos",
    "Bombas de gasolina",
]


def findPlaces(bpsc, lat, lng, keyword, radius, df_gmaps, pagetoken=None, g_key=g_key):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&keyword={keyword}&key={g_key}{pagetoken}".format(
        lat=lat,
        lng=lng,
        radius=radius,
        keyword=keyword,
        g_key=g_key,
        pagetoken="&pagetoken=" + pagetoken if pagetoken else "",
    )
    print(url)
    response = requests.get(url)
    res = json.loads(response.text)
    for result in res["results"]:

        linha = [bpsc]
        try:
            linha.append(keyword)
        except linha.not_found:
            linha.append("None")
        try:
            linha.append(result["name"])
        except linha.not_found:
            linha.append("None")
        try:
            linha.append(result["geometry"]["location"]["lat"])
        except linha.not_found:
            linha.append("None")
        try:
            linha.append(result["geometry"]["location"]["lng"])
        except linha.not_found:
            linha.append("None")
        try:
            linha.append(result.get("rating", 0))
        except linha.not_found:
            linha.append("None")
        try:
            linha.append(result["user_ratings_total"])
        except linha.not_found:
            linha.append("None")
        try:
            linha.append(result["vicinity"])
        except linha.not_found:
            linha.append("None")
        try:
            linha.append(result["place_id"])
        except linha.not_found:
            linha.append("None")

        df_gmaps.loc[len(df_gmaps)] = linha
    pagetoken = res.get("next_page_token", None)
    print(pagetoken)
    return pagetoken


def get_place_details(
    g_key,
    place_id,
    fields=[
        "name",
        "formatted_address",
        "international_phone_number",
        "website",
        "rating",
        "review",
    ],
):
    endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"placeid": place_id, "key": g_key}
    res = requests.get(endpoint_url, params=params)
    place_details = json.loads(res.content)
    return place_details


def findDetails(lplace_id, df_details, df_review, g_key=g_key):
    for place in lplace_id:
        print(place)
        details = get_place_details(g_key, place)
        try:
            website = details["result"]["website"]
        except KeyError:
            website = ""

        try:
            name = details["result"]["name"]
        except KeyError:
            name = ""

        try:
            address = details["result"]["formatted_address"]
        except KeyError:
            address = ""

        try:
            phone_number = details["result"]["international_phone_number"]
        except KeyError:
            phone_number = ""

        try:
            reviews = details["result"]["reviews"]
        except KeyError:
            reviews = []
        print("===================PLACE===================")
        print("Name:", name)
        print("Website:", website)
        print("Address:", address)
        print("Phone Number", phone_number)
        print("==================REVIEWS==================")

        lista = [place, website, name, address, phone_number]
        df_details.loc[len(df_details)] = lista

        for review in reviews:
            author_name = review["author_name"]
            rating = review["rating"]
            text = review["text"]
            time = review["relative_time_description"]
            profile_photo = review["profile_photo_url"]
            print("Author Name:", author_name)
            print("Rating:", rating)
            print("Text:", text)
            print("Time:", time)
            print("Profile photo:", profile_photo)
            print("-----------------------------------------")
            lista = [place, author_name, rating, text, time, profile_photo]
            df_review.loc[len(df_review)] = lista
    return None


df_gmaps = pd.DataFrame(
    columns=[
        "bpsc",
        "keyword",
        "name",
        "lat",
        "lng",
        "rating",
        "user_ratings_total",
        "vicinity",
        "place_id",
    ]
)
df_details = pd.DataFrame(
    columns=["place_id", "website", "name", "address", "phone_number"]
)
df_review = pd.DataFrame(
    columns=["place_id", "author_name", "rating", "text", "time", "profile_photo"]
)


for index, loja in lojas.iterrows():
    pagetoken = None
    lat = loja["lat"]
    lng = loja["long"]
    bpsc = loja["bairro"]

    for keyword in keywords:
        while True:
            pagetoken = findPlaces(
                bpsc,
                lat,
                lng,
                keyword.replace(" ", "%20"),
                radius,
                df_gmaps,
                pagetoken,
                g_key,
            )
            if not pagetoken:
                break

df_gmaps.to_csv(
    "data/out_gmaps.csv", sep=";", decimal=",", index=False, encoding="UTF-8"
)
